from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API Router for REST endpoints
router = DefaultRouter()
router.register(r'households', views.HouseholdViewSet, basename='household')
router.register(r'energy-usage', views.EnergyUsageViewSet, basename='energyusage')
router.register(r'transport-usage', views.TransportUsageViewSet, basename='transportusage')
router.register(r'diet-emissions', views.DietEmissionViewSet, basename='dietemission')
router.register(r'monthly-summaries', views.MonthlyEmissionSummaryViewSet, basename='monthlysummary')
router.register(r'eco-tips', views.EcoTipViewSet, basename='ecotip')

urlpatterns = [
    # Home and Authentication
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('household-setup/', views.household_setup, name='household_setup'),
    
    # Dashboard and Main Views
    path('dashboard/', views.dashboard, name='dashboard'),
    path('reports/', views.reports, name='reports'),
    path('tips/', views.eco_tips, name='eco_tips'),
    
    # Data Entry Forms
    path('add-energy/', views.add_energy_usage, name='add_energy'),
    path('add-transport/', views.add_transport_usage, name='add_transport'),
    path('add-diet/', views.add_diet_data, name='add_diet'),
    
    # AJAX Endpoints
    path('ajax/chart-data/', views.get_chart_data, name='chart_data'),
    
    # API Endpoints
    path('api/', include(router.urls)),
    path('api/update-data/', views.update_scraped_data, name='update_scraped_data'),
]