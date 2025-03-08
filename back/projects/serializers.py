from rest_framework import serializers
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from accounts.models import CustomUser, UserProfile, Role
from accounts.serializers import UserSerializer, UserDetailSerializer
from .models import (
    Project, BrandingPackage, PageDesign, FrontEndPackage, BackEndPackage,
    DashboardPackage, MediaPackage, SalesPackage, Documentation,
    ProjectApplication, ProjectMilestone
)


class ProjectMilestoneListSerializer(serializers.ModelSerializer):
    """Serializer for listing ProjectMilestone objects"""
    days_until = serializers.SerializerMethodField()
    overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectMilestone
        fields = [
            'id', 'title', 'due_date', 'is_completed', 'completion_date',
            'days_until', 'overdue'
        ]
    
    def get_days_until(self, obj):
        if obj.is_completed:
            return 0
        return obj.days_until_due()
    
    def get_overdue(self, obj):
        return obj.is_overdue()


class ProjectMilestoneDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for ProjectMilestone objects"""
    days_until = serializers.SerializerMethodField()
    overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectMilestone
        fields = [
            'id', 'project', 'title', 'description', 'due_date',
            'is_completed', 'completion_date', 'days_until', 'overdue'
        ]
        read_only_fields = ['completion_date']
    
    def get_days_until(self, obj):
        if obj.is_completed:
            return 0
        return obj.days_until_due()
    
    def get_overdue(self, obj):
        return obj.is_overdue()


class ProjectApplicationListSerializer(serializers.ModelSerializer):
    """Serializer for listing ProjectApplication objects"""
    applicant_name = serializers.SerializerMethodField()
    applicant_email = serializers.ReadOnlyField(source='applicant.email')
    applicant_role = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectApplication
        fields = [
            'id', 'project', 'applicant', 'applicant_name', 'applicant_email',
            'applicant_role', 'application_type', 'submission_date', 
            'priority_level', 'is_addressed'
        ]
        
    def get_applicant_name(self, obj):
        return obj.applicant.get_full_name()
    
    def get_applicant_role(self, obj):
        try:
            if hasattr(obj.applicant, 'profile') and obj.applicant.profile.role:
                return obj.applicant.profile.role.get_name_display()
            return None
        except UserProfile.DoesNotExist:
            return None


class ProjectApplicationDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for ProjectApplication objects"""
    applicant = UserSerializer(read_only=True)
    
    class Meta:
        model = ProjectApplication
        fields = [
            'id', 'project', 'applicant', 'application_type',
            'application_details', 'submission_date', 'priority_level',
            'is_addressed'
        ]
        read_only_fields = ['submission_date']


class PageDesignSerializer(serializers.ModelSerializer):
    """Serializer for PageDesign objects"""
    
    class Meta:
        model = PageDesign
        fields = [
            'id', 'project', 'page_name', 'page_sections'
        ]


class BrandingPackageSerializer(serializers.ModelSerializer):
    """Serializer for BrandingPackage objects"""
    
    class Meta:
        model = BrandingPackage
        fields = [
            'id', 'project', 'needs_brand_design', 'brand_design_details',
            'needs_digital_design', 'digital_design_details',
            'needs_paper_design', 'paper_design_details',
            'process_simplification', 'additional_info'
        ]


class FrontEndPackageSerializer(serializers.ModelSerializer):
    """Serializer for FrontEndPackage objects"""
    
    class Meta:
        model = FrontEndPackage
        fields = [
            'id', 'project', 'needs_web_template', 'web_template_details',
            'needs_dynamic_website', 'dynamic_website_details',
            'page_content_structure', 'additional_info'
        ]


class BackEndPackageSerializer(serializers.ModelSerializer):
    """Serializer for BackEndPackage objects"""
    
    class Meta:
        model = BackEndPackage
        fields = [
            'id', 'project', 'needs_client_models', 'client_models_details',
            'needs_organized_models', 'organized_models_details',
            'needs_base_app', 'base_app_details',
            'main_database_name', 'user_data_app_name',
            'data_collection_requirements',
            'needs_rest_api', 'needs_endpoints', 'needs_custom_urls', 'api_details',
            'main_features', 'administrator_roles', 'additional_info'
        ]


class DashboardPackageSerializer(serializers.ModelSerializer):
    """Serializer for DashboardPackage objects"""
    
    class Meta:
        model = DashboardPackage
        fields = [
            'id', 'project', 'needs_admin_dashboard', 'custom_django_dashboard',
            'custom_template_design', 'dashboard_details',
            'needs_content_manager', 'needs_custom_fields',
            'needs_page_template_fields', 'content_manager_details',
            'needs_statistics', 'statistics_details',
            'needs_progress_tracking', 'progress_tracking_details',
            'additional_info'
        ]


class MediaPackageSerializer(serializers.ModelSerializer):
    """Serializer for MediaPackage objects"""
    
    class Meta:
        model = MediaPackage
        fields = [
            'id', 'project', 'needs_media_manager', 'media_organization',
            'needs_media_storage', 'media_storage_details',
            'needs_data_center', 'data_center_details',
            'has_images', 'has_audio', 'has_video',
            'additional_info'
        ]


class SalesPackageSerializer(serializers.ModelSerializer):
    """Serializer for SalesPackage objects"""
    
    class Meta:
        model = SalesPackage
        fields = [
            'id', 'project', 'needs_sales_management',
            'needs_expense_management', 'needs_stock_management',
            'needs_sales_dashboard', 'custom_sales_dashboard',
            'custom_sales_template', 'financial_management_details',
            'additional_info'
        ]


class DocumentationSerializer(serializers.ModelSerializer):
    """Serializer for Documentation objects"""
    
    class Meta:
        model = Documentation
        fields = [
            'id', 'project', 'documentation_details',
            'licensing_details', 'additional_info'
        ]


class ProjectListSerializer(serializers.ModelSerializer):
    """Serializer for listing Project objects"""
    client_name = serializers.SerializerMethodField()
    client_email = serializers.ReadOnlyField(source='client.email')
    client_role = serializers.SerializerMethodField()
    days_active = serializers.SerializerMethodField()
    completion_estimated = serializers.SerializerMethodField()
    project_code = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'client', 'client_name', 'client_email', 'client_role', 
            'status', 'progress', 'created_date', 'finished_date', 'days_active',
            'project_code', 'completion_estimated',
            'includes_branding', 'includes_frontend', 'includes_backend',
            'includes_dashboard', 'includes_media', 'includes_sales'
        ]
    
    def get_client_name(self, obj):
        return obj.client.get_full_name()
    
    def get_client_role(self, obj):
        try:
            if hasattr(obj.client, 'profile') and obj.client.profile.role:
                return obj.client.profile.role.get_name_display()
            return None
        except UserProfile.DoesNotExist:
            return None
    
    def get_days_active(self, obj):
        return obj.days_since_created()
    
    def get_completion_estimated(self, obj):
        if obj.status == 'completed':
            return None
        return obj.get_estimated_completion_date()
    
    def get_project_code(self, obj):
        return obj.get_project_code()


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Project objects with nested related data"""
    client = UserDetailSerializer(read_only=True)
    milestones = ProjectMilestoneListSerializer(many=True, read_only=True)
    page_designs = PageDesignSerializer(many=True, read_only=True)
    applications = ProjectApplicationListSerializer(many=True, read_only=True)
    days_active = serializers.SerializerMethodField()
    completion_estimated = serializers.SerializerMethodField()
    project_code = serializers.SerializerMethodField()
    has_overdue_milestones = serializers.SerializerMethodField()
    
    # Nested package details
    branding_package = BrandingPackageSerializer(read_only=True)
    frontend_package = FrontEndPackageSerializer(read_only=True)
    backend_package = BackEndPackageSerializer(read_only=True)
    dashboard_package = DashboardPackageSerializer(read_only=True)
    media_package = MediaPackageSerializer(read_only=True)
    sales_package = SalesPackageSerializer(read_only=True)
    documentation = DocumentationSerializer(read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'client', 'status', 'progress',
            'created_date', 'updated_date', 'finished_date', 'days_active',
            'project_code', 'completion_estimated', 'has_overdue_milestones',
            'includes_branding', 'includes_frontend', 'includes_backend',
            'includes_dashboard', 'includes_media', 'includes_sales',
            'branding_package', 'frontend_package', 'backend_package',
            'dashboard_package', 'media_package', 'sales_package',
            'documentation', 'milestones', 'page_designs', 'applications'
        ]
        read_only_fields = ['created_date', 'updated_date', 'finished_date', 'progress']
    
    def get_days_active(self, obj):
        return obj.days_since_created()
    
    def get_completion_estimated(self, obj):
        if obj.status == 'completed':
            return None
        return obj.get_estimated_completion_date()
    
    def get_project_code(self, obj):
        return obj.get_project_code()
    
    def get_has_overdue_milestones(self, obj):
        return obj.has_overdue_milestones()


class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating Project objects"""
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'client', 'status', 
            'includes_branding', 'includes_frontend', 'includes_backend',
            'includes_dashboard', 'includes_media', 'includes_sales',
        ]
    
    def validate_client(self, value):
        """
        Validate that client is a valid user with client role
        """
        if not value.is_client():
            raise serializers.ValidationError(
                "Selected user must have a client role. Please assign the client role to this user first."
            )
        return value
    
    def validate_status(self, value):
        """
        Validate status transitions
        """
        if self.instance:  # Update case
            # If changing from 'completed' to something else, clear finished_date
            if self.instance.status == 'completed' and value != 'completed':
                self.instance.finished_date = None
            
            # If changing to 'completed', set finished_date if not already set
            elif value == 'completed' and self.instance.status != 'completed':
                self.instance.finished_date = timezone.now()
        
        return value
    
    def create(self, validated_data):
        """
        Custom create method to handle package creation
        """
        project = Project.objects.create(**validated_data)
        return project


class ProjectTimelineSerializer(serializers.ModelSerializer):
    """Serializer for generating Project timeline data"""
    timeline = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'timeline']
    
    def get_timeline(self, obj):
        return obj.get_timeline()


class CompleteProjectPackageSerializer(serializers.ModelSerializer):
    """Serializer for creating a project with all packages in one request"""
    branding_package = BrandingPackageSerializer(required=False)
    frontend_package = FrontEndPackageSerializer(required=False)
    backend_package = BackEndPackageSerializer(required=False)
    dashboard_package = DashboardPackageSerializer(required=False)
    media_package = MediaPackageSerializer(required=False)
    sales_package = SalesPackageSerializer(required=False)
    documentation = DocumentationSerializer(required=False)
    milestones = ProjectMilestoneDetailSerializer(many=True, required=False)
    page_designs = PageDesignSerializer(many=True, required=False)
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'client', 'status', 
            'includes_branding', 'includes_frontend', 'includes_backend',
            'includes_dashboard', 'includes_media', 'includes_sales',
            'branding_package', 'frontend_package', 'backend_package',
            'dashboard_package', 'media_package', 'sales_package',
            'documentation', 'milestones', 'page_designs'
        ]
    
    def validate_client(self, value):
        """
        Validate that client is a valid user with client role
        """
        if not value.is_client():
            raise serializers.ValidationError(
                "Selected user must have a client role. Please assign the client role to this user first."
            )
        return value
    
    @transaction.atomic
    def create(self, validated_data):
        """Create project with nested packages"""
        # Extract nested package data
        branding_data = None
        frontend_data = None
        backend_data = None
        dashboard_data = None
        media_data = None
        sales_data = None
        documentation_data = None
        milestones_data = []
        page_designs_data = []
        
        if 'branding_package' in validated_data:
            branding_data = validated_data.pop('branding_package')
        
        if 'frontend_package' in validated_data:
            frontend_data = validated_data.pop('frontend_package')
        
        if 'backend_package' in validated_data:
            backend_data = validated_data.pop('backend_package')
        
        if 'dashboard_package' in validated_data:
            dashboard_data = validated_data.pop('dashboard_package')
        
        if 'media_package' in validated_data:
            media_data = validated_data.pop('media_package')
        
        if 'sales_package' in validated_data:
            sales_data = validated_data.pop('sales_package')
        
        if 'documentation' in validated_data:
            documentation_data = validated_data.pop('documentation')
        
        if 'milestones' in validated_data:
            milestones_data = validated_data.pop('milestones')
        
        if 'page_designs' in validated_data:
            page_designs_data = validated_data.pop('page_designs')
        
        # Create project
        project = Project.objects.create(**validated_data)
        
        # Create packages if included and data provided
        if project.includes_branding and branding_data:
            BrandingPackage.objects.create(project=project, **branding_data)
        
        if project.includes_frontend and frontend_data:
            FrontEndPackage.objects.create(project=project, **frontend_data)
        
        if project.includes_backend and backend_data:
            BackEndPackage.objects.create(project=project, **backend_data)
        
        if project.includes_dashboard and dashboard_data:
            DashboardPackage.objects.create(project=project, **dashboard_data)
        
        if project.includes_media and media_data:
            MediaPackage.objects.create(project=project, **media_data)
        
        if project.includes_sales and sales_data:
            SalesPackage.objects.create(project=project, **sales_data)
        
        # Always create documentation
        if documentation_data:
            Documentation.objects.create(project=project, **documentation_data)
        else:
            Documentation.objects.create(project=project)
        
        # Create milestones
        for milestone_data in milestones_data:
            ProjectMilestone.objects.create(project=project, **milestone_data)
        
        # Create page designs
        for design_data in page_designs_data:
            PageDesign.objects.create(project=project, **design_data)
        
        # If no milestones were provided, create a default milestone
        if not milestones_data:
            ProjectMilestone.objects.create(
                project=project,
                title="Project Setup",
                description="Initial project setup and requirements gathering",
                due_date=timezone.now() + timezone.timedelta(days=7),
                is_completed=False
            )
        
        return project
    
    @transaction.atomic
    def update(self, instance, validated_data):
        """Update project with nested packages"""
        # Extract nested package data
        branding_data = None
        frontend_data = None
        backend_data = None
        dashboard_data = None
        media_data = None
        sales_data = None
        documentation_data = None
        
        if 'branding_package' in validated_data:
            branding_data = validated_data.pop('branding_package')
        
        if 'frontend_package' in validated_data:
            frontend_data = validated_data.pop('frontend_package')
        
        if 'backend_package' in validated_data:
            backend_data = validated_data.pop('backend_package')
        
        if 'dashboard_package' in validated_data:
            dashboard_data = validated_data.pop('dashboard_package')
        
        if 'media_package' in validated_data:
            media_data = validated_data.pop('media_package')
        
        if 'sales_package' in validated_data:
            sales_data = validated_data.pop('sales_package')
        
        if 'documentation' in validated_data:
            documentation_data = validated_data.pop('documentation')
        
        # Update project fields
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        
        # Update packages if data provided
        if branding_data and hasattr(instance, 'branding_package'):
            branding_package = instance.branding_package
            for field, value in branding_data.items():
                setattr(branding_package, field, value)
            branding_package.save()
        
        if frontend_data and hasattr(instance, 'frontend_package'):
            frontend_package = instance.frontend_package
            for field, value in frontend_data.items():
                setattr(frontend_package, field, value)
            frontend_package.save()
        
        if backend_data and hasattr(instance, 'backend_package'):
            backend_package = instance.backend_package
            for field, value in backend_data.items():
                setattr(backend_package, field, value)
            backend_package.save()
        
        if dashboard_data and hasattr(instance, 'dashboard_package'):
            dashboard_package = instance.dashboard_package
            for field, value in dashboard_data.items():
                setattr(dashboard_package, field, value)
            dashboard_package.save()
        
        if media_data and hasattr(instance, 'media_package'):
            media_package = instance.media_package
            for field, value in media_data.items():
                setattr(media_package, field, value)
            media_package.save()
        
        if sales_data and hasattr(instance, 'sales_package'):
            sales_package = instance.sales_package
            for field, value in sales_data.items():
                setattr(sales_package, field, value)
            sales_package.save()
        
        if documentation_data and hasattr(instance, 'documentation'):
            documentation = instance.documentation
            for field, value in documentation_data.items():
                setattr(documentation, field, value)
            documentation.save()
        
        return instance


class CompleteMilestoneSerializer(serializers.Serializer):
    """Serializer for marking a milestone as completed"""
    milestone_id = serializers.UUIDField()
    
    def validate_milestone_id(self, value):
        try:
            milestone = ProjectMilestone.objects.get(pk=value)
            return milestone
        except ProjectMilestone.DoesNotExist:
            raise serializers.ValidationError("Milestone not found.")
    
    def save(self):
        milestone = self.validated_data['milestone_id']
        milestone.mark_completed()
        return milestone


class ProjectStatisticsSerializer(serializers.Serializer):
    """Serializer for project statistics"""
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    client_id = serializers.UUIDField(required=False)
    
    def to_representation(self, instance):
        from .utils import get_project_stats
        
        start_date = self.context.get('start_date')
        end_date = self.context.get('end_date')
        client_id = self.context.get('client_id')
        
        return get_project_stats(start_date, end_date, client_id)


class ProjectRequirementsDocumentSerializer(serializers.ModelSerializer):
    """Serializer for generating project requirements document"""
    requirements_document = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'requirements_document']
    
    def get_requirements_document(self, obj):
        return obj.get_requirements_document()


class ProjectApplicationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating project applications with details"""
    
    class Meta:
        model = ProjectApplication
        fields = [
            'project', 'applicant', 'application_type',
            'application_details', 'priority_level'
        ]
    
    def validate(self, data):
        """
        Validate that the applicant is a valid user with the right permissions
        """
        applicant = data.get('applicant')
        if not applicant or not applicant.is_active:
            raise serializers.ValidationError({"applicant": "Valid active user is required."})
        
        # Check if user has permission to submit applications
        if not applicant.has_permission('can_submit_applications'):
            raise serializers.ValidationError({
                "applicant": "User does not have permission to submit applications."
            })
            
        return data
    
    def create(self, validated_data):
        application = ProjectApplication.objects.create(**validated_data)
        return application


class ClientProjectsSerializer(serializers.ModelSerializer):
    """Serializer for listing a client's projects"""
    projects_count = serializers.SerializerMethodField()
    active_projects = serializers.SerializerMethodField()
    completed_projects = serializers.SerializerMethodField()
    pending_projects = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'projects_count', 'active_projects', 'completed_projects', 'pending_projects'
        ]
    
    def get_projects_count(self, obj):
        return obj.projects.count()
    
    def get_active_projects(self, obj):
        return obj.projects.filter(status='in_progress').count()
    
    def get_completed_projects(self, obj):
        return obj.projects.filter(status='completed').count()
    
    def get_pending_projects(self, obj):
        return obj.projects.filter(status='pending').count()