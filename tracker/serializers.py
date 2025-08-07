from rest_framework import serializers
from .models import (
    Household, IndianState, EnergyUsage, TransportUsage, DietEmission,
    MonthlyEmissionSummary, EcoTip, FuelPrice, EmissionFactor, UserGoal
)
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']

class IndianStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndianState
        fields = ['id', 'name', 'electricity_emission_factor']

class HouseholdSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    state = IndianStateSerializer(read_only=True)
    state_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Household
        fields = [
            'id', 'user', 'name', 'house_type', 'members_count',
            'state', 'state_id', 'city', 'income_range',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

class EmissionFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmissionFactor
        fields = [
            'id', 'category', 'name', 'unit', 'emission_factor',
            'source', 'is_active', 'created_at'
        ]

class EnergyUsageSerializer(serializers.ModelSerializer):
    household = HouseholdSerializer(read_only=True)
    
    class Meta:
        model = EnergyUsage
        fields = [
            'id', 'household', 'energy_source', 'consumption', 'unit',
            'cost', 'month_year', 'emission_calculated', 'created_at'
        ]
        read_only_fields = ['id', 'household', 'emission_calculated', 'created_at']
    
    def create(self, validated_data):
        # Automatically assign the household from the request user
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['household'] = request.user.household
        return super().create(validated_data)

class TransportUsageSerializer(serializers.ModelSerializer):
    household = HouseholdSerializer(read_only=True)
    
    class Meta:
        model = TransportUsage
        fields = [
            'id', 'household', 'transport_mode', 'distance_km',
            'frequency_per_month', 'fuel_cost', 'month_year',
            'emission_calculated', 'created_at'
        ]
        read_only_fields = ['id', 'household', 'emission_calculated', 'created_at']
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['household'] = request.user.household
        return super().create(validated_data)

class DietEmissionSerializer(serializers.ModelSerializer):
    household = HouseholdSerializer(read_only=True)
    
    class Meta:
        model = DietEmission
        fields = [
            'id', 'household', 'diet_type', 'frequency',
            'food_waste_percentage', 'month_year',
            'emission_calculated', 'created_at'
        ]
        read_only_fields = ['id', 'household', 'emission_calculated', 'created_at']
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['household'] = request.user.household
        return super().create(validated_data)

class MonthlyEmissionSummarySerializer(serializers.ModelSerializer):
    household = HouseholdSerializer(read_only=True)
    
    class Meta:
        model = MonthlyEmissionSummary
        fields = [
            'id', 'household', 'month_year', 'total_energy_emissions',
            'total_transport_emissions', 'total_diet_emissions',
            'total_emissions', 'per_capita_emissions',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'household', 'total_energy_emissions',
            'total_transport_emissions', 'total_diet_emissions',
            'total_emissions', 'per_capita_emissions',
            'created_at', 'updated_at'
        ]

class EcoTipSerializer(serializers.ModelSerializer):
    class Meta:
        model = EcoTip
        fields = [
            'id', 'title', 'content', 'category', 'potential_reduction',
            'is_active', 'source_url', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class FuelPriceSerializer(serializers.ModelSerializer):
    state = IndianStateSerializer(read_only=True)
    
    class Meta:
        model = FuelPrice
        fields = [
            'id', 'fuel_type', 'state', 'price', 'unit',
            'date_recorded', 'source', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class UserGoalSerializer(serializers.ModelSerializer):
    household = HouseholdSerializer(read_only=True)
    
    class Meta:
        model = UserGoal
        fields = [
            'id', 'household', 'goal_type', 'target_reduction_percentage',
            'baseline_emissions', 'target_date', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'household', 'created_at']
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['household'] = request.user.household
        return super().create(validated_data)

# Specialized serializers for specific use cases
class EmissionBreakdownSerializer(serializers.Serializer):
    """Serializer for emission breakdown data"""
    energy_emissions = serializers.FloatField()
    transport_emissions = serializers.FloatField()
    diet_emissions = serializers.FloatField()
    total_emissions = serializers.FloatField()
    per_capita_emissions = serializers.FloatField()
    month_year = serializers.DateField()

class ComparisonDataSerializer(serializers.Serializer):
    """Serializer for comparison with averages"""
    household_emissions = serializers.FloatField()
    national_average = serializers.FloatField()
    state_average = serializers.FloatField(required=False)
    comparison_percentage = serializers.FloatField()
    rank_percentile = serializers.FloatField(required=False)

class TrendDataSerializer(serializers.Serializer):
    """Serializer for trend analysis data"""
    period = serializers.CharField()
    current_emissions = serializers.FloatField()
    previous_emissions = serializers.FloatField()
    change_percentage = serializers.FloatField()
    trend_direction = serializers.CharField()

class ChartDataSerializer(serializers.Serializer):
    """Serializer for chart data"""
    labels = serializers.ListField(child=serializers.CharField())
    datasets = serializers.ListField(
        child=serializers.DictField(
            child=serializers.FloatField()
        )
    )

class DashboardSummarySerializer(serializers.Serializer):
    """Comprehensive dashboard data serializer"""
    household_info = HouseholdSerializer()
    current_month_summary = MonthlyEmissionSummarySerializer()
    emission_breakdown = EmissionBreakdownSerializer()
    comparison_data = ComparisonDataSerializer()
    trend_data = TrendDataSerializer()
    recent_tips = EcoTipSerializer(many=True)
    fuel_prices = FuelPriceSerializer(many=True)
    chart_data = ChartDataSerializer()

# Form validation serializers
class EnergyUsageFormSerializer(serializers.Serializer):
    """Serializer for energy usage form validation"""
    energy_source = serializers.ChoiceField(choices=EnergyUsage.ENERGY_SOURCES)
    consumption = serializers.FloatField(min_value=0)
    unit = serializers.CharField(max_length=10)
    cost = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    month_year = serializers.DateField()

class TransportUsageFormSerializer(serializers.Serializer):
    """Serializer for transport usage form validation"""
    transport_mode = serializers.ChoiceField(choices=TransportUsage.TRANSPORT_MODES)
    distance_km = serializers.FloatField(min_value=0)
    frequency_per_month = serializers.IntegerField(min_value=1)
    fuel_cost = serializers.DecimalField(max_digits=8, decimal_places=2, required=False)
    month_year = serializers.DateField()

class DietEmissionFormSerializer(serializers.Serializer):
    """Serializer for diet emission form validation"""
    diet_type = serializers.ChoiceField(choices=DietEmission.DIET_TYPES)
    frequency = serializers.ChoiceField(choices=DietEmission.MEAL_FREQUENCIES)
    food_waste_percentage = serializers.FloatField(min_value=0, max_value=100)
    month_year = serializers.DateField()