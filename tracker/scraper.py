import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from django.conf import settings
import logging
from .models import FuelPrice, IndianState, EcoTip

logger = logging.getLogger('tracker')

class FuelPriceScraper:
    """Scraper for Indian fuel prices from various sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_petrol_diesel_prices(self):
        """Scrape petrol and diesel prices from multiple sources"""
        try:
            # Source 1: Sample structure for petrol/diesel prices
            # In real implementation, you would use actual Indian fuel price websites
            prices_data = []
            
            # Example structure - replace with actual scraping logic
            sample_data = [
                {'state': 'Delhi', 'petrol': 96.72, 'diesel': 89.62},
                {'state': 'Mumbai', 'petrol': 106.31, 'diesel': 94.27},
                {'state': 'Chennai', 'petrol': 102.63, 'diesel': 94.24},
                {'state': 'Kolkata', 'petrol': 106.03, 'diesel': 92.76},
                {'state': 'Bangalore', 'petrol': 101.94, 'diesel': 87.89},
                {'state': 'Hyderabad', 'petrol': 109.66, 'diesel': 97.82},
                {'state': 'Pune', 'petrol': 106.12, 'diesel': 92.17},
                {'state': 'Ahmedabad', 'petrol': 96.46, 'diesel': 92.56},
            ]
            
            for data in sample_data:
                try:
                    state, created = IndianState.objects.get_or_create(
                        name=data['state']
                    )
                    
                    # Create or update petrol price
                    FuelPrice.objects.update_or_create(
                        fuel_type='petrol',
                        state=state,
                        date_recorded=datetime.now().date(),
                        defaults={
                            'price': data['petrol'],
                            'unit': 'per litre',
                            'source': 'Web Scraping - Fuel Price Portal'
                        }
                    )
                    
                    # Create or update diesel price
                    FuelPrice.objects.update_or_create(
                        fuel_type='diesel',
                        state=state,
                        date_recorded=datetime.now().date(),
                        defaults={
                            'price': data['diesel'],
                            'unit': 'per litre',
                            'source': 'Web Scraping - Fuel Price Portal'
                        }
                    )
                    
                    prices_data.append(data)
                    
                except Exception as e:
                    logger.error(f"Error saving fuel price for {data['state']}: {e}")
            
            logger.info(f"Successfully scraped fuel prices for {len(prices_data)} states")
            return prices_data
            
        except Exception as e:
            logger.error(f"Error scraping fuel prices: {e}")
            return []
    
    def scrape_lpg_prices(self):
        """Scrape LPG cylinder prices"""
        try:
            # Sample LPG prices - replace with actual scraping
            lpg_prices = [
                {'state': 'Delhi', 'price': 819.00},
                {'state': 'Mumbai', 'price': 819.00},
                {'state': 'Chennai', 'price': 845.50},
                {'state': 'Kolkata', 'price': 845.00},
                {'state': 'Bangalore', 'price': 845.50},
                {'state': 'Hyderabad', 'price': 845.50},
            ]
            
            for data in lpg_prices:
                try:
                    state, created = IndianState.objects.get_or_create(
                        name=data['state']
                    )
                    
                    FuelPrice.objects.update_or_create(
                        fuel_type='lpg',
                        state=state,
                        date_recorded=datetime.now().date(),
                        defaults={
                            'price': data['price'],
                            'unit': 'per 14.2kg cylinder',
                            'source': 'Web Scraping - LPG Portal'
                        }
                    )
                    
                except Exception as e:
                    logger.error(f"Error saving LPG price for {data['state']}: {e}")
            
            logger.info(f"Successfully scraped LPG prices for {len(lpg_prices)} states")
            return lpg_prices
            
        except Exception as e:
            logger.error(f"Error scraping LPG prices: {e}")
            return []

    def scrape_electricity_rates(self):
        """Scrape electricity tariff rates"""
        try:
            # Sample electricity rates per kWh - replace with actual scraping
            electricity_rates = [
                {'state': 'Delhi', 'rate': 3.00},
                {'state': 'Mumbai', 'rate': 2.85},
                {'state': 'Chennai', 'rate': 3.50},
                {'state': 'Kolkata', 'rate': 4.50},
                {'state': 'Bangalore', 'rate': 4.85},
                {'state': 'Hyderabad', 'rate': 2.82},
            ]
            
            for data in electricity_rates:
                try:
                    state, created = IndianState.objects.get_or_create(
                        name=data['state']
                    )
                    
                    FuelPrice.objects.update_or_create(
                        fuel_type='electricity',
                        state=state,
                        date_recorded=datetime.now().date(),
                        defaults={
                            'price': data['rate'],
                            'unit': 'per kWh',
                            'source': 'Web Scraping - Electricity Board'
                        }
                    )
                    
                except Exception as e:
                    logger.error(f"Error saving electricity rate for {data['state']}: {e}")
            
            logger.info(f"Successfully scraped electricity rates for {len(electricity_rates)} states")
            return electricity_rates
            
        except Exception as e:
            logger.error(f"Error scraping electricity rates: {e}")
            return []

class EcoTipsScraper:
    """Scraper for eco-friendly tips and environmental news"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_energy_tips(self):
        """Scrape energy saving tips"""
        try:
            # Sample energy saving tips - in real implementation, scrape from environmental websites
            energy_tips = [
                {
                    'title': 'Switch to LED Bulbs',
                    'content': 'Replace all incandescent and CFL bulbs with LED bulbs. LEDs use up to 80% less energy and last 25 times longer than traditional incandescent bulbs.',
                    'potential_reduction': 15.0,
                    'source_url': 'https://example.com/energy-tips'
                },
                {
                    'title': 'Use Natural Light During Day',
                    'content': 'Open curtains and blinds during daylight hours to reduce dependency on artificial lighting. Position work areas near windows when possible.',
                    'potential_reduction': 8.0,
                    'source_url': 'https://example.com/natural-light'
                },
                {
                    'title': 'Unplug Electronics When Not in Use',
                    'content': 'Many electronics continue to draw power even when turned off. Unplug chargers, TVs, computers, and other devices when not in use.',
                    'potential_reduction': 12.0,
                    'source_url': 'https://example.com/phantom-load'
                },
                {
                    'title': 'Use Ceiling Fans with AC',
                    'content': 'Ceiling fans help circulate air, allowing you to set your AC 2-3 degrees higher while maintaining comfort. This can reduce AC energy consumption by 20-30%.',
                    'potential_reduction': 25.0,
                    'source_url': 'https://example.com/ceiling-fans'
                },
                {
                    'title': 'Maintain Your Appliances',
                    'content': 'Regular maintenance of AC filters, refrigerator coils, and other appliances ensures they operate efficiently and consume less energy.',
                    'potential_reduction': 10.0,
                    'source_url': 'https://example.com/appliance-maintenance'
                }
            ]
            
            saved_tips = []
            for tip_data in energy_tips:
                try:
                    tip, created = EcoTip.objects.get_or_create(
                        title=tip_data['title'],
                        defaults={
                            'content': tip_data['content'],
                            'category': 'energy',
                            'potential_reduction': tip_data['potential_reduction'],
                            'source_url': tip_data['source_url'],
                            'is_active': True
                        }
                    )
                    if created:
                        saved_tips.append(tip)
                except Exception as e:
                    logger.error(f"Error saving energy tip: {e}")
            
            logger.info(f"Successfully scraped {len(saved_tips)} energy tips")
            return saved_tips
            
        except Exception as e:
            logger.error(f"Error scraping energy tips: {e}")
            return []
    
    def scrape_transport_tips(self):
        """Scrape transportation tips"""
        try:
            transport_tips = [
                {
                    'title': 'Use Public Transportation',
                    'content': 'Buses, trains, and metro systems can significantly reduce your carbon footprint compared to private vehicles. One bus can replace 40 cars on the road.',
                    'potential_reduction': 50.0,
                    'source_url': 'https://example.com/public-transport'
                },
                {
                    'title': 'Carpool or Rideshare',
                    'content': 'Share rides with colleagues or friends for daily commutes. Carpooling can reduce individual transport emissions by 45% or more.',
                    'potential_reduction': 30.0,
                    'source_url': 'https://example.com/carpooling'
                },
                {
                    'title': 'Maintain Proper Tire Pressure',
                    'content': 'Under-inflated tires can reduce fuel efficiency by up to 10%. Check tire pressure monthly and maintain manufacturer recommended levels.',
                    'potential_reduction': 5.0,
                    'source_url': 'https://example.com/tire-pressure'
                },
                {
                    'title': 'Plan and Combine Trips',
                    'content': 'Combine multiple errands into one trip to reduce overall travel. Plan efficient routes to minimize distance traveled.',
                    'potential_reduction': 15.0,
                    'source_url': 'https://example.com/trip-planning'
                },
                {
                    'title': 'Consider Electric or Hybrid Vehicles',
                    'content': 'Electric vehicles produce zero direct emissions. Hybrid vehicles can reduce fuel consumption by 30-50% compared to conventional vehicles.',
                    'potential_reduction': 60.0,
                    'source_url': 'https://example.com/electric-vehicles'
                }
            ]
            
            saved_tips = []
            for tip_data in transport_tips:
                try:
                    tip, created = EcoTip.objects.get_or_create(
                        title=tip_data['title'],
                        defaults={
                            'content': tip_data['content'],
                            'category': 'transport',
                            'potential_reduction': tip_data['potential_reduction'],
                            'source_url': tip_data['source_url'],
                            'is_active': True
                        }
                    )
                    if created:
                        saved_tips.append(tip)
                except Exception as e:
                    logger.error(f"Error saving transport tip: {e}")
            
            logger.info(f"Successfully scraped {len(saved_tips)} transport tips")
            return saved_tips
            
        except Exception as e:
            logger.error(f"Error scraping transport tips: {e}")
            return []
    
    def scrape_diet_tips(self):
        """Scrape diet and food-related tips"""
        try:
            diet_tips = [
                {
                    'title': 'Reduce Meat Consumption',
                    'content': 'Livestock farming produces significant greenhouse gases. Reducing meat consumption by 2-3 days per week can substantially lower your carbon footprint.',
                    'potential_reduction': 20.0,
                    'source_url': 'https://example.com/reduce-meat'
                },
                {
                    'title': 'Buy Local and Seasonal Produce',
                    'content': 'Local and seasonal fruits and vegetables require less transportation and storage, reducing associated carbon emissions.',
                    'potential_reduction': 10.0,
                    'source_url': 'https://example.com/local-food'
                },
                {
                    'title': 'Minimize Food Waste',
                    'content': 'Plan meals, store food properly, and use leftovers creatively. Food waste in landfills produces methane, a potent greenhouse gas.',
                    'potential_reduction': 15.0,
                    'source_url': 'https://example.com/food-waste'
                },
                {
                    'title': 'Grow Your Own Herbs and Vegetables',
                    'content': 'Home gardening eliminates transportation emissions and packaging waste. Even small herb gardens can make a difference.',
                    'potential_reduction': 5.0,
                    'source_url': 'https://example.com/home-gardening'
                },
                {
                    'title': 'Choose Organic When Possible',
                    'content': 'Organic farming typically uses less energy-intensive methods and avoids synthetic fertilizers that require significant energy to produce.',
                    'potential_reduction': 8.0,
                    'source_url': 'https://example.com/organic-food'
                }
            ]
            
            saved_tips = []
            for tip_data in diet_tips:
                try:
                    tip, created = EcoTip.objects.get_or_create(
                        title=tip_data['title'],
                        defaults={
                            'content': tip_data['content'],
                            'category': 'diet',
                            'potential_reduction': tip_data['potential_reduction'],
                            'source_url': tip_data['source_url'],
                            'is_active': True
                        }
                    )
                    if created:
                        saved_tips.append(tip)
                except Exception as e:
                    logger.error(f"Error saving diet tip: {e}")
            
            logger.info(f"Successfully scraped {len(saved_tips)} diet tips")
            return saved_tips
            
        except Exception as e:
            logger.error(f"Error scraping diet tips: {e}")
            return []

def run_all_scrapers():
    """Run all scrapers to update data"""
    try:
        # Initialize scrapers
        fuel_scraper = FuelPriceScraper()
        tips_scraper = EcoTipsScraper()
        
        # Scrape fuel prices
        logger.info("Starting fuel price scraping...")
        fuel_scraper.scrape_petrol_diesel_prices()
        fuel_scraper.scrape_lpg_prices()
        fuel_scraper.scrape_electricity_rates()
        
        # Scrape eco tips
        logger.info("Starting eco tips scraping...")
        tips_scraper.scrape_energy_tips()
        tips_scraper.scrape_transport_tips()
        tips_scraper.scrape_diet_tips()
        
        logger.info("All scraping tasks completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error running scrapers: {e}")
        return False