from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count, Q

from .models import (
    Project, BrandingPackage, PageDesign, FrontEndPackage, BackEndPackage,
    DashboardPackage, MediaPackage, SalesPackage, Documentation,
    ProjectApplication, ProjectMilestone
)


@receiver(post_save, sender=Project)
def create_project_packages(sender, instance, created, **kwargs):
    """
    Create associated package records when a new project is created
    """
    if created:
        # Create related package records based on project configuration
        if instance.includes_branding:
            BrandingPackage.objects.create(project=instance)
        
        if instance.includes_frontend:
            FrontEndPackage.objects.create(project=instance)
        
        if instance.includes_backend:
            BackEndPackage.objects.create(project=instance)
        
        if instance.includes_dashboard:
            DashboardPackage.objects.create(project=instance)
        
        if instance.includes_media:
            MediaPackage.objects.create(project=instance)
        
        if instance.includes_sales:
            SalesPackage.objects.create(project=instance)
        
        # Always create documentation
        Documentation.objects.create(project=instance)
        
        # Create initial milestone
        ProjectMilestone.objects.create(
            project=instance,
            title="Project Setup",
            description="Initial project setup and requirements gathering",
            due_date=timezone.now() + timezone.timedelta(days=7),
            is_completed=False
        )


@receiver(post_save, sender=Project)
def update_project_package_records(sender, instance, created, **kwargs):
    """
    Update the associated package records when project package flags change
    """
    if not created:
        # Handle branding package
        if instance.includes_branding and not hasattr(instance, 'branding_package'):
            BrandingPackage.objects.create(project=instance)
        
        # Handle frontend package
        if instance.includes_frontend and not hasattr(instance, 'frontend_package'):
            FrontEndPackage.objects.create(project=instance)
        
        # Handle backend package
        if instance.includes_backend and not hasattr(instance, 'backend_package'):
            BackEndPackage.objects.create(project=instance)
        
        # Handle dashboard package
        if instance.includes_dashboard and not hasattr(instance, 'dashboard_package'):
            DashboardPackage.objects.create(project=instance)
        
        # Handle media package
        if instance.includes_media and not hasattr(instance, 'media_package'):
            MediaPackage.objects.create(project=instance)
        
        # Handle sales package
        if instance.includes_sales and not hasattr(instance, 'sales_package'):
            SalesPackage.objects.create(project=instance)
        
        # Ensure documentation always exists
        if not hasattr(instance, 'documentation'):
            Documentation.objects.create(project=instance)


@receiver(post_save, sender=ProjectMilestone)
def update_project_progress(sender, instance, **kwargs):
    """
    Update project progress when milestones are updated
    """
    instance.project.recalculate_progress()


@receiver(post_delete, sender=ProjectMilestone)
def update_project_progress_on_delete(sender, instance, **kwargs):
    """
    Update project progress when milestones are deleted
    """
    try:
        # The milestone is already deleted, but we can still reference the project
        instance.project.recalculate_progress()
    except Project.DoesNotExist:
        # Project might have been deleted as well
        pass


@receiver(pre_save, sender=Project)
def handle_project_status_change(sender, instance, **kwargs):
    """
    Handle status transitions and set finished date when project is completed
    """
    try:
        old_instance = Project.objects.get(pk=instance.pk)
        
        # If status changed to completed, and wasn't previously completed
        if instance.status == 'completed' and old_instance.status != 'completed':
            # Set finished date if not already set
            if not instance.finished_date:
                instance.finished_date = timezone.now()
            
            # Set progress to 100% when completed
            instance.progress = 100
        
        # If status changed from completed to something else, clear finished date
        elif old_instance.status == 'completed' and instance.status != 'completed':
            instance.finished_date = None
        
    except Project.DoesNotExist:
        # This is a new instance, no status transition to handle
        pass


@receiver(post_save, sender=ProjectApplication)
def notify_on_new_application(sender, instance, created, **kwargs):
    """
    Send email notification when a new project application is received
    """
    if created and hasattr(settings, 'PROJECT_NOTIFICATION_EMAIL'):
        try:
            send_mail(
                f'New Project Application: {instance.application_type}',
                f'A new project application has been submitted:\n\n'
                f'Project: {instance.project.name}\n'
                f'Applicant: {instance.applicant.get_full_name() or instance.applicant.username}\n'
                f'Type: {instance.application_type}\n'
                f'Priority: {instance.priority_level}\n\n'
                f'Please log in to the admin panel to review the application.',
                settings.DEFAULT_FROM_EMAIL,
                [settings.PROJECT_NOTIFICATION_EMAIL],
                fail_silently=True,
            )
        except Exception as e:
            # Log the error but don't interrupt the save process
            print(f"Error sending project application notification: {e}")


def connect_all_signals():
    """
    This function doesn't do anything - it's just here to ensure the signals are imported
    Call this in your AppConfig.ready() method
    """
    pass