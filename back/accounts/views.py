from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

import jwt
import json
import logging
from datetime import datetime, timedelta
from uuid import uuid4

from .models import CustomUser, UserProfile, Role
from .serializers import (
    UserSerializer, UserDetailSerializer, UserCreateSerializer, 
    UserUpdateSerializer, ProfileUpdateSerializer, VerificationSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    RoleAssignmentSerializer, RoleSerializer
)
from .utils import (
    validate_password_strength, normalize_email, send_verification_email,
    send_password_reset_email, send_welcome_email, get_client_ip,
    record_login, assign_role, get_users_by_role, check_user_permission
)

logger = logging.getLogger(__name__)

# Helper functions
def get_tokens_for_user(user):
    """
    Generate JWT tokens for a user
    """
    refresh = RefreshToken.for_user(user)
    
    # Add custom claims to the token
    refresh['email'] = user.email
    refresh['name'] = user.get_full_name()
    
    # Add role information if available
    try:
        if hasattr(user, 'profile') and user.profile.role:
            refresh['role'] = user.profile.role.name
            refresh['role_display'] = user.profile.role.get_name_display()
    except UserProfile.DoesNotExist:
        pass
    
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def jwt_response_handler(token, user=None, request=None):
    """
    Returns the response data for both the refresh and access token.
    """
    return {
        'user': UserDetailSerializer(user, context={'request': request}).data,
        'token': token
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user
    """
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        try:
            with transaction.atomic():
                # Create user and profile
                user = serializer.save()
                
                # Send verification email
                send_verification_email(user, request)
                
                # Return user data without tokens (user needs to verify email first)
                return Response({
                    'success': True,
                    'message': 'User registered successfully. Please check your email for verification instructions.',
                    'user': UserSerializer(user).data
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            logger.error(f"Error in user registration: {str(e)}")
            return Response({
                'success': False,
                'message': 'An error occurred during registration.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({
        'success': False,
        'message': 'Invalid registration data.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    """
    Verify user email with verification code
    """
    serializer = VerificationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Mark email as verified and create default profile
        user.verify_email()
        
        # Generate tokens for verified user
        tokens = get_tokens_for_user(user)
        
        # Send welcome email
        send_welcome_email(user, request)
        
        return Response({
            'success': True,
            'message': 'Email verified successfully.',
            'tokens': tokens,
            'user': UserDetailSerializer(user).data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'message': 'Email verification failed.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification(request):
    """
    Resend verification email
    """
    email = request.data.get('email', '').lower().strip()
    
    if not email:
        return Response({
            'success': False,
            'message': 'Email is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = CustomUser.objects.get(email=email)
        
        if user.is_verified:
            return Response({
                'success': False,
                'message': 'Email is already verified.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate new verification code and send email
        send_verification_email(user, request)
        
        return Response({
            'success': True,
            'message': 'Verification email sent successfully.'
        }, status=status.HTTP_200_OK)
        
    except CustomUser.DoesNotExist:
        return Response({
            'success': False,
            'message': 'No account found with this email address.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        logger.error(f"Error resending verification email: {str(e)}")
        return Response({
            'success': False,
            'message': 'An error occurred while sending verification email.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Login user and generate JWT token
    """
    email = request.data.get('email', '').lower().strip()
    password = request.data.get('password', '')
    
    if not email or not password:
        return Response({
            'success': False,
            'message': 'Email and password are required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get user by email
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            record_login(None, False, request)
            return Response({
                'success': False,
                'message': 'Invalid email or password.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if account is locked
        if user.is_account_locked():
            lock_time_remaining = (user.account_locked_until - timezone.now()).total_seconds() // 60
            return Response({
                'success': False,
                'message': f'Account is temporarily locked due to multiple failed login attempts. Try again in {int(lock_time_remaining)} minutes.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if account is active
        if not user.is_active:
            record_login(user, False, request)
            return Response({
                'success': False,
                'message': 'Account is inactive or has been deactivated.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if email is verified
        if not user.is_verified:
            record_login(user, False, request)
            return Response({
                'success': False,
                'message': 'Email is not verified. Please check your email for verification instructions.',
                'unverified': True
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Authenticate user
        authenticated_user = authenticate(email=email, password=password)
        
        if authenticated_user is None:
            record_login(user, False, request)
            return Response({
                'success': False,
                'message': 'Invalid email or password.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Record successful login and update user's last_login
        record_login(user, True, request)
        
        # Get user profile data
        user_profile = authenticated_user.get_profile()
        
        # Generate tokens
        tokens = get_tokens_for_user(authenticated_user)
        
        return Response({
            'success': True,
            'message': 'Login successful.',
            'tokens': tokens,
            'user': UserDetailSerializer(authenticated_user).data
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error in user login: {str(e)}")
        return Response({
            'success': False,
            'message': 'An error occurred during login.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """
    Refresh JWT token
    """
    refresh_token = request.data.get('refresh')
    
    if not refresh_token:
        return Response({
            'success': False,
            'message': 'Refresh token is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        refresh = RefreshToken(refresh_token)
        
        # Create new tokens
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        
        # Get user from token
        user_id = refresh.payload.get('user_id')
        try:
            user = CustomUser.objects.get(id=user_id)
            
            # Update last activity of user
            if hasattr(user, 'profile'):
                user.profile.update_last_active()
                
            return Response({
                'success': True,
                'message': 'Token refreshed successfully.',
                'tokens': tokens,
                'user': UserDetailSerializer(user).data
            }, status=status.HTTP_200_OK)
            
        except CustomUser.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
    except TokenError as e:
        return Response({
            'success': False,
            'message': 'Invalid or expired refresh token.',
            'error': str(e)
        }, status=status.HTTP_401_UNAUTHORIZED)
        
    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}")
        return Response({
            'success': False,
            'message': 'An error occurred while refreshing token.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def logout_user(request):
    """
    Logout user by blacklisting refresh token
    """
    refresh_token = request.data.get('refresh')
    
    if not refresh_token:
        return Response({
            'success': False,
            'message': 'Refresh token is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Blacklist the token to prevent reuse
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        return Response({
            'success': True,
            'message': 'Logged out successfully.'
        }, status=status.HTTP_200_OK)
        
    except TokenError as e:
        return Response({
            'success': False,
            'message': 'Invalid token.',
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Error in user logout: {str(e)}")
        return Response({
            'success': False,
            'message': 'An error occurred during logout.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    """
    Request password reset by email
    """
    serializer = PasswordResetRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        try:
            user = CustomUser.objects.get(email=email)
            
            # Send password reset email
            send_password_reset_email(user, request)
            
            return Response({
                'success': True,
                'message': 'Password reset email sent successfully. Please check your email for instructions.'
            }, status=status.HTTP_200_OK)
            
        except CustomUser.DoesNotExist:
            # Return success even if user doesn't exist for security reasons
            return Response({
                'success': True,
                'message': 'If an account with this email exists, a password reset email has been sent.'
            }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'message': 'Invalid email.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_password_reset(request):
    """
    Confirm password reset with code and set new password
    """
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        new_password = serializer.validated_data['new_password']
        
        # Set new password
        user.set_password(new_password)
        
        # Clear reset code
        user.reset_code = ""
        user.reset_code_created = None
        
        # Reset failed login attempts
        user.failed_login_attempts = 0
        user.last_failed_login = None
        user.account_locked_until = None
        
        user.save()
        
        # Generate tokens for the user
        tokens = get_tokens_for_user(user)
        
        return Response({
            'success': True,
            'message': 'Password reset successful.',
            'tokens': tokens,
            'user': UserDetailSerializer(user).data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'message': 'Password reset failed.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    Get user profile data
    """
    user = request.user
    
    try:
        # Update last active timestamp
        if hasattr(user, 'profile'):
            user.profile.update_last_active()
            
        return Response({
            'success': True,
            'user': UserDetailSerializer(user).data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        return Response({
            'success': False,
            'message': 'An error occurred while retrieving user profile.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """
    Update user profile data
    """
    user = request.user
    
    # User data and profile data are separate serializers
    user_data = {k: v for k, v in request.data.items() if k in ['first_name', 'last_name', 'phone_number', 'date_of_birth', 'current_password', 'new_password', 'confirm_new_password']}
    profile_data = {k: v for k, v in request.data.items() if k in ['bio', 'avatar', 'location', 'timezone', 'preferences']}
    
    try:
        # Update user data if provided
        if user_data:
            user_serializer = UserUpdateSerializer(user, data=user_data, partial=True)
            if user_serializer.is_valid():
                user = user_serializer.save()
            else:
                return Response({
                    'success': False,
                    'message': 'Invalid user data.',
                    'errors': user_serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update profile data if provided
        if profile_data and hasattr(user, 'profile'):
            profile_serializer = ProfileUpdateSerializer(user.profile, data=profile_data, partial=True)
            if profile_serializer.is_valid():
                profile_serializer.save()
            else:
                return Response({
                    'success': False,
                    'message': 'Invalid profile data.',
                    'errors': profile_serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Return updated user data
        return Response({
            'success': True,
            'message': 'Profile updated successfully.',
            'user': UserDetailSerializer(user).data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        return Response({
            'success': False,
            'message': 'An error occurred while updating profile.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change user password (when already logged in)
    """
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')
    
    if not current_password or not new_password or not confirm_password:
        return Response({
            'success': False,
            'message': 'Current password, new password, and confirm password are required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if new password and confirm password match
    if new_password != confirm_password:
        return Response({
            'success': False,
            'message': 'New passwords do not match.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate password strength
    is_valid, message = validate_password_strength(new_password)
    if not is_valid:
        return Response({
            'success': False,
            'message': message
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if current password is correct
    user = request.user
    if not user.check_password(current_password):
        return Response({
            'success': False,
            'message': 'Current password is incorrect.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Set new password
        user.set_password(new_password)
        user.save(update_fields=['password'])
        
        # Generate new tokens
        tokens = get_tokens_for_user(user)
        
        return Response({
            'success': True,
            'message': 'Password changed successfully.',
            'tokens': tokens
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        return Response({
            'success': False,
            'message': 'An error occurred while changing password.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def deactivate_account(request):
    """
    Deactivate user account
    """
    password = request.data.get('password')
    
    if not password:
        return Response({
            'success': False,
            'message': 'Password is required to deactivate account.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if password is correct
    user = request.user
    if not user.check_password(password):
        return Response({
            'success': False,
            'message': 'Password is incorrect.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Deactivate account
        user.is_active = False
        user.save(update_fields=['is_active'])
        
        # Blacklist any refresh tokens
        refresh_token = request.data.get('refresh')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                pass
        
        return Response({
            'success': True,
            'message': 'Account deactivated successfully.'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error deactivating account: {str(e)}")
        return Response({
            'success': False,
            'message': 'An error occurred while deactivating account.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Role management views (Admin only)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def get_roles(request):
    """
    Get all roles (admin only)
    """
    roles = Role.objects.all()
    serializer = RoleSerializer(roles, many=True)
    
    return Response({
        'success': True,
        'roles': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def assign_user_role(request):
    """
    Assign role to user (admin only)
    """
    serializer = RoleAssignmentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        
        # Get the updated user profile
        user = serializer.validated_data['user']
        
        return Response({
            'success': True,
            'message': f"Role assigned successfully: {serializer.validated_data['role'].get_name_display()}",
            'user': UserDetailSerializer(user).data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'message': 'Role assignment failed.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# User management views (Admin only)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def get_users(request):
    """
    Get all users (admin only)
    """
    # Get query parameters
    role = request.query_params.get('role')
    is_active = request.query_params.get('is_active')
    is_verified = request.query_params.get('is_verified')
    search = request.query_params.get('search')
    
    # Base queryset
    users = CustomUser.objects.all().select_related('profile__role')
    
    # Apply filters
    if role:
        users = users.filter(profile__role__name=role)
    
    if is_active is not None:
        is_active = is_active.lower() == 'true'
        users = users.filter(is_active=is_active)
    
    if is_verified is not None:
        is_verified = is_verified.lower() == 'true'
        users = users.filter(is_verified=is_verified)
    
    if search:
        users = users.filter(
            email__icontains=search
        ) | users.filter(
            first_name__icontains=search
        ) | users.filter(
            last_name__icontains=search
        ) | users.filter(
            phone_number__icontains=search
        )
    
    # Serialize and return data
    serializer = UserDetailSerializer(users, many=True)
    
    return Response({
        'success': True,
        'count': users.count(),
        'users': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def get_user_detail(request, user_id):
    """
    Get user details (admin only)
    """
    try:
        user = CustomUser.objects.get(id=user_id)
        serializer = UserDetailSerializer(user)
        
        return Response({
            'success': True,
            'user': serializer.data
        }, status=status.HTTP_200_OK)
        
    except CustomUser.DoesNotExist:
        return Response({
            'success': False,
            'message': 'User not found.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def update_user(request, user_id):
    """
    Update user details (admin only)
    """
    try:
        user = CustomUser.objects.get(id=user_id)
        
        # User data
        user_data = {k: v for k, v in request.data.items() if k in ['first_name', 'last_name', 'phone_number', 'date_of_birth', 'is_active', 'is_verified']}
        
        # Handle role assignment
        role_id = request.data.get('role_id')
        
        try:
            # Update user data
            if user_data:
                for key, value in user_data.items():
                    setattr(user, key, value)
                user.save()
            
            # Update role if provided
            if role_id:
                try:
                    role = Role.objects.get(id=role_id)
                    profile, created = UserProfile.objects.get_or_create(user=user)
                    profile.role = role
                    profile.save()
                except Role.DoesNotExist:
                    return Response({
                        'success': False,
                        'message': 'Role not found.'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            return Response({
                'success': True,
                'message': 'User updated successfully.',
                'user': UserDetailSerializer(user).data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            return Response({
                'success': False,
                'message': f'An error occurred while updating user: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except CustomUser.DoesNotExist:
        return Response({
            'success': False,
            'message': 'User not found.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def create_user(request):
    """
    Create a new user (admin only)
    """
    # Prepare data
    data = request.data.copy()
    
    # Add confirm_password if not provided
    if 'password' in data and 'confirm_password' not in data:
        data['confirm_password'] = data['password']
    
    serializer = UserCreateSerializer(data=data)
    if serializer.is_valid():
        try:
            # Create user
            user = serializer.save()
            
            # If admin wants user to be verified immediately
            verify_now = request.data.get('verify_now', False)
            if verify_now:
                user.verify_email()
            
            return Response({
                'success': True,
                'message': 'User created successfully.',
                'user': UserDetailSerializer(user).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return Response({
                'success': False,
                'message': f'An error occurred while creating user: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({
        'success': False,
        'message': 'Invalid user data.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def delete_user(request, user_id):
    """
    Delete a user (admin only)
    """
    try:
        user = CustomUser.objects.get(id=user_id)
        
        # Check if trying to delete self
        if request.user.id == user.id:
            return Response({
                'success': False,
                'message': 'You cannot delete your own account from this endpoint.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Delete user
        email = user.email
        user.delete()
        
        return Response({
            'success': True,
            'message': f'User {email} deleted successfully.'
        }, status=status.HTTP_200_OK)
        
    except CustomUser.DoesNotExist:
        return Response({
            'success': False,
            'message': 'User not found.'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        return Response({
            'success': False,
            'message': f'An error occurred while deleting user: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# JWT token validation endpoint
@api_view(['POST'])
@permission_classes([AllowAny])
def validate_token(request):
    """
    Validate JWT token and return user data
    """
    token = request.data.get('token')
    
    if not token:
        return Response({
            'success': False,
            'message': 'Token is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Decode token
        payload = jwt.decode(
            token, 
            settings.SIMPLE_JWT['SIGNING_KEY'],
            algorithms=[settings.SIMPLE_JWT['ALGORITHM']]
        )
        
        # Get user from token
        user_id = payload.get('user_id')
        user = CustomUser.objects.get(id=user_id)
        
        # Check if user is active
        if not user.is_active:
            return Response({
                'success': False,
                'message': 'User is inactive.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Update last active timestamp
        if hasattr(user, 'profile'):
            user.profile.update_last_active()
        
        return Response({
            'success': True,
            'message': 'Token is valid.',
            'user': UserDetailSerializer(user).data
        }, status=status.HTTP_200_OK)
        
    except jwt.ExpiredSignatureError:
        return Response({
            'success': False,
            'message': 'Token has expired.'
        }, status=status.HTTP_401_UNAUTHORIZED)
        
    except jwt.InvalidTokenError:
        return Response({
            'success': False,
            'message': 'Invalid token.'
        }, status=status.HTTP_401_UNAUTHORIZED)
        
    except CustomUser.DoesNotExist:
        return Response({
            'success': False,
            'message': 'User not found.'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        logger.error(f"Error validating token: {str(e)}")
        return Response({
            'success': False,
            'message': 'An error occurred while validating token.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Check permissions endpoint
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def check_permission(request):
    """
    Check if the user has a specific permission
    """
    permission_name = request.data.get('permission')
    
    if not permission_name:
        return Response({
            'success': False,
            'message': 'Permission name is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if user has the permission
    has_permission = check_user_permission(request.user, permission_name)
    
    return Response({
        'success': True,
        'has_permission': has_permission
    }, status=status.HTTP_200_OK)