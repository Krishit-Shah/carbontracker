from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import json
from .models import (
    Household, EnergyUsage, TransportUsage, DietEmission, 
    MonthlyEmissionSummary, EcoTip, FuelPrice, IndianState,
    EmissionFactor, UserGoal
)
from .serializers import (
    HouseholdSerializer, EnergyUsageSerializer, TransportUsageSerializer,
    DietEmissionSerializer, MonthlyEmissionSummarySerializer, EcoTipSerializer
)
from .scraper import run_all_scrapers
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import plotly.graph_objs as go
import plotly.offline as pyo

# Home and Authentication Views
def home(request):
    """Home page view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    context = {
        'total_users': Household.objects.count(),
        'total_emissions_tracked': MonthlyEmissionSummary.objects.aggregate(
            total=Sum('total_emissions')
        )['total'] or 0,
        'recent_tips': EcoTip.objects.filter(is_active=True)[:3],
    }
    return render(request, 'tracker/home.html', context)

def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Please complete your household profile.')
            return redirect('household_setup')
    else:
        form = UserCreationForm()
    return render(request, 'tracker/register.html', {'form': form})

@login_required
def household_setup(request):
    """Household profile setup"""
    try:
        household = request.user.household
        return redirect('dashboard')
    except Household.DoesNotExist:
        if request.method == 'POST':
            data = request.POST
            try:
                with transaction.atomic():
                    state = None
                    if data.get('state'):
                        state = IndianState.objects.get(id=data.get('state'))
                    
                    household = Household.objects.create(
                        user=request.user,
                        name=data.get('name'),
                        house_type=data.get('house_type'),
                        members_count=int(data.get('members_count', 1)),
                        state=state,
                        city=data.get('city'),
                        income_range=data.get('income_range', '')
                    )
                    messages.success(request, 'Household profile created successfully!')
                    return redirect('dashboard')
            except Exception as e:
                messages.error(request, f'Error creating household profile: {e}')
        
        context = {
            'states': IndianState.objects.all(),
        }
        return render(request, 'tracker/household_setup.html', context)

# Dashboard Views
@login_required
def dashboard(request):
    """Main dashboard view"""
    try:
        household = request.user.household
    except Household.DoesNotExist:
        return redirect('household_setup')
    
    current_month = timezone.now().date().replace(day=1)
    
    # Get current month summary
    current_summary, created = MonthlyEmissionSummary.objects.get_or_create(
        household=household,
        month_year=current_month
    )
    
    # Get last 6 months data
    six_months_ago = current_month - timedelta(days=180)
    monthly_summaries = MonthlyEmissionSummary.objects.filter(
        household=household,
        month_year__gte=six_months_ago
    ).order_by('month_year')
    
    # Calculate trends
    previous_month = current_month - timedelta(days=30)
    try:
        previous_summary = MonthlyEmissionSummary.objects.get(
            household=household,
            month_year=previous_month.replace(day=1)
        )
        trend = ((current_summary.total_emissions - previous_summary.total_emissions) / 
                previous_summary.total_emissions * 100) if previous_summary.total_emissions > 0 else 0
    except MonthlyEmissionSummary.DoesNotExist:
        trend = 0
    
    # Get recent eco tips
    tips = EcoTip.objects.filter(is_active=True).order_by('?')[:3]
    
    # Get fuel prices for user's state
    fuel_prices = []
    if household.state:
        fuel_prices = FuelPrice.objects.filter(
            state=household.state,
            date_recorded=timezone.now().date()
        )
    
    context = {
        'household': household,
        'current_summary': current_summary,
        'monthly_summaries': monthly_summaries,
        'trend': trend,
        'tips': tips,
        'fuel_prices': fuel_prices,
        'chart_data': prepare_chart_data(monthly_summaries)
    }
    
    return render(request, 'tracker/dashboard.html', context)

def prepare_chart_data(monthly_summaries):
    """Prepare data for charts"""
    months = []
    energy_data = []
    transport_data = []
    diet_data = []
    total_data = []
    
    for summary in monthly_summaries:
        months.append(summary.month_year.strftime('%b %Y'))
        energy_data.append(float(summary.total_energy_emissions))
        transport_data.append(float(summary.total_transport_emissions))
        diet_data.append(float(summary.total_diet_emissions))
        total_data.append(float(summary.total_emissions))
    
    return {
        'months': months,
        'energy': energy_data,
        'transport': transport_data,
        'diet': diet_data,
        'total': total_data
    }

# Data Entry Views
@login_required
def add_energy_usage(request):
    """Add energy usage data"""
    household = get_object_or_404(Household, user=request.user)
    
    if request.method == 'POST':
        try:
            data = request.POST
            month_year = datetime.strptime(data.get('month_year'), '%Y-%m').date()
            
            energy_usage = EnergyUsage.objects.create(
                household=household,
                energy_source=data.get('energy_source'),
                consumption=float(data.get('consumption')),
                unit=data.get('unit'),
                cost=float(data.get('cost', 0)) if data.get('cost') else None,
                month_year=month_year
            )
            
            # Update monthly summary
            summary, created = MonthlyEmissionSummary.objects.get_or_create(
                household=household,
                month_year=month_year
            )
            summary.save()  # This will recalculate totals
            
            messages.success(request, 'Energy usage added successfully!')
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f'Error adding energy usage: {e}')
    
    return render(request, 'tracker/add_energy.html', {
        'household': household,
        'energy_sources': EnergyUsage.ENERGY_SOURCES
    })

@login_required
def add_transport_usage(request):
    """Add transportation data"""
    household = get_object_or_404(Household, user=request.user)
    
    if request.method == 'POST':
        try:
            data = request.POST
            month_year = datetime.strptime(data.get('month_year'), '%Y-%m').date()
            
            transport_usage = TransportUsage.objects.create(
                household=household,
                transport_mode=data.get('transport_mode'),
                distance_km=float(data.get('distance_km')),
                frequency_per_month=int(data.get('frequency_per_month', 1)),
                fuel_cost=float(data.get('fuel_cost', 0)) if data.get('fuel_cost') else None,
                month_year=month_year
            )
            
            # Update monthly summary
            summary, created = MonthlyEmissionSummary.objects.get_or_create(
                household=household,
                month_year=month_year
            )
            summary.save()
            
            messages.success(request, 'Transportation data added successfully!')
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f'Error adding transport data: {e}')
    
    return render(request, 'tracker/add_transport.html', {
        'household': household,
        'transport_modes': TransportUsage.TRANSPORT_MODES
    })

@login_required
def add_diet_data(request):
    """Add diet emission data"""
    household = get_object_or_404(Household, user=request.user)
    
    if request.method == 'POST':
        try:
            data = request.POST
            month_year = datetime.strptime(data.get('month_year'), '%Y-%m').date()
            
            diet_emission = DietEmission.objects.create(
                household=household,
                diet_type=data.get('diet_type'),
                frequency=data.get('frequency'),
                food_waste_percentage=float(data.get('food_waste_percentage', 10)),
                month_year=month_year
            )
            
            # Update monthly summary
            summary, created = MonthlyEmissionSummary.objects.get_or_create(
                household=household,
                month_year=month_year
            )
            summary.save()
            
            messages.success(request, 'Diet data added successfully!')
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f'Error adding diet data: {e}')
    
    return render(request, 'tracker/add_diet.html', {
        'household': household,
        'diet_types': DietEmission.DIET_TYPES,
        'frequencies': DietEmission.MEAL_FREQUENCIES
    })

# Analysis and Reports Views
@login_required
def reports(request):
    """Detailed reports and analysis"""
    household = get_object_or_404(Household, user=request.user)
    
    # Get yearly data
    current_year = timezone.now().year
    yearly_summaries = MonthlyEmissionSummary.objects.filter(
        household=household,
        month_year__year=current_year
    ).order_by('month_year')
    
    # Calculate yearly totals
    yearly_totals = yearly_summaries.aggregate(
        energy=Sum('total_energy_emissions'),
        transport=Sum('total_transport_emissions'),
        diet=Sum('total_diet_emissions'),
        total=Sum('total_emissions')
    )
    
    # Calculate per capita emissions
    yearly_per_capita = (yearly_totals['total'] or 0) / household.members_count
    
    # Compare with national average
    national_average = 1900  # kg CO2 per person per year for India
    comparison = (yearly_per_capita / national_average * 100) if national_average > 0 else 0
    
    context = {
        'household': household,
        'yearly_summaries': yearly_summaries,
        'yearly_totals': yearly_totals,
        'yearly_per_capita': yearly_per_capita,
        'national_average': national_average,
        'comparison': comparison,
        'chart_data': prepare_chart_data(yearly_summaries)
    }
    
    return render(request, 'tracker/reports.html', context)

@login_required
def eco_tips(request):
    """Eco-friendly tips and suggestions"""
    category = request.GET.get('category', '')
    
    tips = EcoTip.objects.filter(is_active=True)
    if category:
        tips = tips.filter(category=category)
    
    paginator = Paginator(tips, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': EcoTip.CATEGORIES,
        'selected_category': category
    }
    
    return render(request, 'tracker/eco_tips.html', context)

# AJAX and API Views
@login_required
def get_chart_data(request):
    """Get chart data for dashboard"""
    household = get_object_or_404(Household, user=request.user)
    
    period = request.GET.get('period', '6months')
    
    if period == '6months':
        start_date = timezone.now().date() - timedelta(days=180)
    elif period == '1year':
        start_date = timezone.now().date() - timedelta(days=365)
    else:
        start_date = timezone.now().date() - timedelta(days=30)
    
    summaries = MonthlyEmissionSummary.objects.filter(
        household=household,
        month_year__gte=start_date
    ).order_by('month_year')
    
    data = prepare_chart_data(summaries)
    return JsonResponse(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_scraped_data(request):
    """API endpoint to trigger data scraping"""
    try:
        success = run_all_scrapers()
        if success:
            return Response({'message': 'Data scraping completed successfully'})
        else:
            return Response({'error': 'Data scraping failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# REST API ViewSets
class HouseholdViewSet(viewsets.ModelViewSet):
    serializer_class = HouseholdSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Household.objects.filter(user=self.request.user)

class EnergyUsageViewSet(viewsets.ModelViewSet):
    serializer_class = EnergyUsageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return EnergyUsage.objects.filter(household__user=self.request.user)

class TransportUsageViewSet(viewsets.ModelViewSet):
    serializer_class = TransportUsageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return TransportUsage.objects.filter(household__user=self.request.user)

class DietEmissionViewSet(viewsets.ModelViewSet):
    serializer_class = DietEmissionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return DietEmission.objects.filter(household__user=self.request.user)

class MonthlyEmissionSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MonthlyEmissionSummarySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MonthlyEmissionSummary.objects.filter(household__user=self.request.user)

class EcoTipViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EcoTipSerializer
    queryset = EcoTip.objects.filter(is_active=True)
