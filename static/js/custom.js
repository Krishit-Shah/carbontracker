// Custom JavaScript for Carbon Footprint Tracker

// Initialize tooltips and popovers
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-dismiss alerts
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            if (alert.classList.contains('alert-success')) {
                const bsAlert = new bootstrap.Alert(alert);
                setTimeout(() => bsAlert.close(), 5000);
            }
        });
    }, 100);

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add loading spinner to form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Processing...';
                submitBtn.disabled = true;
                
                // Re-enable button after 10 seconds as a failsafe
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 10000);
            }
        });
    });
});

// Utility Functions
const CarbonTracker = {
    // Format numbers with proper Indian number formatting
    formatNumber: function(num, decimals = 1) {
        if (num === null || num === undefined) return '0';
        return parseFloat(num).toLocaleString('en-IN', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
    },

    // Convert kg to tons for large numbers
    formatEmissions: function(kg) {
        if (kg >= 1000) {
            return this.formatNumber(kg / 1000, 2) + ' tons CO₂';
        }
        return this.formatNumber(kg, 1) + ' kg CO₂';
    },

    // Calculate percentage with proper formatting
    calculatePercentage: function(value, total) {
        if (!total || total === 0) return 0;
        return Math.round((value / total) * 100);
    },

    // Get trend direction icon
    getTrendIcon: function(change) {
        if (change > 0) return 'bi-arrow-up text-danger';
        if (change < 0) return 'bi-arrow-down text-success';
        return 'bi-dash text-muted';
    },

    // Format currency in Indian Rupees
    formatCurrency: function(amount) {
        return '₹' + this.formatNumber(amount, 0);
    },

    // Animate counter numbers
    animateCounter: function(element, endValue, duration = 2000) {
        const startValue = 0;
        const increment = endValue / (duration / 16);
        let currentValue = startValue;

        const timer = setInterval(() => {
            currentValue += increment;
            if (currentValue >= endValue) {
                element.textContent = this.formatNumber(endValue);
                clearInterval(timer);
            } else {
                element.textContent = this.formatNumber(currentValue);
            }
        }, 16);
    },

    // Show loading spinner
    showLoading: function(element) {
        element.innerHTML = '<div class="loading-spinner"></div>';
    },

    // Hide loading spinner
    hideLoading: function(element) {
        const spinner = element.querySelector('.loading-spinner');
        if (spinner) {
            spinner.remove();
        }
    },

    // Show toast notification
    showToast: function(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container') || this.createToastContainer();
        
        const toastEl = document.createElement('div');
        toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');
        
        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toastEl);
        const toast = new bootstrap.Toast(toastEl);
        toast.show();
        
        // Remove element after it's hidden
        toastEl.addEventListener('hidden.bs.toast', function() {
            toastEl.remove();
        });
    },

    // Create toast container if it doesn't exist
    createToastContainer: function() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '1055';
        document.body.appendChild(container);
        return container;
    },

    // Validate form inputs
    validateForm: function(form) {
        let isValid = true;
        const inputs = form.querySelectorAll('input[required], select[required]');
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    },

    // Debounce function for search inputs
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Local storage helpers
    storage: {
        set: function(key, value) {
            try {
                localStorage.setItem(key, JSON.stringify(value));
            } catch (e) {
                console.warn('LocalStorage not available');
            }
        },
        
        get: function(key) {
            try {
                const item = localStorage.getItem(key);
                return item ? JSON.parse(item) : null;
            } catch (e) {
                console.warn('LocalStorage not available');
                return null;
            }
        },
        
        remove: function(key) {
            try {
                localStorage.removeItem(key);
            } catch (e) {
                console.warn('LocalStorage not available');
            }
        }
    },

    // API helper functions
    api: {
        get: function(url) {
            return fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            }).then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            });
        },

        post: function(url, data) {
            return fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(data)
            }).then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            });
        },

        getCSRFToken: function() {
            const token = document.querySelector('[name=csrfmiddlewaretoken]');
            return token ? token.value : '';
        }
    }
};

// Chart color schemes for consistency
const ChartColors = {
    energy: {
        background: 'rgba(255, 153, 51, 0.1)',
        border: '#FF9933'
    },
    transport: {
        background: 'rgba(139, 69, 19, 0.1)',
        border: '#8B4513'
    },
    diet: {
        background: 'rgba(19, 136, 8, 0.1)',
        border: '#138808'
    },
    total: {
        background: 'rgba(34, 139, 34, 0.1)',
        border: '#228B22'
    }
};

// Form helpers for data entry pages
const FormHelpers = {
    // Auto-calculate emissions preview
    setupEmissionPreview: function(form, category) {
        const inputs = form.querySelectorAll('input[type="number"]');
        inputs.forEach(input => {
            input.addEventListener('input', CarbonTracker.debounce(() => {
                this.updateEmissionPreview(form, category);
            }, 500));
        });
    },

    updateEmissionPreview: function(form, category) {
        const previewElement = form.querySelector('.emission-preview');
        if (!previewElement) return;

        // Basic emission calculation (simplified)
        let emissions = 0;
        const consumption = parseFloat(form.querySelector('[name="consumption"]')?.value || 0);
        
        // Simple emission factors (in real app, fetch from API)
        const factors = {
            electricity: 0.82,
            lpg: 2.98,
            petrol: 2.31,
            diesel: 2.68
        };

        if (category === 'energy') {
            const source = form.querySelector('[name="energy_source"]')?.value;
            emissions = consumption * (factors[source] || 0.5);
        } else if (category === 'transport') {
            const distance = parseFloat(form.querySelector('[name="distance_km"]')?.value || 0);
            const frequency = parseFloat(form.querySelector('[name="frequency_per_month"]')?.value || 1);
            emissions = distance * frequency * 0.2; // Simplified calculation
        }

        previewElement.innerHTML = `
            <div class="alert alert-info">
                <i class="bi bi-calculator me-2"></i>
                Estimated emissions: <strong>${CarbonTracker.formatEmissions(emissions)}</strong>
            </div>
        `;
    }
};

// Dashboard specific functions
const Dashboard = {
    // Update dashboard data
    refresh: function() {
        const widgets = document.querySelectorAll('.dashboard-widget');
        widgets.forEach(widget => {
            widget.style.opacity = '0.6';
        });

        // Simulate refresh (in real app, make API call)
        setTimeout(() => {
            widgets.forEach(widget => {
                widget.style.opacity = '1';
            });
            CarbonTracker.showToast('Dashboard updated!', 'success');
        }, 1000);
    },

    // Setup auto-refresh
    setupAutoRefresh: function(intervalMinutes = 30) {
        setInterval(() => {
            this.refresh();
        }, intervalMinutes * 60 * 1000);
    }
};

// Export for use in other scripts
window.CarbonTracker = CarbonTracker;
window.ChartColors = ChartColors;
window.FormHelpers = FormHelpers;
window.Dashboard = Dashboard;