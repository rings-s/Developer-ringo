from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q, Count
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from accounts.models import CustomUser
from .models import (
    Project, BrandingPackage, PageDesign, FrontEndPackage, BackEndPackage,
    DashboardPackage, MediaPackage, SalesPackage, Documentation,
    ProjectApplication, ProjectMilestone
)
from .serializers import (
    ProjectListSerializer, ProjectDetailSerializer, ProjectCreateUpdateSerializer,
    ProjectMilestoneListSerializer, ProjectMilestoneDetailSerializer,
    ProjectApplicationListSerializer, ProjectApplicationDetailSerializer,
    PageDesignSerializer, BrandingPackageSerializer, FrontEndPackageSerializer,
    BackEndPackageSerializer, DashboardPackageSerializer, MediaPackageSerializer,
    SalesPackageSerializer, DocumentationSerializer, ProjectTimelineSerializer,
    CompleteProjectPackageSerializer, CompleteMilestoneSerializer,
    ProjectStatisticsSerializer, ProjectRequirementsDocumentSerializer,
    ProjectApplicationCreateSerializer, ClientProjectsSerializer
)
from .utils import (
    generate_project_summary, export_projects_to_csv,
    get_project_statistics_by_client, send_milestone_notifications,
    get_dashboard_data
)


class IsOwnerOrAdmin(IsAuthenticated):
    """Permission to allow only owners or admins to access objects"""
    
    def has_object_permission(self, request, view, obj):
        # Always allow admin users
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Check if object has a client attribute
        if hasattr(obj, 'client'):
            return obj.client == request.user
        
        # Check if object has a project with a client attribute
        if hasattr(obj, 'project') and hasattr(obj.project, 'client'):
            return obj.project.client == request.user
        
        # Check if object is a user
        if isinstance(obj, CustomUser):
            return obj == request.user
        
        return False


# Project Views
class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing Project instances"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Filter projects for regular users, show all for admins
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Project.objects.all().select_related('client').prefetch_related(
                'milestones', 'page_designs', 'applications'
            )
        # Regular users only see their own projects
        return Project.objects.filter(client=user).select_related('client').prefetch_related(
            'milestones', 'page_designs', 'applications'
        )
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProjectCreateUpdateSerializer
        return ProjectDetailSerializer
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get comprehensive project summary"""
        project = self.get_object()
        summary = generate_project_summary(project.id)
        if summary:
            return Response(summary)
        return Response(
            {"detail": "Could not generate project summary"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    @action(detail=True, methods=['get'])
    def timeline(self, request, pk=None):
        """Get project timeline for visualization"""
        project = self.get_object()
        serializer = ProjectTimelineSerializer(project)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def requirements_document(self, request, pk=None):
        """Generate requirements document for the project"""
        project = self.get_object()
        serializer = ProjectRequirementsDocumentSerializer(project)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """Export all projects to CSV"""
        if not request.user.is_staff and not request.user.is_superuser:
            return Response(
                {"detail": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        csv_data = export_projects_to_csv()
        if csv_data:
            response = HttpResponse(csv_data, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="projects_export.csv"'
            return response
        
        return Response(
            {"detail": "Could not generate CSV export"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Project Milestone Views
class ProjectMilestoneViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing ProjectMilestone instances"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Filter milestones for regular users, show all for admins
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return ProjectMilestone.objects.all().select_related('project')
        # Regular users only see milestones for their own projects
        return ProjectMilestone.objects.filter(project__client=user).select_related('project')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectMilestoneListSerializer
        return ProjectMilestoneDetailSerializer
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark a milestone as completed"""
        milestone = self.get_object()
        milestone.mark_completed()
        serializer = self.get_serializer(milestone)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def create_next(self, request, pk=None):
        """Create a new milestone after this one"""
        milestone = self.get_object()
        
        title = request.data.get('title')
        description = request.data.get('description')
        days_offset = request.data.get('days_offset', 14)
        
        if not title:
            return Response(
                {"detail": "Title is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        next_milestone = milestone.create_next_milestone(
            title=title,
            description=description,
            days_offset=int(days_offset)
        )
        
        serializer = self.get_serializer(next_milestone)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Project Application Views
class ProjectApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing ProjectApplication instances"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return ProjectApplication.objects.all().select_related('project', 'applicant')
        # Regular users only see applications they submitted or for their projects
        return ProjectApplication.objects.filter(
            Q(applicant=user) | Q(project__client=user)
        ).select_related('project', 'applicant')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectApplicationListSerializer
        elif self.action == 'create':
            return ProjectApplicationCreateSerializer
        return ProjectApplicationDetailSerializer
    
    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)


# Package View Base Class
class PackageBaseView(generics.RetrieveUpdateAPIView):
    """Base view for retrieving and updating package instances"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return self.model.objects.all()
        return self.model.objects.filter(project__client=user)


# Package-specific Views
class BrandingPackageView(PackageBaseView):
    """View for retrieving and updating BrandingPackage instances"""
    serializer_class = BrandingPackageSerializer
    model = BrandingPackage


class FrontEndPackageView(PackageBaseView):
    """View for retrieving and updating FrontEndPackage instances"""
    serializer_class = FrontEndPackageSerializer
    model = FrontEndPackage


class BackEndPackageView(PackageBaseView):
    """View for retrieving and updating BackEndPackage instances"""
    serializer_class = BackEndPackageSerializer
    model = BackEndPackage


class DashboardPackageView(PackageBaseView):
    """View for retrieving and updating DashboardPackage instances"""
    serializer_class = DashboardPackageSerializer
    model = DashboardPackage


class MediaPackageView(PackageBaseView):
    """View for retrieving and updating MediaPackage instances"""
    serializer_class = MediaPackageSerializer
    model = MediaPackage


class SalesPackageView(PackageBaseView):
    """View for retrieving and updating SalesPackage instances"""
    serializer_class = SalesPackageSerializer
    model = SalesPackage


class DocumentationView(PackageBaseView):
    """View for retrieving and updating Documentation instances"""
    serializer_class = DocumentationSerializer
    model = Documentation


class PageDesignViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing PageDesign instances"""
    serializer_class = PageDesignSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return PageDesign.objects.all().select_related('project')
        return PageDesign.objects.filter(project__client=user).select_related('project')


class CompleteProjectPackageView(generics.CreateAPIView):
    """Create a complete project with all packages in one request"""
    serializer_class = CompleteProjectPackageSerializer
    permission_classes = [IsAuthenticated]


class CompleteMilestoneView(APIView):
    """View for marking a milestone as completed"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = CompleteMilestoneSerializer(data=request.data)
        if serializer.is_valid():
            milestone = serializer.save()
            return Response({
                "id": str(milestone.id),
                "title": milestone.title,
                "is_completed": milestone.is_completed,
                "completion_date": milestone.completion_date
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Utility Views
class DashboardDataView(APIView):
    """View for retrieving dashboard data"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        dashboard_data = get_dashboard_data()
        return Response(dashboard_data)


class ProjectStatisticsView(APIView):
    """View for retrieving project statistics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Parse query parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        client_id = request.query_params.get('client_id')
        
        # Only admins can see all clients' statistics
        if client_id and not request.user.is_staff and not request.user.is_superuser:
            # Ensure users can only access their own statistics
            if str(request.user.id) != client_id:
                return Response(
                    {"detail": "Permission denied"},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # If not admin and no client_id specified, use current user's ID
        if not client_id and not request.user.is_staff and not request.user.is_superuser:
            client_id = str(request.user.id)
        
        # Create serializer context with parameters
        context = {
            'start_date': start_date,
            'end_date': end_date,
            'client_id': client_id
        }
        
        serializer = ProjectStatisticsSerializer(instance=None, context=context)
        return Response(serializer.data)


class ProjectStatisticsByClientView(APIView):
    """View for retrieving project statistics grouped by client"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        client_id = request.query_params.get('client_id')
        statistics = get_project_statistics_by_client(client_id)
        return Response(statistics)


class ClientProjectsView(generics.ListAPIView):
    """View for listing clients with their projects"""
    serializer_class = ClientProjectsSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        return CustomUser.objects.annotate(
            projects_count=Count('projects')
        ).filter(projects_count__gt=0)


class SendMilestoneNotificationsView(APIView):
    """View for sending milestone notifications manually"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def post(self, request):
        notifications_sent = send_milestone_notifications()
        return Response({
            "notifications_sent": notifications_sent,
            "message": f"Sent {notifications_sent} notification emails"
        })