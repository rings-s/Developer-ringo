from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count

from .models import CustomUser, UserProfile, Role


class UserProfileInline(admin.StackedInline):
    """
    Inline admin for UserProfile, embedded in the CustomUser admin
    """
    model = UserProfile
    can_delete = False
    verbose_name_plural = _('Profile')
    fk_name = 'user'
    fields = ('role', 'bio', 'avatar', 'location', 'timezone', 'preferences', 'last_active')
    readonly_fields = ('last_active',)
    extra = 0


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin view for CustomUser model
    """
    inlines = (UserProfileInline,)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone_number', 'date_of_birth')}),
        (_('Verification'), {'fields': ('is_verified', 'verification_code', 'verification_code_created', 
                                       'reset_code', 'reset_code_created')}),
        (_('Security'), {'fields': ('last_login_ip', 'failed_login_attempts', 'last_failed_login', 
                                   'account_locked_until')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'get_role', 'is_verified', 
                   'is_staff', 'is_active', 'date_joined', 'get_last_active')
    list_filter = ('is_active', 'is_verified', 'is_staff', 'is_superuser', 'profile__role')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-date_joined',)
    readonly_fields = ('last_login', 'date_joined', 'last_login_ip', 'last_failed_login', 
                      'account_locked_until')
    actions = ['verify_users', 'deactivate_users', 'activate_users']

    def get_role(self, obj):
        """
        Get the role display name for the list view
        """
        try:
            if obj.profile and obj.profile.role:
                return obj.profile.role.get_name_display()
            return '-'
        except UserProfile.DoesNotExist:
            return '-'
    get_role.short_description = _('Role')
    get_role.admin_order_field = 'profile__role__name'

    def get_last_active(self, obj):
        """
        Get the last active timestamp for the list view
        """
        try:
            if obj.profile and obj.profile.last_active:
                return obj.profile.last_active
            return '-'
        except UserProfile.DoesNotExist:
            return '-'
    get_last_active.short_description = _('Last Active')
    get_last_active.admin_order_field = 'profile__last_active'

    def verify_users(self, request, queryset):
        """
        Action to mark selected users as verified
        """
        updated = 0
        for user in queryset:
            if not user.is_verified:
                user.verify_email()
                updated += 1
        self.message_user(request, _(f"{updated} users were successfully verified."))
    verify_users.short_description = _("Mark selected users as verified")

    def deactivate_users(self, request, queryset):
        """
        Action to deactivate selected users
        """
        updated = queryset.update(is_active=False)
        self.message_user(request, _(f"{updated} users were successfully deactivated."))
    deactivate_users.short_description = _("Deactivate selected users")

    def activate_users(self, request, queryset):
        """
        Action to activate selected users
        """
        updated = queryset.update(is_active=True)
        self.message_user(request, _(f"{updated} users were successfully activated."))
    activate_users.short_description = _("Activate selected users")

    def get_queryset(self, request):
        """
        Override to prefetch related profile and role objects
        """
        return super().get_queryset(request).select_related('profile__role')

    def get_inline_instances(self, request, obj=None):
        """
        Only show inlines for existing users
        """
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """
    Admin view for Role model
    """
    list_display = ('name', 'get_name_display', 'is_active', 'get_users_count', 'created_at')
    list_filter = ('is_active', 'name')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('permissions',)
    fieldsets = (
        (None, {'fields': ('name', 'description', 'is_active')}),
        (_('Permissions'), {'fields': ('permissions',)}),
        (_('Dates'), {'fields': ('created_at', 'updated_at')}),
    )
    actions = ['activate_roles', 'deactivate_roles']

    def get_name_display(self, obj):
        """
        Get the display name for the role
        """
        return obj.get_name_display()
    get_name_display.short_description = _('Display Name')

    def get_users_count(self, obj):
        """
        Count users with this role
        """
        return obj.userprofile_set.count()
    get_users_count.short_description = _('Users')

    def get_queryset(self, request):
        """
        Prefetch related userprofiles for better performance
        """
        return super().get_queryset(request).prefetch_related('userprofile_set')

    def activate_roles(self, request, queryset):
        """
        Action to activate selected roles
        """
        updated = queryset.update(is_active=True)
        self.message_user(request, _(f"{updated} roles were successfully activated."))
    activate_roles.short_description = _("Activate selected roles")

    def deactivate_roles(self, request, queryset):
        """
        Action to deactivate selected roles
        """
        updated = queryset.update(is_active=False)
        self.message_user(request, _(f"{updated} roles were successfully deactivated."))
    deactivate_roles.short_description = _("Deactivate selected roles")