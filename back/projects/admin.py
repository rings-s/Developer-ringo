from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html, mark_safe
from django.urls import reverse
from django.db.models import Count

from .models import (
    Project, BrandingPackage, PageDesign, FrontEndPackage, BackEndPackage,
    DashboardPackage, MediaPackage, SalesPackage, Documentation,
    ProjectApplication, ProjectMilestone
)


class ProjectMilestoneInline(admin.TabularInline):
    """
    Inline admin for ProjectMilestone
    """
    model = ProjectMilestone
    extra = 0
    fields = ('title', 'description', 'due_date', 'is_completed', 'completion_date')
    readonly_fields = ('completion_date',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('due_date')


class PageDesignInline(admin.TabularInline):
    """
    Inline admin for PageDesign
    """
    model = PageDesign
    extra = 0
    fields = ('page_name', 'page_sections')


class ProjectApplicationInline(admin.TabularInline):
    """
    Inline admin for ProjectApplication
    """
    model = ProjectApplication
    extra = 0
    fields = ('applicant', 'application_type', 'submission_date', 'priority_level', 'is_addressed')
    readonly_fields = ('applicant', 'application_type', 'submission_date')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('applicant')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """
    Admin view for Project model
    """
    list_display = ('name', 'client_display', 'status', 'progress_bar', 'created_date', 
                   'days_active', 'packages_summary', 'has_overdue_milestones_display')
    list_filter = ('status', 'includes_branding', 'includes_frontend', 'includes_backend',
                  'includes_dashboard', 'includes_media', 'includes_sales', 'created_date')
    search_fields = ('name', 'client__email', 'client__first_name', 'client__last_name')
    readonly_fields = ('created_date', 'updated_date', 'finished_date', 'progress')
    inlines = [ProjectMilestoneInline, PageDesignInline, ProjectApplicationInline]
    actions = ['mark_in_progress', 'mark_completed', 'mark_terminated']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'client', 'status', 'progress')
        }),
        (_('Packages'), {
            'fields': ('includes_branding', 'includes_frontend', 'includes_backend',
                      'includes_dashboard', 'includes_media', 'includes_sales')
        }),
        (_('Dates'), {
            'fields': ('created_date', 'updated_date', 'finished_date')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('client')
    
    def client_display(self, obj):
        """Display client with link to admin page"""
        if obj.client:
            url = reverse('admin:accounts_customuser_change', args=[obj.client.pk])
            return format_html('<a href="{}">{}</a>', url, obj.client.get_full_name() or obj.client.email)
        return '-'
    client_display.short_description = _('Client')
    client_display.admin_order_field = 'client__email'
    
    def progress_bar(self, obj):
        """Display progress bar"""
        return format_html(
            '<div style="width: 100px; background-color: #f8f8f8; border: 1px solid #ccc;">'
            '<div style="width: {}%; background-color: {}; color: white; text-align: center;">'
            '{}</div></div>',
            obj.progress,
            self._get_progress_color(obj.progress),
            f"{obj.progress}%"
        )
    progress_bar.short_description = _('Progress')
    progress_bar.admin_order_field = 'progress'
    
    def _get_progress_color(self, progress):
        """Get color for progress bar based on percentage"""
        if progress < 30:
            return "#ff4d4d"  # Red
        elif progress < 70:
            return "#ffad33"  # Orange
        else:
            return "#00cc44"  # Green
    
    def days_active(self, obj):
        """Display days since creation"""
        return obj.days_since_created()
    days_active.short_description = _('Days Active')
    
    def packages_summary(self, obj):
        """Display summary of included packages"""
        packages = []
        if obj.includes_branding: packages.append("Branding")
        if obj.includes_frontend: packages.append("Frontend")
        if obj.includes_backend: packages.append("Backend")
        if obj.includes_dashboard: packages.append("Dashboard")
        if obj.includes_media: packages.append("Media")
        if obj.includes_sales: packages.append("Sales")
        
        return ", ".join(packages) if packages else "-"
    packages_summary.short_description = _('Packages')
    
    def has_overdue_milestones_display(self, obj):
        """Display whether project has overdue milestones"""
        has_overdue = obj.has_overdue_milestones()
        color = "#ff4d4d" if has_overdue else "#00cc44"
        text = _("Yes") if has_overdue else _("No")
        return format_html('<span style="color: {};">{}</span>', color, text)
    has_overdue_milestones_display.short_description = _('Overdue Milestones')
    
    def mark_in_progress(self, request, queryset):
        """Mark selected projects as in progress"""
        queryset.update(status='in_progress')
        self.message_user(request, _(f"{queryset.count()} projects marked as in progress."))
    mark_in_progress.short_description = _("Mark selected projects as in progress")
    
    def mark_completed(self, request, queryset):
        """Mark selected projects as completed"""
        from django.utils import timezone
        for project in queryset:
            project.status = 'completed'
            project.progress = 100
            project.finished_date = timezone.now()
            project.save()
        self.message_user(request, _(f"{queryset.count()} projects marked as completed."))
    mark_completed.short_description = _("Mark selected projects as completed")
    
    def mark_terminated(self, request, queryset):
        """Mark selected projects as terminated"""
        queryset.update(status='terminated')
        self.message_user(request, _(f"{queryset.count()} projects marked as terminated."))
    mark_terminated.short_description = _("Mark selected projects as terminated")


@admin.register(ProjectMilestone)
class ProjectMilestoneAdmin(admin.ModelAdmin):
    """
    Admin view for ProjectMilestone model
    """
    list_display = ('title', 'project_link', 'due_date', 'is_completed', 'completion_date', 
                   'days_until_due', 'is_overdue_display')
    list_filter = ('is_completed', 'due_date', 'project__name')
    search_fields = ('title', 'description', 'project__name')
    readonly_fields = ('completion_date',)
    actions = ['mark_completed', 'mark_incomplete']
    
    fieldsets = (
        (None, {
            'fields': ('project', 'title', 'description')
        }),
        (_('Status'), {
            'fields': ('is_completed', 'completion_date', 'due_date')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('project')
    
    def project_link(self, obj):
        """Display project with link to admin page"""
        if obj.project:
            url = reverse('admin:projects_project_change', args=[obj.project.pk])
            return format_html('<a href="{}">{}</a>', url, obj.project.name)
        return '-'
    project_link.short_description = _('Project')
    project_link.admin_order_field = 'project__name'
    
    def days_until_due(self, obj):
        """Display days until due date"""
        days = obj.days_until_due()
        if obj.is_completed:
            return _("Completed")
        if days < 0:
            return format_html('<span style="color: #ff4d4d;">{}</span>', _("Overdue by {} days").format(abs(days)))
        return days
    days_until_due.short_description = _('Days Until Due')
    
    def is_overdue_display(self, obj):
        """Display whether milestone is overdue"""
        if obj.is_completed:
            return format_html('<span style="color: #00cc44;">{}</span>', _("Completed"))
        
        is_overdue = obj.is_overdue()
        color = "#ff4d4d" if is_overdue else "#00cc44"
        text = _("Yes") if is_overdue else _("No")
        return format_html('<span style="color: {};">{}</span>', color, text)
    is_overdue_display.short_description = _('Overdue')
    
    def mark_completed(self, request, queryset):
        """Mark selected milestones as completed"""
        from django.utils import timezone
        for milestone in queryset:
            milestone.mark_completed()
        self.message_user(request, _(f"{queryset.count()} milestones marked as completed."))
    mark_completed.short_description = _("Mark selected milestones as completed")
    
    def mark_incomplete(self, request, queryset):
        """Mark selected milestones as incomplete"""
        queryset.update(is_completed=False, completion_date=None)
        # Update project progress
        for milestone in queryset:
            milestone.project.recalculate_progress()
        self.message_user(request, _(f"{queryset.count()} milestones marked as incomplete."))
    mark_incomplete.short_description = _("Mark selected milestones as incomplete")


@admin.register(ProjectApplication)
class ProjectApplicationAdmin(admin.ModelAdmin):
    """
    Admin view for ProjectApplication model
    """
    list_display = ('project_link', 'applicant_link', 'application_type', 
                   'submission_date', 'priority_level_display', 'is_addressed')
    list_filter = ('application_type', 'priority_level', 'is_addressed', 'submission_date')
    search_fields = ('project__name', 'applicant__email', 'application_type', 'application_details')
    readonly_fields = ('submission_date',)
    actions = ['mark_addressed', 'mark_unaddressed']
    
    fieldsets = (
        (None, {
            'fields': ('project', 'applicant', 'application_type')
        }),
        (_('Details'), {
            'fields': ('application_details', 'priority_level', 'is_addressed')
        }),
        (_('Dates'), {
            'fields': ('submission_date',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('project', 'applicant')
    
    def project_link(self, obj):
        """Display project with link to admin page"""
        if obj.project:
            url = reverse('admin:projects_project_change', args=[obj.project.pk])
            return format_html('<a href="{}">{}</a>', url, obj.project.name)
        return '-'
    project_link.short_description = _('Project')
    project_link.admin_order_field = 'project__name'
    
    def applicant_link(self, obj):
        """Display applicant with link to admin page"""
        if obj.applicant:
            url = reverse('admin:accounts_customuser_change', args=[obj.applicant.pk])
            return format_html('<a href="{}">{}</a>', url, obj.applicant.get_full_name() or obj.applicant.email)
        return '-'
    applicant_link.short_description = _('Applicant')
    applicant_link.admin_order_field = 'applicant__email'
    
    def priority_level_display(self, obj):
        """Display priority level with color coding"""
        priority_colors = {
            0: "#999999",  # Gray - Low
            1: "#3399ff",  # Blue - Normal
            2: "#ffad33",  # Orange - High
            3: "#ff4d4d",  # Red - Urgent
        }
        priority_names = {
            0: _("Low"),
            1: _("Normal"),
            2: _("High"),
            3: _("Urgent"),
        }
        color = priority_colors.get(obj.priority_level, "#999999")
        text = priority_names.get(obj.priority_level, _("Unknown"))
        return format_html('<span style="color: {};">{}</span>', color, text)
    priority_level_display.short_description = _('Priority')
    priority_level_display.admin_order_field = 'priority_level'
    
    def mark_addressed(self, request, queryset):
        """Mark selected applications as addressed"""
        queryset.update(is_addressed=True)
        self.message_user(request, _(f"{queryset.count()} applications marked as addressed."))
    mark_addressed.short_description = _("Mark selected applications as addressed")
    
    def mark_unaddressed(self, request, queryset):
        """Mark selected applications as unaddressed"""
        queryset.update(is_addressed=False)
        self.message_user(request, _(f"{queryset.count()} applications marked as unaddressed."))
    mark_unaddressed.short_description = _("Mark selected applications as unaddressed")


# Register package models with simple ModelAdmin classes
class BasePackageAdmin(admin.ModelAdmin):
    """
    Base admin class for all package models
    """
    list_display = ('project_link',)
    search_fields = ('project__name',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('project')
    
    def project_link(self, obj):
        """Display project with link to admin page"""
        if obj.project:
            url = reverse('admin:projects_project_change', args=[obj.project.pk])
            return format_html('<a href="{}">{}</a>', url, obj.project.name)
        return '-'
    project_link.short_description = _('Project')
    project_link.admin_order_field = 'project__name'


@admin.register(BrandingPackage)
class BrandingPackageAdmin(BasePackageAdmin):
    """Admin view for BrandingPackage model"""
    list_display = BasePackageAdmin.list_display + (
        'needs_brand_design', 'needs_digital_design', 'needs_paper_design',
    )
    list_filter = ('needs_brand_design', 'needs_digital_design', 'needs_paper_design')


@admin.register(PageDesign)
class PageDesignAdmin(BasePackageAdmin):
    """Admin view for PageDesign model"""
    list_display = BasePackageAdmin.list_display + ('page_name',)
    search_fields = BasePackageAdmin.search_fields + ('page_name', 'page_sections')


@admin.register(FrontEndPackage)
class FrontEndPackageAdmin(BasePackageAdmin):
    """Admin view for FrontEndPackage model"""
    list_display = BasePackageAdmin.list_display + (
        'needs_web_template', 'needs_dynamic_website',
    )
    list_filter = ('needs_web_template', 'needs_dynamic_website')


@admin.register(BackEndPackage)
class BackEndPackageAdmin(BasePackageAdmin):
    """Admin view for BackEndPackage model"""
    list_display = BasePackageAdmin.list_display + (
        'needs_client_models', 'needs_organized_models', 'needs_base_app',
        'needs_rest_api',
    )
    list_filter = ('needs_client_models', 'needs_organized_models', 'needs_base_app',
                  'needs_rest_api', 'needs_endpoints', 'needs_custom_urls')


@admin.register(DashboardPackage)
class DashboardPackageAdmin(BasePackageAdmin):
    """Admin view for DashboardPackage model"""
    list_display = BasePackageAdmin.list_display + (
        'needs_admin_dashboard', 'needs_content_manager', 'needs_statistics',
        'needs_progress_tracking',
    )
    list_filter = ('needs_admin_dashboard', 'needs_content_manager', 'needs_statistics',
                  'needs_progress_tracking')


@admin.register(MediaPackage)
class MediaPackageAdmin(BasePackageAdmin):
    """Admin view for MediaPackage model"""
    list_display = BasePackageAdmin.list_display + (
        'needs_media_manager', 'needs_media_storage', 'needs_data_center',
        'has_images', 'has_audio', 'has_video',
    )
    list_filter = ('needs_media_manager', 'needs_media_storage', 'needs_data_center',
                  'has_images', 'has_audio', 'has_video')


@admin.register(SalesPackage)
class SalesPackageAdmin(BasePackageAdmin):
    """Admin view for SalesPackage model"""
    list_display = BasePackageAdmin.list_display + (
        'needs_sales_management', 'needs_expense_management', 'needs_stock_management',
        'needs_sales_dashboard',
    )
    list_filter = ('needs_sales_management', 'needs_expense_management', 'needs_stock_management',
                  'needs_sales_dashboard')


@admin.register(Documentation)
class DocumentationAdmin(BasePackageAdmin):
    """Admin view for Documentation model"""
    list_display = BasePackageAdmin.list_display
    
    
    
    

admin.site.site_header="Developer Ringo"
admin.site.site_title="Developer Ringo"