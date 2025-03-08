from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
import uuid
import re
import logging
from datetime import timedelta

from .models import CustomUser, UserProfile, Role

logger = logging.getLogger(__name__)


def validate_password_strength(password):
    """
    Validate that a password meets minimum strength requirements
    Returns (is_valid, message) tuple
    """
    # Check for minimum length
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "Password must include at least one lowercase letter."
    
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, "Password must include at least one uppercase letter."
    
    # Check for at least one digit
    if not re.search(r'\d', password):
        return False, "Password must include at least one number."
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must include at least one special character."
    
    return True, "Password meets strength requirements."


def normalize_email(email):
    """
    Normalize an email address by lowercasing and stripping whitespace
    """
    return email.lower().strip() if email else None


def is_valid_uuid(uuid_string):
    """
    Check if a string is a valid UUID
    """
    try:
        uuid_obj = uuid.UUID(uuid_string)
        return str(uuid_obj) == uuid_string.lower()
    except (ValueError, AttributeError):
        return False


def send_verification_email(user, request=None):
    """
    Send email verification code to a user
    Returns True if email was sent successfully
    """
    if not user or not user.email:
        return False
    
    # Generate verification code if needed
    if not user.verification_code or not user.is_verification_code_valid():
        user.generate_verification_code()
    
    try:
        # Get site domain
        if request:
            current_site = get_current_site(request)
            domain = current_site.domain
        else:
            domain = settings.SITE_DOMAIN if hasattr(settings, 'SITE_DOMAIN') else 'example.com'
        
        # Prepare email context
        context = {
            'user': user,
            'code': user.verification_code,
            'domain': domain,
            'site_name': settings.SITE_NAME if hasattr(settings, 'SITE_NAME') else 'Our Platform',
            'expiry_minutes': 15  # Code expires after 15 minutes
        }
        
        # Render email template
        html_message = render_to_string('accounts/email/verification_email.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=f"Verify your email for {settings.SITE_NAME if hasattr(settings, 'SITE_NAME') else 'Our Platform'}",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Verification email sent to {user.email}")
        return True
    
    except Exception as e:
        logger.error(f"Error sending verification email to {user.email}: {str(e)}")
        return False


def send_password_reset_email(user, request=None):
    """
    Send password reset code to a user
    Returns True if email was sent successfully
    """
    if not user or not user.email:
        return False
    
    # Generate reset code
    user.generate_reset_code()
    
    try:
        # Get site domain
        if request:
            current_site = get_current_site(request)
            domain = current_site.domain
        else:
            domain = settings.SITE_DOMAIN if hasattr(settings, 'SITE_DOMAIN') else 'example.com'
        
        # Prepare email context
        context = {
            'user': user,
            'code': user.reset_code,
            'domain': domain,
            'site_name': settings.SITE_NAME if hasattr(settings, 'SITE_NAME') else 'Our Platform',
            'expiry_minutes': 15  # Code expires after 15 minutes
        }
        
        # Render email template
        html_message = render_to_string('accounts/email/password_reset_email.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=f"Reset your password for {settings.SITE_NAME if hasattr(settings, 'SITE_NAME') else 'Our Platform'}",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Password reset email sent to {user.email}")
        return True
    
    except Exception as e:
        logger.error(f"Error sending password reset email to {user.email}: {str(e)}")
        return False


def send_welcome_email(user, request=None):
    """
    Send welcome email to a newly verified user
    Returns True if email was sent successfully
    """
    if not user or not user.email or not user.is_verified:
        return False
    
    try:
        # Get site domain
        if request:
            current_site = get_current_site(request)
            domain = current_site.domain
        else:
            domain = settings.SITE_DOMAIN if hasattr(settings, 'SITE_DOMAIN') else 'example.com'
        
        # Prepare email context
        context = {
            'user': user,
            'domain': domain,
            'site_name': settings.SITE_NAME if hasattr(settings, 'SITE_NAME') else 'Our Platform',
        }
        
        # Render email template
        html_message = render_to_string('accounts/email/welcome_email.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=f"Welcome to {settings.SITE_NAME if hasattr(settings, 'SITE_NAME') else 'Our Platform'}",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Welcome email sent to {user.email}")
        return True
    
    except Exception as e:
        logger.error(f"Error sending welcome email to {user.email}: {str(e)}")
        return False


def get_client_ip(request):
    """
    Get the client IP address from request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def record_login(user, success, request=None):
    """
    Record a login attempt and handle account locking
    """
    if not user:
        return
    
    ip_address = None
    if request:
        ip_address = get_client_ip(request)
    
    user.record_login_attempt(success=success, ip_address=ip_address)
    
    if success and hasattr(user, 'profile'):
        # Update last active timestamp
        try:
            profile = user.profile
            profile.update_last_active()
        except UserProfile.DoesNotExist:
            # Create profile if it doesn't exist
            UserProfile.objects.create(user=user, last_active=timezone.now())


def assign_role(user, role_name):
    """
    Assign a role to a user
    Returns the updated profile or None if failed
    """
    if not user:
        return None
    
    try:
        # Get or create the role
        try:
            role = Role.objects.get(name=role_name)
        except Role.DoesNotExist:
            logger.error(f"Role '{role_name}' does not exist")
            return None
        
        # Get or create the profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Assign the role
        profile.role = role
        profile.save(update_fields=['role'])
        
        logger.info(f"Assigned role '{role_name}' to user {user.email}")
        return profile
    
    except Exception as e:
        logger.error(f"Error assigning role '{role_name}' to user {user.email}: {str(e)}")
        return None


def get_users_by_role(role_name):
    """
    Get all users with a specific role
    """
    return CustomUser.objects.filter(
        profile__role__name=role_name,
        is_active=True
    ).select_related('profile')


def get_inactive_users(days=30):
    """
    Get users who haven't been active for a specified number of days
    """
    cutoff_date = timezone.now() - timedelta(days=days)
    return CustomUser.objects.filter(
        profile__last_active__lt=cutoff_date,
        is_active=True
    ).select_related('profile')


def create_user_with_profile(email, password, first_name, last_name, role_name=None, **extra_fields):
    """
    Create a new user with profile in a single transaction
    Returns (user, profile) tuple or (None, None) if failed
    """
    from django.db import transaction
    
    email = normalize_email(email)
    if not email:
        return None, None
    
    try:
        with transaction.atomic():
            # Create the user
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                **extra_fields
            )
            
            # Get the role if specified
            role = None
            if role_name:
                try:
                    role = Role.objects.get(name=role_name)
                except Role.DoesNotExist:
                    # Default to client role if specified role doesn't exist
                    role = Role.get_default_client_role()
            else:
                # Default to client role if no role specified
                role = Role.get_default_client_role()
            
            # Create the profile with the role
            profile = UserProfile.objects.create(
                user=user,
                role=role
            )
            
            logger.info(f"Created new user {email} with {role.get_name_display() if role else 'no'} role")
            return user, profile
    
    except Exception as e:
        logger.error(f"Error creating user {email}: {str(e)}")
        return None, None


def check_user_permission(user, permission_name):
    """
    Check if a user has a specific permission
    """
    if not user or not user.is_active:
        return False
    
    # Superusers have all permissions
    if user.is_superuser:
        return True
    
    # Check permission through profile role
    return user.has_permission(permission_name)