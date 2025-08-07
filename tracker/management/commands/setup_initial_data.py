from django.core.management.base import BaseCommand
from django.db import transaction
from tracker.models import (
    IndianState, EmissionFactor, EcoTip
)
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Setup initial data for Carbon Footprint Tracker including Indian states, emission factors, and eco tips'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-tips',
            action='store_true',
            help='Skip loading eco tips',
        )
        parser.add_argument(
            '--skip-states',
            action='store_true',
            help='Skip loading Indian states',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌱 Setting up initial data for Carbon Footprint Tracker...'))
        
        try:
            with transaction.atomic():
                if not options['skip_states']:
                    self.create_indian_states()
                
                self.create_emission_factors()
                
                if not options['skip_tips']:
                    self.create_eco_tips()
                
                self.stdout.write(
                    self.style.SUCCESS('✅ Successfully setup initial data!')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error setting up data: {e}')
            )
            raise

    def create_indian_states(self):
        """Create Indian states with electricity emission factors"""
        states_data = [
            {'name': 'Andhra Pradesh', 'emission_factor': 0.79},
            {'name': 'Arunachal Pradesh', 'emission_factor': 0.65},
            {'name': 'Assam', 'emission_factor': 0.71},
            {'name': 'Bihar', 'emission_factor': 0.89},
            {'name': 'Chhattisgarh', 'emission_factor': 0.95},
            {'name': 'Delhi', 'emission_factor': 0.82},
            {'name': 'Goa', 'emission_factor': 0.76},
            {'name': 'Gujarat', 'emission_factor': 0.84},
            {'name': 'Haryana', 'emission_factor': 0.81},
            {'name': 'Himachal Pradesh', 'emission_factor': 0.45},
            {'name': 'Jharkhand', 'emission_factor': 0.92},
            {'name': 'Karnataka', 'emission_factor': 0.73},
            {'name': 'Kerala', 'emission_factor': 0.68},
            {'name': 'Madhya Pradesh', 'emission_factor': 0.88},
            {'name': 'Maharashtra', 'emission_factor': 0.77},
            {'name': 'Manipur', 'emission_factor': 0.69},
            {'name': 'Meghalaya', 'emission_factor': 0.72},
            {'name': 'Mizoram', 'emission_factor': 0.74},
            {'name': 'Nagaland', 'emission_factor': 0.73},
            {'name': 'Odisha', 'emission_factor': 0.91},
            {'name': 'Punjab', 'emission_factor': 0.78},
            {'name': 'Rajasthan', 'emission_factor': 0.85},
            {'name': 'Sikkim', 'emission_factor': 0.42},
            {'name': 'Tamil Nadu', 'emission_factor': 0.75},
            {'name': 'Telangana', 'emission_factor': 0.80},
            {'name': 'Tripura', 'emission_factor': 0.76},
            {'name': 'Uttar Pradesh', 'emission_factor': 0.86},
            {'name': 'Uttarakhand', 'emission_factor': 0.67},
            {'name': 'West Bengal', 'emission_factor': 0.87},
            # Union Territories
            {'name': 'Andaman and Nicobar Islands', 'emission_factor': 0.83},
            {'name': 'Chandigarh', 'emission_factor': 0.79},
            {'name': 'Dadra and Nagar Haveli and Daman and Diu', 'emission_factor': 0.81},
            {'name': 'Jammu and Kashmir', 'emission_factor': 0.58},
            {'name': 'Ladakh', 'emission_factor': 0.61},
            {'name': 'Lakshadweep', 'emission_factor': 0.85},
            {'name': 'Puducherry', 'emission_factor': 0.78},
        ]
        
        created_count = 0
        for state_data in states_data:
            state, created = IndianState.objects.get_or_create(
                name=state_data['name'],
                defaults={'electricity_emission_factor': state_data['emission_factor']}
            )
            if created:
                created_count += 1
        
        self.stdout.write(f'📍 Created {created_count} Indian states')

    def create_emission_factors(self):
        """Create emission factors for different categories"""
        factors_data = [
            # Energy emission factors (kg CO2 per unit)
            {'category': 'energy', 'name': 'Electricity', 'unit': 'kWh', 'factor': 0.82, 'source': 'Central Electricity Authority, India'},
            {'category': 'energy', 'name': 'LPG', 'unit': 'kg', 'factor': 2.98, 'source': 'Ministry of Petroleum, India'},
            {'category': 'energy', 'name': 'CNG', 'unit': 'kg', 'factor': 2.75, 'source': 'IGL India'},
            {'category': 'energy', 'name': 'Kerosene', 'unit': 'litre', 'factor': 2.52, 'source': 'IPCC Guidelines'},
            {'category': 'energy', 'name': 'Wood', 'unit': 'kg', 'factor': 1.87, 'source': 'Forest Survey of India'},
            {'category': 'energy', 'name': 'Coal', 'unit': 'kg', 'factor': 2.42, 'source': 'Coal India Limited'},
            {'category': 'energy', 'name': 'Solar', 'unit': 'kWh', 'factor': 0.05, 'source': 'MNRE India'},
            
            # Transport emission factors (kg CO2 per km)
            {'category': 'transport', 'name': 'Bike', 'unit': 'km', 'factor': 0.06, 'source': 'ARAI India'},
            {'category': 'transport', 'name': 'Car Petrol', 'unit': 'km', 'factor': 0.17, 'source': 'ARAI India'},
            {'category': 'transport', 'name': 'Car Diesel', 'unit': 'km', 'factor': 0.16, 'source': 'ARAI India'},
            {'category': 'transport', 'name': 'Car CNG', 'unit': 'km', 'factor': 0.14, 'source': 'ARAI India'},
            {'category': 'transport', 'name': 'Auto', 'unit': 'km', 'factor': 0.08, 'source': 'ARAI India'},
            {'category': 'transport', 'name': 'Bus', 'unit': 'km', 'factor': 0.04, 'source': 'Indian Railways'},
            {'category': 'transport', 'name': 'Train', 'unit': 'km', 'factor': 0.03, 'source': 'Indian Railways'},
            {'category': 'transport', 'name': 'Metro', 'unit': 'km', 'factor': 0.02, 'source': 'Delhi Metro'},
            {'category': 'transport', 'name': 'Flight Domestic', 'unit': 'km', 'factor': 0.18, 'source': 'DGCA India'},
            {'category': 'transport', 'name': 'Flight International', 'unit': 'km', 'factor': 0.20, 'source': 'ICAO'},
            
            # Diet emission factors (kg CO2 per kg of food)
            {'category': 'diet', 'name': 'Rice', 'unit': 'kg', 'factor': 4.5, 'source': 'Indian Agricultural Research'},
            {'category': 'diet', 'name': 'Wheat', 'unit': 'kg', 'factor': 1.2, 'source': 'Indian Agricultural Research'},
            {'category': 'diet', 'name': 'Lentils', 'unit': 'kg', 'factor': 0.9, 'source': 'Indian Agricultural Research'},
            {'category': 'diet', 'name': 'Chicken', 'unit': 'kg', 'factor': 6.1, 'source': 'Livestock Emission Study India'},
            {'category': 'diet', 'name': 'Mutton', 'unit': 'kg', 'factor': 39.2, 'source': 'Livestock Emission Study India'},
            {'category': 'diet', 'name': 'Fish', 'unit': 'kg', 'factor': 5.4, 'source': 'Marine Fisheries India'},
            {'category': 'diet', 'name': 'Milk', 'unit': 'litre', 'factor': 3.2, 'source': 'National Dairy Development Board'},
            {'category': 'diet', 'name': 'Vegetables', 'unit': 'kg', 'factor': 0.4, 'source': 'Indian Agricultural Research'},
            {'category': 'diet', 'name': 'Fruits', 'unit': 'kg', 'factor': 0.5, 'source': 'Indian Agricultural Research'},
        ]
        
        created_count = 0
        for factor_data in factors_data:
            factor, created = EmissionFactor.objects.get_or_create(
                category=factor_data['category'],
                name=factor_data['name'],
                defaults={
                    'unit': factor_data['unit'],
                    'emission_factor': factor_data['factor'],
                    'source': factor_data['source'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1
        
        self.stdout.write(f'⚡ Created {created_count} emission factors')

    def create_eco_tips(self):
        """Create eco-friendly tips"""
        tips_data = [
            # Energy Tips
            {
                'title': 'Switch to LED Bulbs',
                'content': 'Replace all incandescent and CFL bulbs with LED bulbs. LEDs use up to 80% less energy and last 25 times longer than traditional incandescent bulbs. For an average Indian household, this can save ₹2,000-3,000 annually on electricity bills.',
                'category': 'energy',
                'potential_reduction': 15.0,
                'source_url': 'https://beeindia.gov.in/content/led-programme'
            },
            {
                'title': 'Use Natural Light During Day',
                'content': 'Open curtains and blinds during daylight hours to reduce dependency on artificial lighting. Position work areas near windows when possible. In Indian homes, proper use of natural light can reduce electricity consumption by 10-15%.',
                'category': 'energy',
                'potential_reduction': 8.0,
                'source_url': 'https://beeindia.gov.in/content/energy-conservation'
            },
            {
                'title': 'Optimize Air Conditioner Usage',
                'content': 'Set AC temperature to 24°C or higher. Use ceiling fans with AC to circulate air better. Clean AC filters monthly for optimal efficiency. In hot Indian summers, this can reduce cooling costs by 20-30%.',
                'category': 'energy',
                'potential_reduction': 25.0,
                'source_url': 'https://beeindia.gov.in/content/room-air-conditioner'
            },
            {
                'title': 'Unplug Electronics When Not in Use',
                'content': 'Many electronics continue to draw power even when turned off (phantom load). Unplug chargers, TVs, computers, and other devices when not in use. This can save 5-10% on your electricity bill.',
                'category': 'energy',
                'potential_reduction': 12.0,
                'source_url': 'https://beeindia.gov.in/content/standby-power-loss'
            },
            
            # Transport Tips
            {
                'title': 'Use Public Transportation',
                'content': 'Buses, trains, and metro systems can significantly reduce your carbon footprint compared to private vehicles. One bus can replace 40 cars on the road. In cities like Delhi and Mumbai, metro and buses are efficient alternatives.',
                'category': 'transport',
                'potential_reduction': 50.0,
                'source_url': 'https://www.indianrailways.gov.in/railwayboard/view_section.jsp?lang=0&id=0,1,304,366,537'
            },
            {
                'title': 'Carpool or Rideshare',
                'content': 'Share rides with colleagues or friends for daily commutes. Carpooling can reduce individual transport emissions by 45% or more. Use apps like BlaBlaCar or organize carpools in your office/society.',
                'category': 'transport',
                'potential_reduction': 30.0,
                'source_url': 'https://www.mohua.gov.in/cms/smart-cities-mission.php'
            },
            {
                'title': 'Maintain Proper Tire Pressure',
                'content': 'Under-inflated tires can reduce fuel efficiency by up to 10%. Check tire pressure monthly and maintain manufacturer recommended levels. This simple step can improve your vehicle\'s mileage significantly.',
                'category': 'transport',
                'potential_reduction': 5.0,
                'source_url': 'https://www.arai.in/energy-environment'
            },
            {
                'title': 'Plan and Combine Trips',
                'content': 'Combine multiple errands into one trip to reduce overall travel. Plan efficient routes to minimize distance traveled. This is especially effective in Indian cities with heavy traffic.',
                'category': 'transport',
                'potential_reduction': 15.0,
                'source_url': 'https://www.mohua.gov.in/cms/sustainable-urban-transport.php'
            },
            
            # Diet Tips
            {
                'title': 'Reduce Meat Consumption',
                'content': 'Livestock farming produces significant greenhouse gases. Try "Meatless Monday" or reduce meat consumption by 2-3 days per week. Traditional Indian vegetarian cuisine offers diverse, nutritious alternatives.',
                'category': 'diet',
                'potential_reduction': 20.0,
                'source_url': 'https://www.fao.org/livestock-environment/en/'
            },
            {
                'title': 'Buy Local and Seasonal Produce',
                'content': 'Local and seasonal fruits and vegetables require less transportation and storage, reducing associated carbon emissions. Visit local mandis and farmers\' markets for fresh, seasonal produce.',
                'category': 'diet',
                'potential_reduction': 10.0,
                'source_url': 'https://www.nfdb.com/'
            },
            {
                'title': 'Minimize Food Waste',
                'content': 'Plan meals, store food properly using traditional Indian methods, and use leftovers creatively. Food waste in landfills produces methane, a potent greenhouse gas. In India, 40% of food is wasted.',
                'category': 'diet',
                'potential_reduction': 15.0,
                'source_url': 'https://www.fssai.gov.in/cms/food-waste.php'
            },
            {
                'title': 'Grow Your Own Herbs and Vegetables',
                'content': 'Start a kitchen garden with herbs like mint, coriander, and curry leaves. Even small balcony gardens can make a difference. Home gardening eliminates transportation emissions and packaging waste.',
                'category': 'diet',
                'potential_reduction': 5.0,
                'source_url': 'https://mkisan.gov.in/home-gardening'
            },
            
            # General Tips
            {
                'title': 'Reduce, Reuse, Recycle',
                'content': 'Follow the 3 Rs principle. Reduce consumption, reuse items creatively, and recycle materials properly. India generates 62 million tonnes of waste annually - proper waste management is crucial.',
                'category': 'general',
                'potential_reduction': 18.0,
                'source_url': 'https://www.swachhbharatmission.gov.in/'
            },
            {
                'title': 'Use Water Efficiently',
                'content': 'Fix leaky taps, use water-saving fixtures, and harvest rainwater. Water heating and pumping consume significant energy. Traditional Indian water conservation methods like storing water in clay pots are also effective.',
                'category': 'general',
                'potential_reduction': 8.0,
                'source_url': 'https://jalshakti-dowr.gov.in/schemes/rainwater-harvesting'
            }
        ]
        
        created_count = 0
        for tip_data in tips_data:
            tip, created = EcoTip.objects.get_or_create(
                title=tip_data['title'],
                defaults={
                    'content': tip_data['content'],
                    'category': tip_data['category'],
                    'potential_reduction': tip_data['potential_reduction'],
                    'source_url': tip_data['source_url'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1
        
        self.stdout.write(f'💡 Created {created_count} eco tips')