from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('register/', views.register_user, name='register'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
    path('login/', views.login_user, name='login'),
    path('refresh-token/', views.refresh_token, name='refresh_token'),
    path('logout/', views.logout_user, name='logout'),
    
    # Password reset
    path('request-password-reset/', views.request_password_reset, name='request_password_reset'),
    path('confirm-password-reset/', views.confirm_password_reset, name='confirm_password_reset'),
    
    # User profile
    path('profile/', views.get_user_profile, name='get_profile'),
    path('profile/update/', views.update_user_profile, name='update_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('deactivate-account/', views.deactivate_account, name='deactivate_account'),
    
    # Role management (admin only)
    path('roles/', views.get_roles, name='get_roles'),
    path('assign-role/', views.assign_user_role, name='assign_role'),
    
    # User management (admin only)
    path('users/', views.get_users, name='get_users'),
    path('users/<uuid:user_id>/', views.get_user_detail, name='get_user_detail'),
    path('users/<uuid:user_id>/update/', views.update_user, name='update_user'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/<uuid:user_id>/delete/', views.delete_user, name='delete_user'),
    
    # Token validation
    path('validate-token/', views.validate_token, name='validate_token'),
    
    # Permission check
    path('check-permission/', views.check_permission, name='check_permission'),
]

"""
API Documentation:

Authentication Endpoints:
-----------------------
POST /accounts/register/
    Register a new user
    Body: {
        "email": string,
        "password": string,
        "confirm_password": string,
        "first_name": string,
        "last_name": string,
        "phone_number": string (optional),
        "date_of_birth": date (optional)
    }

POST /accounts/verify-email/
    Verify user's email address
    Body: {
        "email": string,
        "verification_code": string
    }

POST /accounts/resend-verification/
    Resend verification email
    Body: {
        "email": string
    }

POST /accounts/login/
    Login and get JWT tokens
    Body: {
        "email": string,
        "password": string
    }

POST /accounts/refresh-token/
    Refresh access token
    Body: {
        "refresh": string
    }

POST /accounts/logout/
    Logout user by blacklisting token
    Body: {
        "refresh": string
    }

Password Management:
------------------
POST /accounts/request-password-reset/
    Request password reset
    Body: {
        "email": string
    }

POST /accounts/confirm-password-reset/
    Confirm password reset with code
    Body: {
        "email": string,
        "reset_code": string,
        "new_password": string,
        "confirm_password": string
    }

POST /accounts/change-password/
    Change password (requires authentication)
    Body: {
        "current_password": string,
        "new_password": string,
        "confirm_password": string
    }

Profile Management:
-----------------
GET /accounts/profile/
    Get user profile data (requires authentication)

PUT /accounts/profile/update/
    Update user profile (requires authentication)
    Body: {
        "first_name": string (optional),
        "last_name": string (optional),
        "phone_number": string (optional),
        "date_of_birth": date (optional),
        "bio": string (optional),
        "avatar": file (optional),
        "location": string (optional),
        "timezone": string (optional),
        "preferences": json (optional)
    }

DELETE /accounts/deactivate-account/
    Deactivate user account (requires authentication)
    Body: {
        "password": string,
        "refresh": string (optional)
    }

Admin Endpoints (require admin privileges):
-----------------------------------------
GET /accounts/roles/
    Get all roles

POST /accounts/assign-role/
    Assign role to user
    Body: {
        "user_id": string (UUID),
        "role_id": string (UUID)
    }

GET /accounts/users/
    Get all users
    Query parameters:
        role: string (filter by role)
        is_active: boolean (filter by active status)
        is_verified: boolean (filter by verification status)
        search: string (search in email, name, phone)

GET /accounts/users/<uuid:user_id>/
    Get specific user details

PUT /accounts/users/<uuid:user_id>/update/
    Update user details
    Body: {
        "first_name": string (optional),
        "last_name": string (optional),
        "phone_number": string (optional),
        "date_of_birth": date (optional),
        "is_active": boolean (optional),
        "is_verified": boolean (optional),
        "role_id": string (UUID) (optional)
    }

POST /accounts/users/create/
    Create a new user
    Body: {
        "email": string,
        "password": string,
        "confirm_password": string (optional),
        "first_name": string,
        "last_name": string,
        "phone_number": string (optional),
        "date_of_birth": date (optional),
        "role": UUID (optional),
        "verify_now": boolean (optional)
    }

DELETE /accounts/users/<uuid:user_id>/delete/
    Delete a user

Other Endpoints:
--------------
POST /accounts/validate-token/
    Validate JWT token
    Body: {
        "token": string
    }

POST /accounts/check-permission/
    Check if user has specific permission (requires authentication)
    Body: {
        "permission": string
    }
"""