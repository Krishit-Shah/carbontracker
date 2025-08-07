# 🌱 Carbon Footprint Tracker for Indian Households

A comprehensive Django web application designed specifically for Indian households to track, analyze, and reduce their carbon footprint. Built with Bootstrap 5, Chart.js, and featuring India-specific emission factors and data sources.

## 🇮🇳 India-Centric Features

- **Local Emission Factors**: Uses India-specific emission factors for electricity, fuels, and food
- **Indian Fuel Prices**: Real-time scraping of petrol, diesel, LPG, and electricity prices by state
- **Indian Diet Analysis**: Tailored for Indian cuisine patterns (vegetarian, non-vegetarian, regional variations)
- **Multi-language Support**: Ready for Hindi and regional language integration
- **Indian Currency**: All pricing in Indian Rupees (₹)
- **State-wise Data**: Supports all Indian states with location-specific calculations

## ✨ Key Features

### 📊 Comprehensive Tracking
- **Energy Usage**: Electricity, LPG, CNG, Kerosene, Wood/Biomass, Coal, Solar
- **Transportation**: All modes from bicycles to international flights
- **Diet & Food**: Indian diet patterns with food waste tracking
- **Emission Calculations**: Automatic CO₂ calculations with Indian emission factors

### 🎨 Modern UI/UX
- **Bootstrap 5**: Responsive, mobile-first design
- **Indian Theme**: Saffron, green, and white color scheme
- **Interactive Charts**: Chart.js visualizations with emission breakdowns
- **Dark/Light Mode**: User preference support (planned)

### 🔧 Technical Features
- **Django 4.2+**: Modern Python web framework
- **REST API**: Full API access for mobile apps and integrations
- **Web Scraping**: BeautifulSoup integration for real-time price data
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Authentication**: Django's built-in user system with household profiles

### 📈 Analytics & Insights
- **Monthly Trends**: Track emission changes over time
- **Category Breakdown**: Detailed analysis by energy, transport, and diet
- **National Comparisons**: Compare with Indian national averages
- **Goal Setting**: Personal reduction targets and progress tracking
- **Eco Tips**: Curated suggestions for reducing carbon footprint

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ installed
- pip package manager
- Git (for cloning)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd carbontrack
```

2. **Create virtual environment**
```bash
python3 -m venv carbon_env
source carbon_env/bin/activate  # On Windows: carbon_env\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup database**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create superuser (optional)**
```bash
python manage.py createsuperuser
```

6. **Load initial data**
```bash
python manage.py shell
>>> from tracker.scraper import run_all_scrapers
>>> run_all_scrapers()  # Load sample fuel prices and eco tips
>>> exit()
```

7. **Run development server**
```bash
python manage.py runserver
```

8. **Access the application**
   - Main app: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/
   - API docs: http://127.0.0.1:8000/api/

## 📱 Usage Guide

### Getting Started
1. **Register**: Create a new account on the homepage
2. **Setup Household**: Complete your family profile with location and member count
3. **Start Tracking**: Begin adding your energy, transport, and diet data
4. **View Dashboard**: Monitor your emissions and progress

### Adding Data

#### Energy Usage
- Go to "Add Data" → "Energy Usage"
- Select energy source (electricity, LPG, etc.)
- Enter consumption amount and period
- System automatically calculates CO₂ emissions

#### Transportation
- Select transport mode (bike, car, bus, train, flight)
- Enter distance and frequency
- Add fuel costs if available
- Get emission breakdown by transport type

#### Diet & Food
- Choose your diet pattern (vegan, vegetarian, non-veg)
- Set frequency of different food types
- Estimate food waste percentage
- See impact of dietary choices

### Viewing Reports
- **Dashboard**: Current month overview with trends
- **Reports**: Detailed yearly analysis and comparisons
- **Charts**: Interactive visualizations of your data
- **Tips**: Personalized recommendations for reduction

## 🛠️ Development

### Project Structure
```
carbontrack/
├── carbontrack/          # Django project settings
├── tracker/              # Main application
│   ├── models.py        # Database models
│   ├── views.py         # View logic
│   ├── serializers.py   # API serializers
│   ├── scraper.py       # Web scraping functionality
│   └── admin.py         # Admin interface
├── templates/           # HTML templates
│   ├── base.html       # Base template
│   └── tracker/        # App-specific templates
├── static/             # Static files
│   ├── css/           # Stylesheets
│   ├── js/            # JavaScript
│   └── img/           # Images
├── requirements.txt    # Python dependencies
└── manage.py          # Django management script
```

### Key Models
- **Household**: User family/household information
- **EnergyUsage**: Energy consumption tracking
- **TransportUsage**: Transportation emission data
- **DietEmission**: Food-related emissions
- **MonthlyEmissionSummary**: Aggregated monthly data
- **EcoTip**: Environmental tips and suggestions
- **FuelPrice**: Current fuel prices by state

### API Endpoints
```
/api/households/              # Household management
/api/energy-usage/            # Energy data CRUD
/api/transport-usage/         # Transport data CRUD
/api/diet-emissions/          # Diet data CRUD
/api/monthly-summaries/       # Emission summaries
/api/eco-tips/               # Environmental tips
/api/update-data/            # Trigger data scraping
```

### Customization

#### Adding New Emission Factors
```python
# In Django shell or data migration
from tracker.models import EmissionFactor

EmissionFactor.objects.create(
    category='energy',
    name='Solar Panel',
    unit='kWh',
    emission_factor=0.05,  # kg CO2 per kWh
    source='Renewable Energy Agency'
)
```

#### Modifying Calculations
Edit the `calculate_emissions()` methods in models.py for each category:
- `EnergyUsage.calculate_emissions()`
- `TransportUsage.calculate_emissions()`
- `DietEmission.calculate_emissions()`

#### Adding New States
```python
from tracker.models import IndianState

IndianState.objects.create(
    name='Goa',
    electricity_emission_factor=0.78  # kg CO2/kWh
)
```

## 🌐 Deployment

### Production Setup

1. **Environment Variables**
```bash
export DEBUG=False
export SECRET_KEY='your-secret-key'
export DATABASE_URL='postgresql://user:password@host:port/dbname'
export ALLOWED_HOSTS='yourdomain.com,www.yourdomain.com'
```

2. **Database (PostgreSQL)**
```bash
pip install psycopg2-binary
# Update DATABASES in settings.py
python manage.py migrate
```

3. **Static Files**
```bash
python manage.py collectstatic
```

4. **Web Server (Nginx + Gunicorn)**
```bash
pip install gunicorn
gunicorn carbontrack.wsgi:application --bind 0.0.0.0:8000
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "carbontrack.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Heroku Deployment
1. Create `Procfile`:
```
web: gunicorn carbontrack.wsgi:application
release: python manage.py migrate
```

2. Update `requirements.txt` with production dependencies
3. Configure environment variables in Heroku dashboard
4. Deploy using Git or Heroku CLI

## 🔧 Configuration

### Settings Options
```python
# Custom settings in carbontrack/settings.py

# Carbon footprint specific settings
CARBON_FOOTPRINT_SETTINGS = {
    'DEFAULT_EMISSION_FACTORS': {
        'electricity': 0.82,  # kg CO2/kWh for India
        'lpg': 2.98,          # kg CO2/kg
        'petrol': 2.31,       # kg CO2/litre
        'diesel': 2.68,       # kg CO2/litre
    },
    'AVERAGE_INDIAN_EMISSIONS': {
        'per_capita_yearly': 1900,  # kg CO2 per person per year
        'household_monthly': 300,   # kg CO2 per household per month
    }
}

# Celery for background tasks (optional)
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
```

### Web Scraping Configuration
The app includes BeautifulSoup-based scrapers for:
- Fuel prices from Indian petroleum websites
- Eco tips from environmental websites
- Electricity tariffs from state electricity boards

To run scrapers manually:
```python
from tracker.scraper import run_all_scrapers
run_all_scrapers()
```

## 🧪 Testing

### Run Tests
```bash
python manage.py test
```

### Test Coverage
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

### Sample Data for Testing
```python
# In Django shell
from django.contrib.auth.models import User
from tracker.models import Household, IndianState

# Create test user and household
user = User.objects.create_user('testuser', 'test@example.com', 'password')
state = IndianState.objects.create(name='Delhi', electricity_emission_factor=0.82)
household = Household.objects.create(
    user=user,
    name='Test Family',
    house_type='apartment',
    members_count=4,
    state=state,
    city='New Delhi'
)
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly
4. Commit changes: `git commit -m "Add feature"`
5. Push to branch: `git push origin feature-name`
6. Create a Pull Request

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings for all functions and classes
- Write tests for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Indian Government**: For emission factor data and environmental policies
- **Bootstrap Team**: For the excellent CSS framework
- **Chart.js**: For beautiful, responsive charts
- **Django Community**: For the robust web framework
- **Environmental Organizations**: For guidance on carbon footprint calculations

## 📞 Support

- **Issues**: Report bugs and request features on GitHub Issues
- **Email**: contact@ecotrack-india.com
- **Documentation**: Full API docs available at `/api/`
- **Community**: Join our Discord server for discussions

## 🗺️ Roadmap

### Upcoming Features
- [ ] Mobile app (React Native)
- [ ] Hindi and regional language support
- [ ] Advanced analytics with ML predictions
- [ ] Community challenges and leaderboards
- [ ] Integration with smart home devices
- [ ] Carbon offset marketplace
- [ ] Export data to PDF reports
- [ ] Social sharing of achievements

### Version History
- **v1.0.0**: Initial release with core tracking features
- **v1.1.0**: Web scraping and real-time price updates
- **v1.2.0**: Advanced visualizations and comparisons
- **v2.0.0**: Mobile app and API v2 (planned)

---

**Made with ❤️ in India for a sustainable future 🌍**

*Contribute to reducing India's carbon footprint, one household at a time.*
