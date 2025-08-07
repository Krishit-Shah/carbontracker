from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

class IndianState(models.Model):
    """Indian states for location-based calculations"""
    name = models.CharField(max_length=100, unique=True)
    electricity_emission_factor = models.FloatField(default=0.82)  # kg CO2/kWh
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Household(models.Model):
    """Household information for users"""
    HOUSE_TYPES = [
        ('apartment', 'Apartment'),
        ('independent', 'Independent House'),
        ('villa', 'Villa'),
        ('other', 'Other'),
    ]
    
    INCOME_RANGES = [
        ('below_2lakh', 'Below ₹2 Lakh'),
        ('2_5lakh', '₹2-5 Lakh'),
        ('5_10lakh', '₹5-10 Lakh'),
        ('10_25lakh', '₹10-25 Lakh'),
        ('above_25lakh', 'Above ₹25 Lakh'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='household')
    name = models.CharField(max_length=200, help_text="Household/Family name")
    house_type = models.CharField(max_length=20, choices=HOUSE_TYPES, default='apartment')
    members_count = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(20)])
    state = models.ForeignKey(IndianState, on_delete=models.SET_NULL, null=True, blank=True)
    city = models.CharField(max_length=100)
    income_range = models.CharField(max_length=20, choices=INCOME_RANGES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"

class EmissionFactor(models.Model):
    """Emission factors for different activities and fuels"""
    CATEGORIES = [
        ('energy', 'Energy'),
        ('transport', 'Transport'),
        ('diet', 'Diet'),
        ('waste', 'Waste'),
    ]
    
    category = models.CharField(max_length=20, choices=CATEGORIES)
    name = models.CharField(max_length=100)  # e.g., "Petrol", "Electricity", "Beef"
    unit = models.CharField(max_length=20)   # e.g., "litre", "kWh", "kg"
    emission_factor = models.FloatField(help_text="kg CO2 per unit")
    source = models.CharField(max_length=200, blank=True, help_text="Data source")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.emission_factor} kg CO2/{self.unit})"
    
    class Meta:
        unique_together = ['category', 'name']

class EnergyUsage(models.Model):
    """Track household energy consumption"""
    ENERGY_SOURCES = [
        ('electricity', 'Electricity'),
        ('lpg', 'LPG'),
        ('cng', 'CNG'),
        ('kerosene', 'Kerosene'),
        ('wood', 'Wood/Biomass'),
        ('coal', 'Coal'),
        ('solar', 'Solar Energy'),
    ]
    
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='energy_usage')
    energy_source = models.CharField(max_length=20, choices=ENERGY_SOURCES)
    consumption = models.FloatField(validators=[MinValueValidator(0)])
    unit = models.CharField(max_length=10)  # kWh, kg, litre
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    month_year = models.DateField(help_text="Month and year of consumption")
    emission_calculated = models.FloatField(null=True, blank=True, help_text="kg CO2")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def calculate_emissions(self):
        """Calculate CO2 emissions for this energy usage"""
        try:
            factor = EmissionFactor.objects.get(
                category='energy', 
                name__icontains=self.energy_source,
                is_active=True
            )
            self.emission_calculated = self.consumption * factor.emission_factor
            return self.emission_calculated
        except EmissionFactor.DoesNotExist:
            return 0
    
    def save(self, *args, **kwargs):
        if not self.emission_calculated:
            self.calculate_emissions()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.household.name} - {self.energy_source} ({self.month_year})"
    
    class Meta:
        unique_together = ['household', 'energy_source', 'month_year']

class TransportUsage(models.Model):
    """Track transportation and travel emissions"""
    TRANSPORT_MODES = [
        ('bike', 'Motorcycle/Scooter'),
        ('car_petrol', 'Car (Petrol)'),
        ('car_diesel', 'Car (Diesel)'),
        ('car_cng', 'Car (CNG)'),
        ('auto', 'Auto-rickshaw'),
        ('bus', 'Bus'),
        ('train', 'Train'),
        ('metro', 'Metro'),
        ('flight_domestic', 'Domestic Flight'),
        ('flight_international', 'International Flight'),
        ('walking', 'Walking'),
        ('cycling', 'Bicycle'),
    ]
    
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='transport_usage')
    transport_mode = models.CharField(max_length=25, choices=TRANSPORT_MODES)
    distance_km = models.FloatField(validators=[MinValueValidator(0)])
    frequency_per_month = models.PositiveIntegerField(default=1)
    fuel_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    month_year = models.DateField()
    emission_calculated = models.FloatField(null=True, blank=True, help_text="kg CO2")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def calculate_emissions(self):
        """Calculate CO2 emissions for transportation"""
        try:
            factor = EmissionFactor.objects.get(
                category='transport',
                name__icontains=self.transport_mode.split('_')[0],
                is_active=True
            )
            total_distance = self.distance_km * self.frequency_per_month
            self.emission_calculated = total_distance * factor.emission_factor
            return self.emission_calculated
        except EmissionFactor.DoesNotExist:
            return 0
    
    def save(self, *args, **kwargs):
        if not self.emission_calculated:
            self.calculate_emissions()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.household.name} - {self.transport_mode} ({self.month_year})"

class DietEmission(models.Model):
    """Track diet-based emissions"""
    DIET_TYPES = [
        ('vegan', 'Vegan'),
        ('vegetarian', 'Vegetarian'),
        ('eggetarian', 'Eggetarian'),
        ('pescatarian', 'Pescatarian'),
        ('chicken', 'Non-veg (Chicken)'),
        ('mutton', 'Non-veg (Mutton/Goat)'),
        ('mixed', 'Mixed Diet'),
    ]
    
    MEAL_FREQUENCIES = [
        ('daily', 'Daily'),
        ('weekly', '2-3 times per week'),
        ('monthly', 'Few times per month'),
        ('rarely', 'Rarely'),
    ]
    
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='diet_emissions')
    diet_type = models.CharField(max_length=20, choices=DIET_TYPES)
    frequency = models.CharField(max_length=10, choices=MEAL_FREQUENCIES)
    food_waste_percentage = models.FloatField(
        default=10.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Estimated food waste percentage"
    )
    month_year = models.DateField()
    emission_calculated = models.FloatField(null=True, blank=True, help_text="kg CO2")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def calculate_emissions(self):
        """Calculate CO2 emissions for diet"""
        # Base emissions per person per month (kg CO2)
        diet_emissions = {
            'vegan': 30,
            'vegetarian': 45,
            'eggetarian': 60,
            'pescatarian': 75,
            'chicken': 90,
            'mutton': 120,
            'mixed': 100,
        }
        
        frequency_multiplier = {
            'daily': 1.0,
            'weekly': 0.5,
            'monthly': 0.2,
            'rarely': 0.1,
        }
        
        base_emission = diet_emissions.get(self.diet_type, 50)
        freq_mult = frequency_multiplier.get(self.frequency, 1.0)
        waste_mult = 1 + (self.food_waste_percentage / 100)
        
        self.emission_calculated = base_emission * freq_mult * waste_mult * self.household.members_count
        return self.emission_calculated
    
    def save(self, *args, **kwargs):
        if not self.emission_calculated:
            self.calculate_emissions()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.household.name} - {self.diet_type} ({self.month_year})"

class MonthlyEmissionSummary(models.Model):
    """Monthly summary of all emissions for a household"""
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='monthly_summaries')
    month_year = models.DateField()
    total_energy_emissions = models.FloatField(default=0)
    total_transport_emissions = models.FloatField(default=0)
    total_diet_emissions = models.FloatField(default=0)
    total_emissions = models.FloatField(default=0)
    per_capita_emissions = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_totals(self):
        """Calculate total emissions for the month"""
        # Energy emissions
        energy_total = self.household.energy_usage.filter(
            month_year=self.month_year
        ).aggregate(
            total=models.Sum('emission_calculated')
        )['total'] or 0
        
        # Transport emissions
        transport_total = self.household.transport_usage.filter(
            month_year=self.month_year
        ).aggregate(
            total=models.Sum('emission_calculated')
        )['total'] or 0
        
        # Diet emissions
        diet_total = self.household.diet_emissions.filter(
            month_year=self.month_year
        ).aggregate(
            total=models.Sum('emission_calculated')
        )['total'] or 0
        
        self.total_energy_emissions = energy_total
        self.total_transport_emissions = transport_total
        self.total_diet_emissions = diet_total
        self.total_emissions = energy_total + transport_total + diet_total
        self.per_capita_emissions = self.total_emissions / self.household.members_count if self.household.members_count > 0 else 0
        
        return self.total_emissions
    
    def save(self, *args, **kwargs):
        self.calculate_totals()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.household.name} - {self.month_year} ({self.total_emissions:.2f} kg CO2)"
    
    class Meta:
        unique_together = ['household', 'month_year']
        ordering = ['-month_year']

class EcoTip(models.Model):
    """Eco-friendly tips and suggestions"""
    CATEGORIES = [
        ('energy', 'Energy Saving'),
        ('transport', 'Transportation'),
        ('diet', 'Diet & Food'),
        ('waste', 'Waste Management'),
        ('general', 'General'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORIES)
    potential_reduction = models.FloatField(
        help_text="Potential CO2 reduction per month (kg)",
        null=True, blank=True
    )
    is_active = models.BooleanField(default=True)
    source_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']

class FuelPrice(models.Model):
    """Track current fuel and energy prices in India"""
    FUEL_TYPES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('lpg', 'LPG'),
        ('cng', 'CNG'),
        ('electricity', 'Electricity'),
    ]
    
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPES)
    state = models.ForeignKey(IndianState, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    unit = models.CharField(max_length=20)  # per litre, per kWh, etc.
    date_recorded = models.DateField(default=timezone.now)
    source = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.fuel_type} - {self.state.name} (₹{self.price}/{self.unit})"
    
    class Meta:
        unique_together = ['fuel_type', 'state', 'date_recorded']
        ordering = ['-date_recorded']

class UserGoal(models.Model):
    """User-defined emission reduction goals"""
    GOAL_TYPES = [
        ('monthly', 'Monthly Reduction'),
        ('yearly', 'Yearly Reduction'),
        ('per_capita', 'Per Capita Target'),
    ]
    
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='goals')
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPES)
    target_reduction_percentage = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    baseline_emissions = models.FloatField(help_text="Baseline emissions in kg CO2")
    target_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def current_progress(self):
        """Calculate current progress towards goal"""
        # This would calculate actual progress based on recent emissions
        # Implementation would depend on the goal type and timeframe
        pass
    
    def __str__(self):
        return f"{self.household.name} - {self.goal_type} ({self.target_reduction_percentage}%)"
