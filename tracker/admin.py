from django.contrib import admin
from .models import (
    IndianState, Household, EmissionFactor, EnergyUsage, 
    TransportUsage, DietEmission, MonthlyEmissionSummary, 
    EcoTip, FuelPrice, UserGoal
)

@admin.register(IndianState)
class IndianStateAdmin(admin.ModelAdmin):
    list_display = ['name', 'electricity_emission_factor', 'created_at']
    search_fields = ['name']
    ordering = ['name']

@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'house_type', 'members_count', 'state', 'city', 'created_at']
    list_filter = ['house_type', 'state', 'income_range', 'created_at']
    search_fields = ['name', 'user__username', 'city']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'house_type', 'members_count')
        }),
        ('Location', {
            'fields': ('state', 'city')
        }),
        ('Demographics', {
            'fields': ('income_range',)
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(EmissionFactor)
class EmissionFactorAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'emission_factor', 'unit', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'source']
    ordering = ['category', 'name']
    
@admin.register(EnergyUsage)
class EnergyUsageAdmin(admin.ModelAdmin):
    list_display = ['household', 'energy_source', 'consumption', 'unit', 'month_year', 'emission_calculated']
    list_filter = ['energy_source', 'month_year', 'created_at']
    search_fields = ['household__name', 'household__user__username']
    readonly_fields = ['emission_calculated', 'created_at']
    date_hierarchy = 'month_year'

@admin.register(TransportUsage)
class TransportUsageAdmin(admin.ModelAdmin):
    list_display = ['household', 'transport_mode', 'distance_km', 'frequency_per_month', 'month_year', 'emission_calculated']
    list_filter = ['transport_mode', 'month_year']
    search_fields = ['household__name']
    readonly_fields = ['emission_calculated', 'created_at']
    date_hierarchy = 'month_year'

@admin.register(DietEmission)
class DietEmissionAdmin(admin.ModelAdmin):
    list_display = ['household', 'diet_type', 'frequency', 'food_waste_percentage', 'month_year', 'emission_calculated']
    list_filter = ['diet_type', 'frequency', 'month_year']
    search_fields = ['household__name']
    readonly_fields = ['emission_calculated', 'created_at']
    date_hierarchy = 'month_year'

@admin.register(MonthlyEmissionSummary)
class MonthlyEmissionSummaryAdmin(admin.ModelAdmin):
    list_display = ['household', 'month_year', 'total_emissions', 'per_capita_emissions', 'updated_at']
    list_filter = ['month_year']
    search_fields = ['household__name']
    readonly_fields = ['total_energy_emissions', 'total_transport_emissions', 'total_diet_emissions', 
                      'total_emissions', 'per_capita_emissions', 'created_at', 'updated_at']
    date_hierarchy = 'month_year'

@admin.register(EcoTip)
class EcoTipAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'potential_reduction', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at']

@admin.register(FuelPrice)
class FuelPriceAdmin(admin.ModelAdmin):
    list_display = ['fuel_type', 'state', 'price', 'unit', 'date_recorded', 'source']
    list_filter = ['fuel_type', 'state', 'date_recorded']
    search_fields = ['state__name', 'source']
    date_hierarchy = 'date_recorded'
    readonly_fields = ['created_at']

@admin.register(UserGoal)
class UserGoalAdmin(admin.ModelAdmin):
    list_display = ['household', 'goal_type', 'target_reduction_percentage', 'target_date', 'is_active']
    list_filter = ['goal_type', 'is_active', 'target_date']
    search_fields = ['household__name']
    readonly_fields = ['created_at']
