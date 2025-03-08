from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Permission, Group
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db import transaction
import random
import uuid
from datetime import timedelta


class Role(models.Model):
    """
    Defines user roles and associated permissions in the platform
    """
    ADMIN = 'admin'
    CLIENT = 'client'
    STAFF = 'staff'
    
    ROLE_CHOICES = [
        (ADMIN, _('Administrator')),
        (CLIENT, _('Client')),
        (STAFF, _('Staff')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=50, 
        choices=ROLE_CHOICES, 
        unique=True,
        help_text=_('Role name determines user permissions and access levels')
    )
    description = models.TextField(
        blank=True,
        help_text=_('Detailed description of role responsibilities')
    )
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('permissions'),
        blank=True,
        help_text=_('Specific permissions granted to this role'),
        related_name='platform_roles'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(
        default=True,
        help_text=_('Designates whether this role is active. Unselect instead of deleting roles.')
    )

    class Meta:
        verbose_name = _('role')
        verbose_name_plural = _('roles')
        ordering = ['name']

    def __str__(self):
        return self.get_name_display()

    @property
    def default_permissions(self):
        """
        Define default permissions for each role
        """
        permissions_map = {
            self.ADMIN: {
                'can_manage_users': True,
                'can_manage_roles': True,
                'can_manage_content': True,
                'can_manage_payments': True,
                'can_view_analytics': True,
                'can_manage_system': True,
                'can_manage_projects': True,
            },
            
            self.CLIENT: {
                'can_view_own_projects': True,
                'can_request_services': True,
                'can_view_own_reports': True,
                'can_submit_applications': True,
            },
            
            self.STAFF: {
                'can_moderate_content': True,
                'can_manage_projects': True,
                'can_handle_support': True,
                'can_view_reports': True,
                'can_assist_users': True,
            }
        }
        return permissions_map.get(self.name, {})

    def clean(self):
        """
        Custom validation for Role model
        """
        if self.name not in dict(self.ROLE_CHOICES):
            raise ValidationError({'name': _('Invalid role name selected.')})
            
    @classmethod
    def get_default_client_role(cls):
        """
        Get or create the default client role
        """
        role, created = cls.objects.get_or_create(
            name=cls.CLIENT,
            defaults={
                'description': _('Default client role with standard permissions')
            }
        )
        return role


class CustomUserManager(BaseUserManager):
    """
    Custom user manager for email-based authentication
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('Email address is required'))
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
            
        user.full_clean()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)
        
    def get_clients(self):
        """
        Return all users with client role
        """
        return self.filter(profile__role__name=Role.CLIENT, is_active=True)
        
    def get_staff(self):
        """
        Return all users with staff role
        """
        return self.filter(profile__role__name=Role.STAFF, is_active=True)
        
    def get_administrators(self):
        """
        Return all users with admin role
        """
        return self.filter(profile__role__name=Role.ADMIN, is_active=True)


class UserProfile(models.Model):
    """
    Extended user profile with additional fields
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        'CustomUser', 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    role = models.ForeignKey(
        Role, 
        on_delete=models.SET_NULL, 
        null=True,
        help_text=_('User role determines permissions and access levels')
    )
    bio = models.TextField(
        blank=True,
        help_text=_('User biography or introduction')
    )
    avatar = models.ImageField(
        upload_to='avatars/', 
        null=True, 
        blank=True,
        help_text=_('Profile picture')
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('User\'s general location for matching with nearby clients')
    )
    timezone = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('User\'s timezone for scheduling purposes')
    )
    preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text=_('User preferences and settings')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(
        null=True, 
        blank=True,
        help_text=_('Last activity timestamp')
    )

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()}'s Profile"

    def has_permission(self, permission_name):
        """
        Check if the user has a specific permission based on their role
        """
        if not self.role:
            return False
        return self.role.default_permissions.get(permission_name, False)

    def update_last_active(self):
        """
        Update the last active timestamp
        """
        self.last_active = timezone.now()
        self.save(update_fields=['last_active'])
        
    def is_client(self):
        """
        Check if user has client role
        """
        return self.role and self.role.name == Role.CLIENT
        
    def is_staff_member(self):
        """
        Check if user has staff role
        """
        return self.role and self.role.name == Role.STAFF
        
    def is_administrator(self):
        """
        Check if user has admin role
        """
        return self.role and self.role.name == Role.ADMIN


class CustomUser(AbstractUser):
    """
    Custom user model with email-based authentication
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None  # Remove username field
    email = models.EmailField(
        _('email address'), 
        unique=True,
        error_messages={
            'unique': _('A user with this email already exists.'),
        },
        help_text=_('Required. Your email address will be used for authentication.')
    )
    first_name = models.CharField(
        _('first name'), 
        max_length=30,
        help_text=_('Required. Your first name.')
    )
    last_name = models.CharField(
        _('last name'), 
        max_length=30,
        help_text=_('Required. Your last name.')
    )
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_('Phone number must be entered in the format: "+999999999". Up to 15 digits allowed.')
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        help_text=_('Optional. Phone number for contact purposes.')
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        help_text=_('Optional. Date of birth for age verification.')
    )
    is_verified = models.BooleanField(
        default=False,
        help_text=_('Indicates if the user\'s email has been verified.')
    )
    
    # Authentication fields
    verification_token = models.CharField(max_length=100, blank=True)
    verification_token_created = models.DateTimeField(null=True, blank=True)
    verification_code = models.CharField(max_length=6, blank=True)
    verification_code_created = models.DateTimeField(null=True, blank=True)
    reset_code = models.CharField(max_length=6, blank=True)
    reset_code_created = models.DateTimeField(null=True, blank=True)
    
    # Add related_names to fix clashes
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
        related_name='custom_users'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='custom_users'
    )
    
    # Activity tracking
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    last_failed_login = models.DateTimeField(null=True, blank=True)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']

    def __str__(self):
        return self.email

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def generate_verification_code(self):
        """
        Generate a random 6-digit verification code
        """
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        self.verification_code = code
        self.verification_code_created = timezone.now()
        
        # Expire any existing reset code if it exists
        if self.reset_code and not self.is_reset_code_expired():
            self.reset_code = ""
            self.reset_code_created = None
        
        self.save(update_fields=['verification_code', 'verification_code_created', 
                                'reset_code', 'reset_code_created'])
        return code

    def generate_reset_code(self):
        """
        Generate a random 6-digit reset code
        """
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        self.reset_code = code
        self.reset_code_created = timezone.now()
        
        # Clear verification code if exists
        self.verification_code = ""
        self.verification_code_created = None
        
        self.save(update_fields=['reset_code', 'reset_code_created',
                                'verification_code', 'verification_code_created'])
        return code

    def is_verification_code_valid(self):
        """
        Check if verification code is valid and not expired
        """
        if not self.verification_code_created:
            return False
        return timezone.now() - self.verification_code_created <= timedelta(minutes=15)

    def is_reset_code_valid(self):
        """
        Check if reset code is valid and not expired
        """
        if not self.reset_code_created:
            return False
        return timezone.now() - self.reset_code_created <= timedelta(minutes=15)

    def is_reset_code_expired(self):
        """
        Check if the reset code has expired
        """
        if not self.reset_code_created:
            return True
        return timezone.now() - self.reset_code_created > timedelta(minutes=15)

    def verify_email(self):
        """
        Verify user's email and set up their profile
        """
        with transaction.atomic():
            self.is_verified = True
            self.verification_code = ""
            self.verification_code_created = None
            self.verification_token = ""
            self.verification_token_created = None
            self.save(update_fields=['is_verified', 'verification_code', 
                                   'verification_code_created', 'verification_token',
                                   'verification_token_created'])
            
            # Create or update profile with appropriate role
            default_role = Role.get_default_client_role()
            UserProfile.objects.update_or_create(
                user=self,
                defaults={'role': default_role}
            )

    def record_login_attempt(self, success, ip_address=None):
        """
        Record login attempt and handle account locking
        """
        if success:
            self.failed_login_attempts = 0
            self.last_failed_login = None
            self.account_locked_until = None
            self.last_login_ip = ip_address
        else:
            self.failed_login_attempts += 1
            self.last_failed_login = timezone.now()
            
            # Lock account after 5 failed attempts
            if self.failed_login_attempts >= 5:
                self.account_locked_until = timezone.now() + timedelta(minutes=30)
        
        self.save(update_fields=['failed_login_attempts', 'last_failed_login',
                                'account_locked_until', 'last_login_ip'])

    def is_account_locked(self):
        """
        Check if account is temporarily locked due to failed login attempts
        """
        if not self.account_locked_until:
            return False
        return timezone.now() < self.account_locked_until
        
    def get_profile(self):
        """
        Get or create user profile
        """
        profile, created = UserProfile.objects.get_or_create(user=self)
        return profile
        
    def has_permission(self, permission_name):
        """
        Check if user has specific permission through their profile role
        """
        try:
            return self.profile.has_permission(permission_name)
        except UserProfile.DoesNotExist:
            return False
            
    def is_client(self):
        """
        Check if user has client role
        """
        try:
            return self.profile.is_client()
        except UserProfile.DoesNotExist:
            return False
            
    def is_staff_member(self):
        """
        Check if user has staff role
        """
        try:
            return self.profile.is_staff_member()
        except UserProfile.DoesNotExist:
            return False
            
    def is_administrator(self):
        """
        Check if user has admin role
        """
        try:
            return self.profile.is_administrator()
        except UserProfile.DoesNotExist:
            return False

    def clean(self):
        """
        Custom validation for CustomUser model
        """
        super().clean()
        self.email = self.email.lower().strip()
        
        if self.date_of_birth:
            age = (timezone.now().date() - self.date_of_birth).days / 365
            if age < 13:
                raise ValidationError(
                    {'date_of_birth': _('Users must be at least 13 years old.')}
                )