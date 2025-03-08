from django.db import models
from django.conf import settings  # Add this import to reference AUTH_USER_MODEL
from django.utils import timezone
import uuid


class Project(models.Model):
    """Main project model that connects all package components"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('terminated', 'Terminated'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='projects')  # Fixed: using AUTH_USER_MODEL
    name = models.CharField(max_length=255)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    finished_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.IntegerField(default=0, help_text="Progress percentage (0-100)")
    
    # Define which packages are included in this project
    includes_branding = models.BooleanField(default=False)
    includes_frontend = models.BooleanField(default=False)
    includes_backend = models.BooleanField(default=False)
    includes_dashboard = models.BooleanField(default=False)
    includes_media = models.BooleanField(default=False)
    includes_sales = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} ({self.client.username})"
    
    class Meta:
        ordering = ['-created_date']
    
    def recalculate_progress(self):
        """
        Recalculate project progress based on completed milestones
        """
        milestones = self.milestones.all()
        if not milestones.exists():
            self.progress = 0
        else:
            completed = milestones.filter(is_completed=True).count()
            total = milestones.count()
            self.progress = int((completed / total) * 100)
        
        self.save(update_fields=['progress'])
        return self.progress

    def get_project_code(self):
        """
        Get or generate a unique project code
        """
        return f"PD-{self.created_date.year}-{self.id.hex[:4].upper()}"

    def get_estimated_completion_date(self):
        """
        Estimate the completion date based on milestones
        """
        if self.status == 'completed' and self.finished_date:
            return self.finished_date
        
        future_milestones = self.milestones.filter(
            is_completed=False
        ).order_by('-due_date')
        
        if future_milestones.exists():
            # Return the latest milestone date
            return future_milestones.first().due_date
        
        # If no future milestones, estimate based on progress
        if self.progress < 10:
            # Just starting - estimate 2 months
            return timezone.now() + timezone.timedelta(days=60)
        elif self.progress < 50:
            # Early stages - estimate 1.5 months
            return timezone.now() + timezone.timedelta(days=45)
        elif self.progress < 80:
            # Mid stages - estimate 1 month
            return timezone.now() + timezone.timedelta(days=30)
        else:
            # Final stages - estimate 2 weeks
            return timezone.now() + timezone.timedelta(days=14)

    def get_timeline(self):
        """
        Get project timeline for visualization
        """
        from .utils import generate_project_timeline
        return generate_project_timeline(self)

    def get_requirements_document(self):
        """
        Generate a comprehensive requirements document
        """
        from .utils import generate_project_requirements_document
        return generate_project_requirements_document(self)

    def create_milestone(self, title, description=None, due_days=14):
        """
        Create a new milestone for this project
        """
        due_date = timezone.now() + timezone.timedelta(days=due_days)
        milestone = ProjectMilestone.objects.create(
            project=self,
            title=title,
            description=description,
            due_date=due_date,
            is_completed=False
        )
        return milestone

    def has_overdue_milestones(self):
        """
        Check if the project has any overdue milestones
        """
        return self.milestones.filter(
            is_completed=False,
            due_date__lt=timezone.now()
        ).exists()

    def get_next_milestone(self):
        """
        Get the next upcoming milestone
        """
        next_milestones = self.milestones.filter(
            is_completed=False,
            due_date__gte=timezone.now()
        ).order_by('due_date')
        
        if next_milestones.exists():
            return next_milestones.first()
        return None

    def get_packages_summary(self):
        """
        Get a summary of all included packages
        """
        packages = []
        
        if self.includes_branding:
            packages.append({
                'name': 'Branding',
                'has_record': hasattr(self, 'branding_package'),
                'details': self.branding_package if hasattr(self, 'branding_package') else None
            })
        
        if self.includes_frontend:
            packages.append({
                'name': 'Frontend (Svelte)',
                'has_record': hasattr(self, 'frontend_package'),
                'details': self.frontend_package if hasattr(self, 'frontend_package') else None
            })
        
        if self.includes_backend:
            packages.append({
                'name': 'Backend (Django)',
                'has_record': hasattr(self, 'backend_package'),
                'details': self.backend_package if hasattr(self, 'backend_package') else None
            })
        
        if self.includes_dashboard:
            packages.append({
                'name': 'Dashboard',
                'has_record': hasattr(self, 'dashboard_package'),
                'details': self.dashboard_package if hasattr(self, 'dashboard_package') else None
            })
        
        if self.includes_media:
            packages.append({
                'name': 'Media Management',
                'has_record': hasattr(self, 'media_package'),
                'details': self.media_package if hasattr(self, 'media_package') else None
            })
        
        if self.includes_sales:
            packages.append({
                'name': 'Sales Management',
                'has_record': hasattr(self, 'sales_package'),
                'details': self.sales_package if hasattr(self, 'sales_package') else None
            })
        
        return packages

    def days_since_created(self):
        """
        Calculate the number of days since project creation
        """
        return (timezone.now().date() - self.created_date.date()).days

    def days_until_completion(self):
        """
        Calculate the number of days until estimated completion
        """
        if self.status == 'completed':
            return 0
        
        est_completion = self.get_estimated_completion_date()
        return (est_completion.date() - timezone.now().date()).days


class BrandingPackage(models.Model):
    """Stores information about branding requirements"""
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='branding_package')
    
    # Brand Design
    needs_brand_design = models.BooleanField(default=False)
    brand_design_details = models.TextField(blank=True, null=True, 
        help_text="What are your brand design requirements?")
    
    # Digital Design
    needs_digital_design = models.BooleanField(default=False)
    digital_design_details = models.TextField(blank=True, null=True,
        help_text="What are your digital design requirements?")
    
    # Paper Design
    needs_paper_design = models.BooleanField(default=False)
    paper_design_details = models.TextField(blank=True, null=True,
        help_text="What are your paper design requirements?")
    
    # Process Simplification Question
    process_simplification = models.TextField(blank=True, null=True,
        help_text="What are ways to make the process easier to achieve the end result? Do you "
                 "have to show any Identification/Information to show it's a legit Business?")
    
    # Additional Information
    additional_info = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Branding Package for {self.project.name}"


class PageDesign(models.Model):
    """Stores information about page design requirements"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='page_designs')
    page_name = models.CharField(max_length=100)
    page_sections = models.TextField(blank=True, null=True,
        help_text="What do you want to have in each section? Is it a set of pictures, or some "
                "text about a certain topic?")
    
    def __str__(self):
        return f"{self.page_name} for {self.project.name}"


class FrontEndPackage(models.Model):
    """Stores information about frontend requirements using JavaScript Meta Frameworks"""
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='frontend_package')
    
    # Web Template
    needs_web_template = models.BooleanField(default=False)
    web_template_details = models.TextField(blank=True, null=True,
        help_text="What kind of web template do you need?")
    
    # Dynamic Website / Web-Application
    needs_dynamic_website = models.BooleanField(default=False)
    dynamic_website_details = models.TextField(blank=True, null=True,
        help_text="What are your requirements for the dynamic website/web-application?")
    
    # Page Content Structure
    page_content_structure = models.TextField(blank=True, null=True,
        help_text="What would you like to have on your pages? Break it down into sections.")
    
    # Additional Information
    additional_info = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Frontend Package for {self.project.name}"


class BackEndPackage(models.Model):
    """Stores information about backend requirements using Django"""
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='backend_package')
    
    # Backend Framework is always Django
    
    # Client Models Requirements
    needs_client_models = models.BooleanField(default=False)
    client_models_details = models.TextField(blank=True, null=True,
        help_text="What kind of client models do you need?")
    
    # Organized Client Models
    needs_organized_models = models.BooleanField(default=False)
    organized_models_details = models.TextField(blank=True, null=True,
        help_text="How would you like your client models organized?")
    
    # Base App Requirements
    needs_base_app = models.BooleanField(default=False)
    base_app_details = models.TextField(blank=True, null=True,
        help_text="What functionality do you need in the base app (User Base, Groups, Authentication)?")
    
    # Main Database App
    main_database_name = models.CharField(max_length=100, blank=True, null=True,
        help_text="Name of your main database app where client models are stored")
    
    # User Data App
    user_data_app_name = models.CharField(max_length=100, blank=True, null=True,
        help_text="Name of app for user permissions and other functionality")
    
    # Data Collection
    data_collection_requirements = models.TextField(blank=True, null=True,
        help_text="What do you want to learn about your audience?")
    
    # API Requirements
    needs_rest_api = models.BooleanField(default=False)
    needs_endpoints = models.BooleanField(default=False)
    needs_custom_urls = models.BooleanField(default=False)
    api_details = models.TextField(blank=True, null=True,
        help_text="Details about your API requirements (serializers, endpoints, URLs)")
    
    # Main Features Description
    main_features = models.TextField(blank=True, null=True,
        help_text="What are the main Functions or Features of the application? Do they have "
                 "any Sub-Functions or Paid Features for the Clients and Consumers?")
    
    # Additional Information
    additional_info = models.TextField(blank=True, null=True)
    
    # Administrator Roles (moved from CustomPythonPackage)
    administrator_roles = models.TextField(blank=True, null=True,
        help_text="Who is the main Administrator? Do they have any Employees or Sub-Admins? "
                 "Is there someone who challenges the Project?")
    
    def __str__(self):
        return f"Backend Package for {self.project.name}"


class DashboardPackage(models.Model):
    """Stores information about Django dashboard requirements"""
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='dashboard_package')
    
    # Dashboard Requirements
    needs_admin_dashboard = models.BooleanField(default=False)
    custom_django_dashboard = models.BooleanField(default=False)
    custom_template_design = models.BooleanField(default=False)
    dashboard_details = models.TextField(blank=True, null=True,
        help_text="What features do you need in your dashboard? (Statistics, Frontend Content Editor, etc.)")
    
    # Page/Content Manager
    needs_content_manager = models.BooleanField(default=False)
    needs_custom_fields = models.BooleanField(default=False)
    needs_page_template_fields = models.BooleanField(default=False)
    content_manager_details = models.TextField(blank=True, null=True,
        help_text="What would you like to edit? Are there going to be posts or articles like a blog? "
                 "Are they a fixed set of text? Or will it be different types of content?")
    
    # Statistics
    needs_statistics = models.BooleanField(default=False)
    statistics_details = models.TextField(blank=True, null=True,
        help_text="What type of statistics would you like to see about your audience?")
    
    # Timeline & Progress Tracking
    needs_progress_tracking = models.BooleanField(default=False)
    progress_tracking_details = models.TextField(blank=True, null=True,
        help_text="Details about timeline and progress bar requirements")
    
    # Additional Information
    additional_info = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Dashboard Package for {self.project.name}"


class MediaPackage(models.Model):
    """Stores information about media management requirements"""
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='media_package')
    
    # Media Management Requirements
    needs_media_manager = models.BooleanField(default=False)
    media_organization = models.TextField(blank=True, null=True,
        help_text="How would you like to manage your media? Would you like to split it into different "
                 "Categories, Genres, Places, and People?")
    
    # Media Storage Options
    needs_media_storage = models.BooleanField(default=False)
    media_storage_details = models.TextField(blank=True, null=True,
        help_text="What are your media storage requirements?")
    
    # Data Center Options
    needs_data_center = models.BooleanField(default=False)
    data_center_details = models.TextField(blank=True, null=True,
        help_text="What are your data center requirements?")
    
    # Media Types
    has_images = models.BooleanField(default=False)
    has_audio = models.BooleanField(default=False)
    has_video = models.BooleanField(default=False)
    
    # Additional Information
    additional_info = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Media Package for {self.project.name}"


class SalesPackage(models.Model):
    """Stores information about sales management requirements"""
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='sales_package')
    
    # Sales Management Requirements
    needs_sales_management = models.BooleanField(default=False)
    needs_expense_management = models.BooleanField(default=False)
    needs_stock_management = models.BooleanField(default=False)
    
    # Sales Dashboard
    needs_sales_dashboard = models.BooleanField(default=False)
    custom_sales_dashboard = models.BooleanField(default=False)
    custom_sales_template = models.BooleanField(default=False)
    
    # Financial Management
    financial_management_details = models.TextField(blank=True, null=True,
        help_text="Would you like to manage your Finances through the website?")
    
    # Additional Information
    additional_info = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Sales Package for {self.project.name}"


class Documentation(models.Model):
    """Stores information about documentation requirements"""
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='documentation')
    
    # Documentation Requirements
    documentation_details = models.TextField(blank=True, null=True,
        help_text="Think about the most important aspects in the application that need documentation")
    
    # Licensing Information
    licensing_details = models.TextField(blank=True, null=True,
        help_text="Details about licensing requirements")
    
    # Additional Information
    additional_info = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Documentation for {self.project.name}"


class ProjectApplication(models.Model):
    """Stores information about project application form submissions"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='project_applications')  # Fixed: using AUTH_USER_MODEL
    submission_date = models.DateTimeField(auto_now_add=True)
    application_type = models.CharField(max_length=100)
    application_details = models.TextField(blank=True, null=True)
    priority_level = models.IntegerField(default=0)
    is_addressed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Application for {self.project.name} by {self.applicant.username}"


class ProjectMilestone(models.Model):
    """Tracks project milestones and progress"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField()
    completion_date = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.title} for {self.project.name}"
    
    def days_until_due(self):
        """
        Calculate days until due date
        """
        if self.is_completed:
            return 0
        
        return (self.due_date.date() - timezone.now().date()).days

    def is_overdue(self):
        """
        Check if milestone is overdue
        """
        return not self.is_completed and self.due_date < timezone.now()

    def mark_completed(self, save=True):
        """
        Mark milestone as completed
        """
        self.is_completed = True
        self.completion_date = timezone.now()
        
        if save:
            self.save(update_fields=['is_completed', 'completion_date'])
            # Update project progress
            self.project.recalculate_progress()
        
        return self

    def create_next_milestone(self, title, description=None, days_offset=14):
        """
        Create a new milestone after this one
        """
        # Base new milestone on this one's due date or completion date
        if self.is_completed and self.completion_date:
            base_date = self.completion_date
        else:
            base_date = self.due_date
        
        due_date = base_date + timezone.timedelta(days=days_offset)
        
        return ProjectMilestone.objects.create(
            project=self.project,
            title=title,
            description=description,
            due_date=due_date,
            is_completed=False
        )