from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Set application namespace
app_name = 'projects'

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'projects', views.ProjectViewSet, basename='project')
router.register(r'milestones', views.ProjectMilestoneViewSet, basename='milestone')
router.register(r'applications', views.ProjectApplicationViewSet, basename='application')
router.register(r'page-designs', views.PageDesignViewSet, basename='page-design')

# URL patterns
urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Package views
    path('packages/branding/<uuid:pk>/', views.BrandingPackageView.as_view(), name='branding-package'),
    path('packages/frontend/<uuid:pk>/', views.FrontEndPackageView.as_view(), name='frontend-package'),
    path('packages/backend/<uuid:pk>/', views.BackEndPackageView.as_view(), name='backend-package'),
    path('packages/dashboard/<uuid:pk>/', views.DashboardPackageView.as_view(), name='dashboard-package'),
    path('packages/media/<uuid:pk>/', views.MediaPackageView.as_view(), name='media-package'),
    path('packages/sales/<uuid:pk>/', views.SalesPackageView.as_view(), name='sales-package'),
    path('packages/documentation/<uuid:pk>/', views.DocumentationView.as_view(), name='documentation'),
    
    # Complete project package view
    path('complete-project-package/', views.CompleteProjectPackageView.as_view(), name='complete-project-package'),
    
    # Complete milestone
    path('complete-milestone/', views.CompleteMilestoneView.as_view(), name='complete-milestone'),
    
    # Utility views
    path('dashboard-data/', views.DashboardDataView.as_view(), name='dashboard-data'),
    path('project-statistics/', views.ProjectStatisticsView.as_view(), name='project-statistics'),
    path('project-statistics-by-client/', views.ProjectStatisticsByClientView.as_view(), name='project-statistics-by-client'),
    path('client-projects/', views.ClientProjectsView.as_view(), name='client-projects'),
    path('send-milestone-notifications/', views.SendMilestoneNotificationsView.as_view(), name='send-milestone-notifications'),
]