/**
 * Notification Utilities for Agent Run View
 * Handles user notifications and feedback messages
 */

/**
 * Show a notification message to the user
 * @param {string} message - The message to display
 * @param {string} type - Type of notification: 'info', 'success', 'error', 'warning'
 */
function showNotification(message, type = 'info') {
    // Create a simple notification
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
        type === 'success' ? 'bg-green-500 text-white' :
        type === 'error' ? 'bg-red-500 text-white' :
        type === 'warning' ? 'bg-orange-500 text-white' :
        'bg-blue-500 text-white'
    }`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

/**
 * Show a loading notification that needs to be manually dismissed
 * @param {string} message - The loading message
 * @returns {HTMLElement} The notification element for manual removal
 */
function showLoadingNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 bg-blue-500 text-white flex items-center';
    notification.innerHTML = `
        <svg class="animate-spin h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        ${message}
    `;
    document.body.appendChild(notification);
    return notification;
}

/**
 * Dismiss a specific notification
 * @param {HTMLElement} notification - The notification element to remove
 */
function dismissNotification(notification) {
    if (notification && notification.parentNode) {
        notification.remove();
    }
}

// Export functions for global use
window.showNotification = showNotification;
window.showLoadingNotification = showLoadingNotification;
window.dismissNotification = dismissNotification;
