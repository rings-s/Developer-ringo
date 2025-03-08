from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum, F, ExpressionWrapper, fields
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import csv
import io
import uuid
import calendar
import logging
import json
from datetime import timedelta, datetime

from .models import (
    Project, BrandingPackage, PageDesign, FrontEndPackage, BackEndPackage,
    DashboardPackage, MediaPackage, SalesPackage, Documentation,
    ProjectApplication, ProjectMilestone
)

logger = logging.getLogger(__name__)


def generate_project_summary(project_id):
    """
    Generate a comprehensive summary of a project
    
    Returns a dictionary with project details or None if project is not found
    """
    try:
        project = Project.objects.get(pk=project_id)
        
        # Get project packages
        packages = []
        if project.includes_branding and hasattr(project, 'branding_package'):
            packages.append({
                'name': 'Branding',
                'details': {
                    'needs_brand_design': project.branding_package.needs_brand_design,
                    'needs_digital_design': project.branding_package.needs_digital_design,
                    'needs_paper_design': project.branding_package.needs_paper_design,
                }
            })
        
        if project.includes_frontend and hasattr(project, 'frontend_package'):
            packages.append({
                'name': 'Frontend',
                'details': {
                    'needs_web_template': project.frontend_package.needs_web_template,
                    'needs_dynamic_website': project.frontend_package.needs_dynamic_website,
                }
            })
        
        if project.includes_backend and hasattr(project, 'backend_package'):
            packages.append({
                'name': 'Backend',
                'details': {
                    'needs_client_models': project.backend_package.needs_client_models,
                    'needs_organized_models': project.backend_package.needs_organized_models,
                    'needs_base_app': project.backend_package.needs_base_app,
                    'needs_rest_api': project.backend_package.needs_rest_api,
                }
            })
        
        if project.includes_dashboard and hasattr(project, 'dashboard_package'):
            packages.append({
                'name': 'Dashboard',
                'details': {
                    'needs_admin_dashboard': project.dashboard_package.needs_admin_dashboard,
                    'needs_content_manager': project.dashboard_package.needs_content_manager,
                    'needs_statistics': project.dashboard_package.needs_statistics,
                    'needs_progress_tracking': project.dashboard_package.needs_progress_tracking,
                }
            })
        
        if project.includes_media and hasattr(project, 'media_package'):
            packages.append({
                'name': 'Media',
                'details': {
                    'needs_media_manager': project.media_package.needs_media_manager,
                    'needs_media_storage': project.media_package.needs_media_storage,
                    'needs_data_center': project.media_package.needs_data_center,
                    'has_images': project.media_package.has_images,
                    'has_audio': project.media_package.has_audio,
                    'has_video': project.media_package.has_video,
                }
            })
        
        if project.includes_sales and hasattr(project, 'sales_package'):
            packages.append({
                'name': 'Sales',
                'details': {
                    'needs_sales_management': project.sales_package.needs_sales_management,
                    'needs_expense_management': project.sales_package.needs_expense_management,
                    'needs_stock_management': project.sales_package.needs_stock_management,
                    'needs_sales_dashboard': project.sales_package.needs_sales_dashboard,
                }
            })
        
        # Get project milestones
        milestones = project.milestones.all().order_by('due_date')
        milestones_data = [
            {
                'id': str(m.id),
                'title': m.title,
                'description': m.description or "",
                'due_date': m.due_date.strftime('%Y-%m-%d'),
                'is_completed': m.is_completed,
                'completion_date': m.completion_date.strftime('%Y-%m-%d') if m.completion_date else None,
                'is_overdue': m.is_overdue(),
                'days_until_due': m.days_until_due(),
            }
            for m in milestones
        ]
        
        # Get page designs
        page_designs = project.page_designs.all()
        page_designs_data = [
            {
                'id': str(pd.id),
                'page_name': pd.page_name,
                'page_sections': pd.page_sections or "",
            }
            for pd in page_designs
        ]
        
        # Get project applications
        applications = project.applications.all().order_by('-submission_date')
        applications_data = [
            {
                'id': str(app.id),
                'applicant': app.applicant.get_full_name() or app.applicant.email,
                'application_type': app.application_type,
                'submission_date': app.submission_date.strftime('%Y-%m-%d'),
                'priority_level': app.priority_level,
                'is_addressed': app.is_addressed,
            }
            for app in applications
        ]
        
        # Build summary dictionary
        summary = {
            'id': str(project.id),
            'name': project.name,
            'client': {
                'id': str(project.client.id),
                'name': project.client.get_full_name(),
                'email': project.client.email,
            },
            'status': project.status,
            'progress': project.progress,
            'code': project.get_project_code(),
            'dates': {
                'created': project.created_date.strftime('%Y-%m-%d'),
                'updated': project.updated_date.strftime('%Y-%m-%d'),
                'finished': project.finished_date.strftime('%Y-%m-%d') if project.finished_date else None,
                'days_active': project.days_since_created(),
                'estimated_completion': project.get_estimated_completion_date().strftime('%Y-%m-%d') if project.status != 'completed' else None,
            },
            'packages': packages,
            'milestones': milestones_data,
            'page_designs': page_designs_data,
            'applications': applications_data,
            'has_overdue_milestones': project.has_overdue_milestones(),
        }
        
        return summary
    
    except Project.DoesNotExist:
        logger.error(f"Project with ID {project_id} not found")
        return None
    except Exception as e:
        logger.error(f"Error generating project summary for {project_id}: {str(e)}")
        return None


def export_projects_to_csv():
    """
    Export all projects to CSV
    
    Returns a CSV string with project data
    """
    try:
        # Get all projects with related data
        projects = Project.objects.all().select_related(
            'client', 
        ).prefetch_related(
            'milestones',
            'page_designs',
            'applications',
        )
        
        # Create CSV file
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header row
        header = [
            'Project ID', 'Name', 'Client Name', 'Client Email', 'Status', 
            'Progress', 'Created Date', 'Finished Date', 'Days Active',
            'Project Code', 'Includes Branding', 'Includes Frontend', 
            'Includes Backend', 'Includes Dashboard', 'Includes Media', 
            'Includes Sales', 'Milestones Total', 'Milestones Completed', 
            'Milestones Overdue', 'Page Designs Count', 'Applications Count'
        ]
        writer.writerow(header)
        
        # Write data rows
        for project in projects:
            # Get related counts
            milestones = list(project.milestones.all())
            milestones_total = len(milestones)
            milestones_completed = sum(1 for m in milestones if m.is_completed)
            milestones_overdue = sum(1 for m in milestones if m.is_overdue())
            page_designs_count = project.page_designs.count()
            applications_count = project.applications.count()
            
            # Format data
            row = [
                str(project.id),
                project.name,
                project.client.get_full_name(),
                project.client.email,
                project.status,
                f"{project.progress}%",
                project.created_date.strftime('%Y-%m-%d'),
                project.finished_date.strftime('%Y-%m-%d') if project.finished_date else 'N/A',
                project.days_since_created(),
                project.get_project_code(),
                'Yes' if project.includes_branding else 'No',
                'Yes' if project.includes_frontend else 'No',
                'Yes' if project.includes_backend else 'No',
                'Yes' if project.includes_dashboard else 'No',
                'Yes' if project.includes_media else 'No',
                'Yes' if project.includes_sales else 'No',
                milestones_total,
                milestones_completed,
                milestones_overdue,
                page_designs_count,
                applications_count,
            ]
            writer.writerow(row)
        
        return output.getvalue()
    
    except Exception as e:
        logger.error(f"Error exporting projects to CSV: {str(e)}")
        return None


def get_project_statistics_by_client(client_id=None):
    """
    Get project statistics by client
    
    If client_id is provided, only get statistics for that client
    Otherwise, get statistics for all clients
    
    Returns a dictionary with client statistics
    """
    try:
        from accounts.models import CustomUser
        
        # Base query for clients with projects
        clients_query = CustomUser.objects.annotate(
            projects_count=Count('projects', distinct=True),
            completed_projects=Count('projects', filter=Q(projects__status='completed'), distinct=True),
            in_progress_projects=Count('projects', filter=Q(projects__status='in_progress'), distinct=True),
            pending_projects=Count('projects', filter=Q(projects__status='pending'), distinct=True),
            terminated_projects=Count('projects', filter=Q(projects__status='terminated'), distinct=True),
        ).filter(projects_count__gt=0)
        
        # Filter by client ID if provided
        if client_id:
            clients_query = clients_query.filter(id=client_id)
        
        # Get statistics for each client
        client_stats = []
        for client in clients_query:
            # Get average completion time for this client's completed projects
            completed_projects = Project.objects.filter(
                client=client,
                status='completed',
                created_date__isnull=False,
                finished_date__isnull=False
            )
            
            avg_completion_days = 0
            if completed_projects.exists():
                completion_days = [
                    (p.finished_date - p.created_date).days
                    for p in completed_projects
                ]
                avg_completion_days = sum(completion_days) / len(completion_days)
            
            # Get package distribution for this client
            projects = Project.objects.filter(client=client)
            package_distribution = {
                'branding': projects.filter(includes_branding=True).count(),
                'frontend': projects.filter(includes_frontend=True).count(),
                'backend': projects.filter(includes_backend=True).count(),
                'dashboard': projects.filter(includes_dashboard=True).count(),
                'media': projects.filter(includes_media=True).count(),
                'sales': projects.filter(includes_sales=True).count(),
            }
            
            # Add client statistics to the list
            client_stats.append({
                'id': str(client.id),
                'name': client.get_full_name(),
                'email': client.email,
                'projects': {
                    'total': client.projects_count,
                    'completed': client.completed_projects,
                    'in_progress': client.in_progress_projects,
                    'pending': client.pending_projects,
                    'terminated': client.terminated_projects,
                },
                'avg_completion_days': round(avg_completion_days, 1),
                'package_distribution': package_distribution,
            })
        
        return client_stats
    
    except Exception as e:
        logger.error(f"Error getting project statistics by client: {str(e)}")
        return []


def send_milestone_notifications():
    """
    Send email notifications for upcoming and overdue milestones
    
    This function should be run daily by a scheduled task
    
    Returns the number of notifications sent
    """
    if not hasattr(settings, 'PROJECT_NOTIFICATION_EMAIL'):
        logger.warning("PROJECT_NOTIFICATION_EMAIL not set in settings")
        return 0
    
    try:
        notifications_sent = 0
        
        # Get overdue milestones
        overdue_milestones = ProjectMilestone.objects.filter(
            is_completed=False,
            due_date__lt=timezone.now()
        ).select_related('project', 'project__client')
        
        # Get milestones due soon (in the next 2 days)
        due_soon_milestones = ProjectMilestone.objects.filter(
            is_completed=False,
            due_date__gte=timezone.now(),
            due_date__lte=timezone.now() + timedelta(days=2)
        ).select_related('project', 'project__client')
        
        # Send notifications for overdue milestones
        if overdue_milestones.exists():
            overdue_data = []
            for milestone in overdue_milestones:
                days_overdue = (timezone.now().date() - milestone.due_date.date()).days
                overdue_data.append({
                    'project': milestone.project.name,
                    'milestone': milestone.title,
                    'due_date': milestone.due_date.strftime('%Y-%m-%d'),
                    'days_overdue': days_overdue,
                    'client': milestone.project.client.get_full_name(),
                    'client_email': milestone.project.client.email,
                })
            
            # Render email template
            context = {
                'overdue_milestones': overdue_data,
                'count': len(overdue_data),
            }
            html_message = render_to_string('projects/email/overdue_milestones_notification.html', context)
            plain_message = strip_tags(html_message)
            
            # Send email
            send_mail(
                subject=f"{len(overdue_data)} Overdue Project Milestones",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.PROJECT_NOTIFICATION_EMAIL],
                html_message=html_message,
                fail_silently=False,
            )
            
            notifications_sent += 1
        
        # Send notifications for milestones due soon
        if due_soon_milestones.exists():
            due_soon_data = []
            for milestone in due_soon_milestones:
                days_until = (milestone.due_date.date() - timezone.now().date()).days
                due_soon_data.append({
                    'project': milestone.project.name,
                    'milestone': milestone.title,
                    'due_date': milestone.due_date.strftime('%Y-%m-%d'),
                    'days_until': days_until,
                    'client': milestone.project.client.get_full_name(),
                    'client_email': milestone.project.client.email,
                })
            
            # Render email template
            context = {
                'due_soon_milestones': due_soon_data,
                'count': len(due_soon_data),
            }
            html_message = render_to_string('projects/email/upcoming_milestones_notification.html', context)
            plain_message = strip_tags(html_message)
            
            # Send email
            send_mail(
                subject=f"{len(due_soon_data)} Upcoming Project Milestones",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.PROJECT_NOTIFICATION_EMAIL],
                html_message=html_message,
                fail_silently=False,
            )
            
            notifications_sent += 1
        
        return notifications_sent
    
    except Exception as e:
        logger.error(f"Error sending milestone notifications: {str(e)}")
        return 0


def get_dashboard_data():
    """
    Get data for the admin dashboard
    
    Returns a dictionary with dashboard data
    """
    try:
        # Get overall project statistics
        total_projects = Project.objects.count()
        completed_projects = Project.objects.filter(status='completed').count()
        in_progress_projects = Project.objects.filter(status='in_progress').count()
        pending_projects = Project.objects.filter(status='pending').count()
        
        # Get milestone statistics
        total_milestones = ProjectMilestone.objects.count()
        completed_milestones = ProjectMilestone.objects.filter(is_completed=True).count()
        overdue_milestones = ProjectMilestone.objects.filter(
            is_completed=False,
            due_date__lt=timezone.now()
        ).count()
        
        # Get recent projects
        recent_projects = Project.objects.order_by('-created_date')[:5].values(
            'id', 'name', 'client__email', 'status', 'progress', 'created_date'
        )
        
        # Get recent milestones
        recent_milestones = ProjectMilestone.objects.order_by('-due_date')[:5].values(
            'id', 'project__name', 'title', 'due_date', 'is_completed'
        )
        
        # Get package statistics
        package_stats = {
            'branding': Project.objects.filter(includes_branding=True).count(),
            'frontend': Project.objects.filter(includes_frontend=True).count(),
            'backend': Project.objects.filter(includes_backend=True).count(),
            'dashboard': Project.objects.filter(includes_dashboard=True).count(),
            'media': Project.objects.filter(includes_media=True).count(),
            'sales': Project.objects.filter(includes_sales=True).count(),
        }
        
        # Get monthly project data for current year
        monthly_data = get_monthly_projects_data(timezone.now().year)
        
        # Build dashboard data dictionary
        dashboard_data = {
            'projects': {
                'total': total_projects,
                'completed': completed_projects,
                'in_progress': in_progress_projects,
                'pending': pending_projects,
                'completion_rate': round((completed_projects / total_projects) * 100, 1) if total_projects > 0 else 0,
            },
            'milestones': {
                'total': total_milestones,
                'completed': completed_milestones,
                'overdue': overdue_milestones,
                'completion_rate': round((completed_milestones / total_milestones) * 100, 1) if total_milestones > 0 else 0,
            },
            'recent_projects': list(recent_projects),
            'recent_milestones': list(recent_milestones),
            'package_stats': package_stats,
            'monthly_data': monthly_data,
        }
        
        return dashboard_data
    
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        return {}