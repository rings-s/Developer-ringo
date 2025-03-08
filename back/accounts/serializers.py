from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from .models import Role, UserProfile, CustomUser


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role model"""
    name_display = serializers.CharField(source='get_name_display', read_only=True)
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'name_display', 'description', 
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    role_display = serializers.CharField(source='role.get_name_display', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'role', 'role_display', 'bio', 'avatar',
            'location', 'timezone', 'preferences', 'last_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'last_active']


class UserSerializer(serializers.ModelSerializer):
    """Basic serializer for CustomUser model"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'is_verified', 'date_joined'
        ]
        read_only_fields = ['date_joined', 'is_verified']
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for CustomUser with nested profile data"""
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'date_of_birth', 'is_verified',
            'date_joined', 'last_login', 'last_login_ip',
            'role', 'profile'
        ]
        read_only_fields = ['date_joined', 'last_login', 'last_login_ip', 'is_verified']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_role(self, obj):
        try:
            if hasattr(obj, 'profile') and obj.profile.role:
                return {
                    'id': str(obj.profile.role.id),
                    'name': obj.profile.role.name,
                    'display': obj.profile.role.get_name_display()
                }
            return None
        except UserProfile.DoesNotExist:
            return None


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new user with optional profile data"""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), required=False, write_only=True)
    bio = serializers.CharField(required=False, write_only=True)
    location = serializers.CharField(required=False, write_only=True)
    timezone = serializers.CharField(required=False, write_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'email', 'password', 'confirm_password', 'first_name', 'last_name',
            'phone_number', 'date_of_birth', 'role', 'bio', 'location', 'timezone'
        ]
    
    def validate(self, data):
        """
        Validate that passwords match and other validations
        """
        if data['password'] != data.pop('confirm_password'):
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
            
        # Email validation
        email = data.get('email', '').lower().strip()
        if CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists."})
            
        # Age validation if date of birth provided
        date_of_birth = data.get('date_of_birth')
        if date_of_birth:
            age = (timezone.now().date() - date_of_birth).days / 365
            if age < 13:
                raise serializers.ValidationError({"date_of_birth": "Users must be at least 13 years old."})
                
        return data
    
    def create(self, validated_data):
        """Create user and profile in a transaction"""
        # Extract profile fields
        role = validated_data.pop('role', None)
        bio = validated_data.pop('bio', '')
        location = validated_data.pop('location', '')
        timezone_str = validated_data.pop('timezone', '')
        
        # Get the password
        password = validated_data.pop('password')
        
        with transaction.atomic():
            # Create user
            user = CustomUser.objects.create_user(
                password=password,
                **validated_data
            )
            
            # Create or update profile
            profile_data = {}
            if role:
                profile_data['role'] = role
            if bio:
                profile_data['bio'] = bio
            if location:
                profile_data['location'] = location
            if timezone_str:
                profile_data['timezone'] = timezone_str
                
            if profile_data:
                UserProfile.objects.update_or_create(
                    user=user,
                    defaults=profile_data
                )
                
            return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user data"""
    current_password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})
    new_password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})
    confirm_new_password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})
    
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'phone_number', 'date_of_birth',
            'current_password', 'new_password', 'confirm_new_password'
        ]
    
    def validate(self, data):
        """
        Validate password change if requested
        """
        current_password = data.pop('current_password', None)
        new_password = data.pop('new_password', None)
        confirm_new_password = data.pop('confirm_new_password', None)
        
        # If changing password
        if new_password:
            if not current_password:
                raise serializers.ValidationError({"current_password": "Current password is required to set a new password."})
            
            if not self.instance.check_password(current_password):
                raise serializers.ValidationError({"current_password": "Current password is incorrect."})
            
            if new_password != confirm_new_password:
                raise serializers.ValidationError({"confirm_new_password": "New passwords do not match."})
            
            # Add password to validated data to set later
            data['_password'] = new_password
            
        # Age validation if date of birth provided
        date_of_birth = data.get('date_of_birth')
        if date_of_birth:
            age = (timezone.now().date() - date_of_birth).days / 365
            if age < 13:
                raise serializers.ValidationError({"date_of_birth": "Users must be at least 13 years old."})
                
        return data
    
    def update(self, instance, validated_data):
        """Update user with option to change password"""
        # Handle password change
        password = validated_data.pop('_password', None)
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        # Set new password if provided
        if password:
            instance.set_password(password)
            
        instance.save()
        return instance


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile data"""
    
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'location', 'timezone', 'preferences']
    
    def update(self, instance, validated_data):
        """Update profile fields"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        instance.save()
        return instance


class VerificationSerializer(serializers.Serializer):
    """Serializer for email verification"""
    verification_code = serializers.CharField(required=True, min_length=6, max_length=6)
    email = serializers.EmailField(required=True)
    
    def validate(self, data):
        """Validate verification code"""
        try:
            email = data['email'].lower().strip()
            user = CustomUser.objects.get(email=email)
            
            if user.is_verified:
                raise serializers.ValidationError({"email": "This account is already verified."})
                
            if not user.verification_code:
                raise serializers.ValidationError({"verification_code": "No verification code has been generated."})
                
            if not user.is_verification_code_valid():
                raise serializers.ValidationError({"verification_code": "Verification code has expired. Please request a new one."})
                
            if user.verification_code != data['verification_code']:
                raise serializers.ValidationError({"verification_code": "Invalid verification code."})
                
            data['user'] = user
            return data
            
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({"email": "No account found with this email address."})


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for requesting a password reset"""
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Check that the email exists"""
        email = value.lower().strip()
        if not CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError("No account found with this email address.")
        return email


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for confirming a password reset"""
    email = serializers.EmailField(required=True)
    reset_code = serializers.CharField(required=True, min_length=6, max_length=6)
    new_password = serializers.CharField(required=True, min_length=8)
    confirm_password = serializers.CharField(required=True, min_length=8)
    
    def validate(self, data):
        """Validate reset code and passwords"""
        try:
            email = data['email'].lower().strip()
            user = CustomUser.objects.get(email=email)
            
            if not user.reset_code:
                raise serializers.ValidationError({"reset_code": "No reset code has been generated."})
                
            if not user.is_reset_code_valid():
                raise serializers.ValidationError({"reset_code": "Reset code has expired. Please request a new one."})
                
            if user.reset_code != data['reset_code']:
                raise serializers.ValidationError({"reset_code": "Invalid reset code."})
                
            if data['new_password'] != data['confirm_password']:
                raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
                
            data['user'] = user
            return data
            
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({"email": "No account found with this email address."})
            

class RoleAssignmentSerializer(serializers.Serializer):
    """Serializer for assigning a role to a user"""
    user_id = serializers.UUIDField(required=True)
    role_id = serializers.UUIDField(required=True)
    
    def validate(self, data):
        """Validate user and role exist"""
        try:
            user = CustomUser.objects.get(id=data['user_id'])
            data['user'] = user
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({"user_id": "User not found."})
            
        try:
            role = Role.objects.get(id=data['role_id'])
            data['role'] = role
        except Role.DoesNotExist:
            raise serializers.ValidationError({"role_id": "Role not found."})
            
        return data
        
    def save(self):
        """Assign role to user profile"""
        user = self.validated_data['user']
        role = self.validated_data['role']
        
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.role = role
        profile.save()
        
        return profile