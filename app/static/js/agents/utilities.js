/**
 * Utilities Module
 * Contains helper functions used across the agent edit page
 */

/**
 * Show notification to user
 */
function showNotification(message, isSuccess = true) {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transition-all duration-300 transform translate-x-full ${
        isSuccess ? 'bg-green-100 border border-green-400 text-green-700' : 'bg-red-100 border border-red-400 text-red-700'
    }`;
    
    notification.innerHTML = `
        <div class="flex items-center">
            <i class="${isSuccess ? 'bi bi-check-circle' : 'bi bi-exclamation-triangle'} mr-2"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-2 text-gray-500 hover:text-gray-700">
                <i class="bi bi-x"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.classList.remove('translate-x-full');
    }, 100);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.classList.add('translate-x-full');
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}

/**
 * Simple auto-save functionality
 */
let saveTimeout;
function scheduleAutoSave() {
    clearTimeout(saveTimeout);
    saveTimeout = setTimeout(function() {
        console.log('Auto-saving agent changes...');
        // Auto-save logic can be added here
    }, 2000);
}

/**
 * Helper function to escape HTML
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return (text || '').replace(/[&<>"']/g, m => map[m]);
}

/**
 * Enable/disable test buttons based on assistant tool selection
 */
function updateTestButtonsState() {
    const assistantTool = document.getElementById('ai_assistant_tool')?.value;
    const testConnectionBtn = document.getElementById('testConnectionBtn');
    const testChatBtn = document.getElementById('testChatBtn');
    
    if (testConnectionBtn && testChatBtn) {
        if (assistantTool && assistantTool !== '') {
            testConnectionBtn.disabled = false;
            testChatBtn.disabled = false;
        } else {
            testConnectionBtn.disabled = true;
            testChatBtn.disabled = true;
        }
    }
}

/**
 * Update assistant status display
 */
function updateAssistantStatus() {
    const assistantTool = document.getElementById('ai_assistant_tool')?.value;
    const statusElement = document.getElementById('assistantStatus');
    
    if (statusElement) {
        if (assistantTool && assistantTool !== '') {
            statusElement.textContent = 'Configured';
            statusElement.className = 'ml-2 px-2 py-1 text-xs rounded-full bg-green-100 text-green-600';
        } else {
            statusElement.textContent = 'Not Configured';
            statusElement.className = 'ml-2 px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-600';
        }
    }
}

/**
 * Debug function to test API connectivity
 */
async function debugTaskAPI() {
    try {
        const agentId = window.agentData?.id || '';
        const debugUrl = `/agents/api/${agentId}/tasks/debug`;
        
        console.log('Testing debug endpoint:', debugUrl);
        
        const response = await fetch(debugUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name="csrf_token"]')?.value || ''
            },
            body: JSON.stringify({test: 'debug'})
        });
        
        const result = await response.json();
        console.log('Debug response:', result);
        showNotification('Debug test completed. Check console for details.', true);
        
    } catch (error) {
        console.error('Debug test failed:', error);
        showNotification('Debug test failed: ' + error.message, false);
    }
}

/**
 * Initialize DOM event listeners
 */
function initializeEventListeners() {
    // Add change listeners to form fields for auto-save
    const form = document.getElementById('agentEditForm');
    if (form) {
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('change', scheduleAutoSave);
            input.addEventListener('input', scheduleAutoSave);
        });
    }
    
    // Initialize assistant tool display and button states
    const assistantToolSelect = document.getElementById('ai_assistant_tool');
    if (assistantToolSelect) {
        assistantToolSelect.addEventListener('change', updateTestButtonsState);
        assistantToolSelect.addEventListener('change', updateAssistantStatus);
        updateTestButtonsState(); // Initial state
        updateAssistantStatus(); // Initial state
        
        // Trigger initial configuration details display
        const selectedTool = assistantToolSelect.value;
        if (selectedTool && typeof onAssistantToolChange === 'function') {
            onAssistantToolChange(selectedTool);
        }
    }
}

/**
 * Initialize utilities on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
});

// Make functions globally available
window.showNotification = showNotification;
window.scheduleAutoSave = scheduleAutoSave;
window.escapeHtml = escapeHtml;
window.updateTestButtonsState = updateTestButtonsState;
window.updateAssistantStatus = updateAssistantStatus;
window.debugTaskAPI = debugTaskAPI;
