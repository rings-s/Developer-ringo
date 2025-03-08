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