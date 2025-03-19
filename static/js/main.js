/**
 * Personal Assistant - Main JavaScript
 * 
 * This file contains the main JavaScript functionality for the personal assistant application.
 * It follows clean, organized structure with appropriate comments and error handling.
 */

// Use strict mode to catch common coding mistakes
'use strict';

/**
 * Main application object using module pattern to avoid global namespace pollution
 */
const PersonalAssistant = (function() {
    // Private variables
    let authStatus = {
        gmail: false,
        calendar: false,
        user: null
    };
    
    /**
     * Initialize the application
     */
    function init() {
        // Check authentication status on page load
        checkAuthStatus();
        
        // Set up event listeners
        setupEventListeners();
        
        // Initialize tooltips
        initTooltips();
        
        console.log('Personal Assistant initialized');
    }
    
    /**
     * Check authentication status for Google services
     */
    function checkAuthStatus() {
        fetch('/api/auth/status')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                authStatus.gmail = data.gmail_authenticated;
                authStatus.calendar = data.calendar_authenticated;
                authStatus.user = data.user_info;
                
                updateAuthUI();
            })
            .catch(error => {
                console.error('Error checking auth status:', error);
                showErrorNotification('Failed to check authentication status');
            });
    }
    
    /**
     * Update the UI based on authentication status
     */
    function updateAuthUI() {
        const authStatusDiv = document.getElementById('auth-status');
        if (!authStatusDiv) return;
        
        if (authStatus.gmail || authStatus.calendar) {
            // User is authenticated
            authStatusDiv.innerHTML = `
                <div class="dropdown">
                    <button class="btn btn-outline-light dropdown-toggle" type="button" id="userDropdown" data-bs-toggle="dropdown">
                        <i class="fas fa-user-circle me-1"></i>
                        ${authStatus.user ? authStatus.user.email : 'User'}
                    </button>
                    <ul class="dropdown-menu dropdown-menu-end">
                        <li><a class="dropdown-item" href="/preferences"><i class="fas fa-cog me-1"></i>Preferences</a></li>
                        <li><hr class="dropdown-divider"></li>
                        <li>
                            <button class="dropdown-item text-danger" id="logout-btn">
                                <i class="fas fa-sign-out-alt me-1"></i>Logout
                            </button>
                        </li>
                    </ul>
                </div>
            `;
            
            // Add logout event listener
            document.getElementById('logout-btn').addEventListener('click', logout);
        } else {
            // User is not authenticated
            authStatusDiv.innerHTML = `
                <a href="/auth/login" class="btn btn-outline-light" id="login-btn">
                    <i class="fas fa-sign-in-alt me-1"></i>Login
                </a>
            `;
        }
        
        // Update service status indicators if they exist
        updateServiceStatus('gmail-status', authStatus.gmail);
        updateServiceStatus('calendar-status', authStatus.calendar);
    }
    
    /**
     * Update service status indicator
     * 
     * @param {string} elementId - ID of the status element
     * @param {boolean} isAuthenticated - Whether the service is authenticated
     */
    function updateServiceStatus(elementId, isAuthenticated) {
        const statusElement = document.getElementById(elementId);
        if (!statusElement) return;
        
        if (isAuthenticated) {
            statusElement.innerHTML = '<span class="badge bg-success">Connected</span>';
        } else {
            statusElement.innerHTML = '<span class="badge bg-danger">Not Connected</span>';
        }
    }
    
    /**
     * Set up global event listeners
     */
    function setupEventListeners() {
        // Handle form submissions to prevent page reload
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', function(e) {
                // Only prevent default if the form doesn't have a specific action
                if (!this.getAttribute('action')) {
                    e.preventDefault();
                }
            });
        });
        
        // Auto-resize textareas
        document.querySelectorAll('textarea').forEach(textarea => {
            textarea.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = (this.scrollHeight) + 'px';
            });
        });
    }
    
    /**
     * Initialize Bootstrap tooltips
     */
    function initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    /**
     * Log out the user
     */
    function logout() {
        fetch('/api/auth/logout', { method: 'POST' })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Refresh the page to update UI
                window.location.reload();
            })
            .catch(error => {
                console.error('Error logging out:', error);
                showErrorNotification('Failed to log out');
            });
    }
    
    /**
     * Show a success notification
     * 
     * @param {string} message - The message to display
     */
    function showSuccessNotification(message) {
        showNotification(message, 'success');
    }
    
    /**
     * Show an error notification
     * 
     * @param {string} message - The message to display
     */
    function showErrorNotification(message) {
        showNotification(message, 'danger');
    }
    
    /**
     * Show a notification
     * 
     * @param {string} message - The message to display
     * @param {string} type - The type of notification (success, danger, warning, info)
     */
    function showNotification(message, type = 'info') {
        // Check if notification container exists, create if not
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.style.position = 'fixed';
            container.style.top = '20px';
            container.style.right = '20px';
            container.style.zIndex = '1050';
            document.body.appendChild(container);
        }
        
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `toast align-items-center text-white bg-${type} border-0`;
        notification.role = 'alert';
        notification.setAttribute('aria-live', 'assertive');
        notification.setAttribute('aria-atomic', 'true');
        
        notification.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        container.appendChild(notification);
        
        // Initialize and show the toast
        const toast = new bootstrap.Toast(notification, {
            autohide: true,
            delay: 5000
        });
        toast.show();
        
        // Remove from DOM after hiding
        notification.addEventListener('hidden.bs.toast', function() {
            notification.remove();
        });
    }
    
    /**
     * Format a date for display
     * 
     * @param {Date|string} date - The date to format
     * @param {boolean} includeTime - Whether to include the time
     * @returns {string} Formatted date string
     */
    function formatDate(date, includeTime = true) {
        if (!(date instanceof Date)) {
            date = new Date(date);
        }
        
        const options = {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        };
        
        if (includeTime) {
            options.hour = '2-digit';
            options.minute = '2-digit';
        }
        
        return date.toLocaleDateString(undefined, options);
    }
    
    /**
     * Format a date for datetime-local input
     * 
     * @param {Date|string} date - The date to format
     * @returns {string} Formatted date string for datetime-local input
     */
    function formatDateTimeForInput(date) {
        if (!(date instanceof Date)) {
            date = new Date(date);
        }
        
        return date.toISOString().slice(0, 16);
    }
    
    // Public API
    return {
        init: init,
        showSuccessNotification: showSuccessNotification,
        showErrorNotification: showErrorNotification,
        formatDate: formatDate,
        formatDateTimeForInput: formatDateTimeForInput
    };
})();

// Initialize the application when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', PersonalAssistant.init);
