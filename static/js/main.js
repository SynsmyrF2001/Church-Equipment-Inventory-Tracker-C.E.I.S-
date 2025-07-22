// Main JavaScript for Church Equipment Inventory System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize search functionality
    initializeSearch();
    
    // Initialize form enhancements
    initializeFormEnhancements();
    
    // Initialize mobile optimizations
    initializeMobileOptimizations();
    
    // Initialize auto-refresh for dashboard
    initializeAutoRefresh();
    
    console.log('Church Equipment Inventory System initialized');
});

// Tooltips disabled for cleaner interface

/**
 * Initialize search functionality
 */
function initializeSearch() {
    const searchForm = document.querySelector('form[action*="index"]');
    const searchInput = document.getElementById('search');
    
    if (searchInput) {
        // Add search icon
        const searchIcon = document.createElement('i');
        searchIcon.setAttribute('data-feather', 'search');
        searchIcon.className = 'position-absolute top-50 end-0 translate-middle-y me-3';
        searchIcon.style.pointerEvents = 'none';
        searchIcon.style.zIndex = '5';
        
        const inputGroup = searchInput.parentNode;
        inputGroup.style.position = 'relative';
        inputGroup.appendChild(searchIcon);
        
        // Re-initialize feather icons
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
        
        // Auto-submit on enter
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                searchForm.submit();
            }
        });
    }
}

/**
 * Initialize form enhancements
 */
function initializeFormEnhancements() {
    // Auto-format currency inputs
    const priceInputs = document.querySelectorAll('input[name="purchase_price"]');
    priceInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value && !isNaN(this.value)) {
                this.value = parseFloat(this.value).toFixed(2);
            }
        });
    });
    
    // Auto-uppercase serial numbers
    const serialInputs = document.querySelectorAll('input[name="serial_number"]');
    serialInputs.forEach(input => {
        input.addEventListener('input', function() {
            this.value = this.value.toUpperCase();
        });
    });
    
    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('button[type="submit"][class*="danger"]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
    
    // Form validation feedback
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                
                // Focus first invalid field
                const firstInvalidField = form.querySelector(':invalid');
                if (firstInvalidField) {
                    firstInvalidField.focus();
                    firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
            form.classList.add('was-validated');
        });
    });
}

/**
 * Initialize mobile optimizations
 */
function initializeMobileOptimizations() {
    // Detect mobile device
    const isMobile = window.innerWidth <= 768;
    
    if (isMobile) {
        // Make tables more touch-friendly
        const tables = document.querySelectorAll('.table-responsive table');
        tables.forEach(table => {
            table.style.fontSize = '0.875rem';
        });
        
        // Add swipe gestures for table navigation
        addSwipeGestures();
        
        // Optimize dropdown menus for touch
        optimizeDropdowns();
        
        // Add pull-to-refresh functionality
        addPullToRefresh();
    }
    
    // Handle orientation changes
    window.addEventListener('orientationchange', function() {
        setTimeout(function() {
            // Recalculate layouts after orientation change
            window.dispatchEvent(new Event('resize'));
        }, 100);
    });
}

/**
 * Add swipe gestures for better mobile navigation
 */
function addSwipeGestures() {
    let startX = 0;
    let startY = 0;
    
    document.addEventListener('touchstart', function(e) {
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
    }, { passive: true });
    
    document.addEventListener('touchend', function(e) {
        if (!startX || !startY) return;
        
        const endX = e.changedTouches[0].clientX;
        const endY = e.changedTouches[0].clientY;
        
        const diffX = startX - endX;
        const diffY = startY - endY;
        
        // Horizontal swipe (left/right)
        if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
            if (diffX > 0) {
                // Swiped left - could trigger next action
                console.log('Swiped left');
            } else {
                // Swiped right - could trigger back action
                console.log('Swiped right');
            }
        }
        
        startX = 0;
        startY = 0;
    }, { passive: true });
}

/**
 * Optimize dropdown menus for mobile
 */
function optimizeDropdowns() {
    const dropdowns = document.querySelectorAll('.dropdown-toggle');
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('click', function(e) {
            // Add slight delay for better touch response
            setTimeout(() => {
                const menu = this.nextElementSibling;
                if (menu && menu.classList.contains('dropdown-menu')) {
                    menu.style.minWidth = '200px';
                }
            }, 10);
        });
    });
}

/**
 * Add pull-to-refresh functionality
 */
function addPullToRefresh() {
    let startY = 0;
    let currentY = 0;
    let pulling = false;
    
    document.addEventListener('touchstart', function(e) {
        if (window.scrollY === 0) {
            startY = e.touches[0].clientY;
            pulling = false;
        }
    }, { passive: true });
    
    document.addEventListener('touchmove', function(e) {
        if (startY && window.scrollY === 0) {
            currentY = e.touches[0].clientY;
            if (currentY > startY + 50 && !pulling) {
                pulling = true;
                showPullToRefreshIndicator();
            }
        }
    }, { passive: true });
    
    document.addEventListener('touchend', function() {
        if (pulling) {
            pulling = false;
            hidePullToRefreshIndicator();
            // Refresh the page
            window.location.reload();
        }
        startY = 0;
        currentY = 0;
    }, { passive: true });
}

/**
 * Show pull-to-refresh indicator
 */
function showPullToRefreshIndicator() {
    let indicator = document.getElementById('pull-refresh-indicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'pull-refresh-indicator';
        indicator.className = 'alert alert-info text-center position-fixed w-100';
        indicator.style.top = '0';
        indicator.style.zIndex = '9999';
        indicator.innerHTML = '<i data-feather="refresh-cw" class="me-2"></i>Release to refresh';
        document.body.insertBefore(indicator, document.body.firstChild);
        
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    }
    indicator.style.display = 'block';
}

/**
 * Hide pull-to-refresh indicator
 */
function hidePullToRefreshIndicator() {
    const indicator = document.getElementById('pull-refresh-indicator');
    if (indicator) {
        indicator.style.display = 'none';
    }
}

/**
 * Initialize auto-refresh for dashboard
 */
function initializeAutoRefresh() {
    // Only auto-refresh on dashboard
    if (window.location.pathname === '/' || window.location.pathname.includes('index')) {
        // Check for updates every 5 minutes
        setInterval(function() {
            // Only refresh if user is active (not idle)
            if (document.visibilityState === 'visible') {
                checkForUpdates();
            }
        }, 300000); // 5 minutes
    }
}

/**
 * Check for updates without full page refresh
 */
function checkForUpdates() {
    // This could be enhanced to use AJAX to check for changes
    // For now, we'll just add a visual indicator that data might be stale
    const lastUpdate = localStorage.getItem('lastDashboardUpdate');
    const now = new Date().getTime();
    
    if (lastUpdate && (now - parseInt(lastUpdate)) > 900000) { // 15 minutes
        showStaleDataWarning();
    }
    
    localStorage.setItem('lastDashboardUpdate', now.toString());
}

/**
 * Show stale data warning
 */
function showStaleDataWarning() {
    const warning = document.createElement('div');
    warning.className = 'alert alert-warning alert-dismissible fade show position-fixed';
    warning.style.top = '80px';
    warning.style.right = '20px';
    warning.style.zIndex = '9999';
    warning.style.maxWidth = '300px';
    warning.innerHTML = `
        <small>
            <i data-feather="clock" class="me-1"></i>
            Data may be outdated. 
            <a href="#" onclick="window.location.reload()" class="alert-link">Refresh</a>
        </small>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(warning);
    
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
    
    // Auto-remove after 10 seconds
    setTimeout(() => {
        if (warning.parentNode) {
            warning.remove();
        }
    }, 10000);
}

/**
 * Utility function to format dates
 */
function formatDate(date, format = 'short') {
    const options = {
        short: { year: 'numeric', month: 'short', day: 'numeric' },
        long: { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }
    };
    
    return new Intl.DateTimeFormat('en-US', options[format]).format(new Date(date));
}

/**
 * Utility function to show loading state
 */
function showLoading(element) {
    if (element) {
        element.classList.add('loading');
        const spinner = document.createElement('div');
        spinner.className = 'spinner-border spinner-border-sm me-2';
        spinner.setAttribute('role', 'status');
        element.insertBefore(spinner, element.firstChild);
    }
}

/**
 * Utility function to hide loading state
 */
function hideLoading(element) {
    if (element) {
        element.classList.remove('loading');
        const spinner = element.querySelector('.spinner-border');
        if (spinner) {
            spinner.remove();
        }
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-bg-${type} border-0`;
    toastEl.setAttribute('role', 'alert');
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
    
    // Remove toast element after it's hidden
    toastEl.addEventListener('hidden.bs.toast', function() {
        toastEl.remove();
    });
}

/**
 * Create toast container if it doesn't exist
 */
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function() {
            showToast('Copied to clipboard!', 'success');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showToast('Copied to clipboard!', 'success');
    }
}

// Novice features disabled for cleaner interface

// Tooltips disabled for cleaner interface

// Smart form assistance disabled for cleaner interface

// Name suggestions disabled for cleaner interface

// Location suggestions disabled for cleaner interface

// Button feedback disabled for cleaner interface

// Contextual help disabled for cleaner interface

// Tutorial highlights disabled for cleaner interface

// Keyboard shortcuts disabled for cleaner interface

// Export functions for global use
window.ChurchInventory = {
    showToast,
    copyToClipboard,
    formatDate,
    showLoading,
    hideLoading
};
