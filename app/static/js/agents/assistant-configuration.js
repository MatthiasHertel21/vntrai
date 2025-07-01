/**
 * Assistant Configuration Module
 * Handles AI assistant tool configuration, testing, and status management
 */

// ===========================
// ASSISTANT CONFIGURATION CORE
// ===========================

// Initialize assistant configuration system
function initializeAssistantConfiguration() {
    // Use assistant tools from window object (injected from template)
    // const assistantTools = window.assistantTools || []; // Removed to avoid conflicts - use window.assistantTools directly
    
    // Update initial assistant status
    updateAssistantStatus();
    
    // Set up event listeners
    const assistantToolSelect = document.getElementById('ai_assistant_tool');
    if (assistantToolSelect) {
        assistantToolSelect.addEventListener('change', function() {
            onAssistantToolChange(this.value);
            updateAssistantStatus();
            updateTestButtonsState();
        });
        
        // Trigger initial configuration details display
        onAssistantToolChange(assistantToolSelect.value);
        updateTestButtonsState(); // Initial state
    }
}

// Handle assistant tool selection changes
function onAssistantToolChange(value) {
    // Configuration details container was removed - skip details display
    const detailsPanel = document.getElementById('assistant_config_details');
    if (!detailsPanel) {
        console.log('Configuration details container not available (removed from UI)');
        return;
    }
    
    const detailsDiv = document.getElementById('assistant_tool_details');
    
    // Check if elements exist to prevent errors
    if (!detailsDiv) {
        console.warn('Assistant configuration details elements not found');
        return;
    }
    
    if (value && value.startsWith('tool:')) {
        // Tool-based assistant
        const toolId = value.substring(5);
        const tool = (window.assistantTools || []).find(t => t.id === toolId);
        
        if (tool) {
            const assistantOptions = tool.options?.assistant || {};
            
            detailsDiv.innerHTML = `
                <div class="space-y-2">
                    <div><strong>Tool:</strong> ${escapeHtml(tool.name)}</div>
                    <div><strong>Type:</strong> ${escapeHtml(tool.tool_definition)}</div>
                    <div><strong>Status:</strong> ${escapeHtml(tool.status)}</div>
                    <div><strong>Integration:</strong> ${escapeHtml(tool.integration_id || 'Not connected')}</div>
                    <div><strong>Assistant Enabled:</strong> ${assistantOptions.enabled ? 'Yes' : 'No'}</div>
                </div>
            `;
            detailsPanel.classList.remove('hidden');
        }
    } else {
        // No selection
        detailsPanel.classList.add('hidden');
    }
}

// Update assistant status indicator
function updateAssistantStatus() {
    const assistantTool = document.getElementById('ai_assistant_tool');
    const statusElement = document.getElementById('assistantStatus');
    
    if (!assistantTool || !statusElement) return;
    
    if (assistantTool.value && assistantTool.value !== '') {
        statusElement.textContent = 'Configured';
        statusElement.className = 'ml-2 px-2 py-1 text-xs rounded-full bg-green-100 text-green-600';
    } else {
        statusElement.textContent = 'Not Configured';
        statusElement.className = 'ml-2 px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-600';
    }
}

// Update test button states
function updateTestButtonsState() {
    const assistantTool = document.getElementById('ai_assistant_tool');
    const testConnectionBtn = document.getElementById('testConnectionBtn');
    const testChatBtn = document.getElementById('testChatBtn');
    
    if (!assistantTool) return;
    
    const hasValidTool = assistantTool.value && assistantTool.value.startsWith('tool:');
    
    if (testConnectionBtn) {
        testConnectionBtn.disabled = !hasValidTool;
    }
    
    if (testChatBtn) {
        testChatBtn.disabled = !hasValidTool;
    }
}

// ===========================
// ASSISTANT TESTING FUNCTIONS
// ===========================

// Test assistant connection
async function testAssistantConnection() {
    const selectedTool = document.getElementById('ai_assistant_tool');
    if (!selectedTool) return;
    
    const toolValue = selectedTool.value;
    
    if (!toolValue) {
        showNotificationSafe('Please select an AI assistant tool first', false);
        return;
    }
    
    if (toolValue.startsWith('tool:')) {
        const toolId = toolValue.substring(5);
        
        try {
            const response = await fetch(`/tools/test_assistant/${toolId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            showNotificationSafe(data.message, data.success);
            
        } catch (error) {
            console.error('Error testing assistant connection:', error);
            showNotificationSafe('Connection test failed: ' + error.message, false);
        }
    } else {
        showNotificationSafe('Please select a valid assistant tool', false);
    }
}

// Test chat with assistant
async function chatWithAssistant() {
    const selectedTool = document.getElementById('ai_assistant_tool');
    if (!selectedTool) return;
    
    const toolValue = selectedTool.value;
    
    if (!toolValue) {
        showNotificationSafe('Please select an AI assistant tool first', false);
        return;
    }
    
    if (toolValue.startsWith('tool:')) {
        const toolId = toolValue.substring(5);
        const message = prompt('Enter a test message:');
        
        if (!message) return;
        
        try {
            const response = await fetch(`/tools/chat_assistant/${toolId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                const responseMessage = data.message || data.data?.message || 'No response';
                alert('Assistant Response: ' + responseMessage);
            } else {
                showNotificationSafe('Chat failed: ' + data.message, false);
            }
            
        } catch (error) {
            console.error('Error chatting with assistant:', error);
            showNotificationSafe('Chat failed: ' + error.message, false);
        }
    } else {
        showNotificationSafe('Please select a valid assistant tool', false);
    }
}

// ===========================
// UTILITY FUNCTIONS
// ===========================

// Safe notification function that checks if showNotification exists
function showNotificationSafe(message, isSuccess) {
    if (typeof showNotification === 'function') {
        showNotification(message, isSuccess);
    } else {
        // Fallback to console
        console.log(`${isSuccess ? 'SUCCESS' : 'ERROR'}: ${message}`);
    }
}

// Safe HTML escaping function
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ===========================
// PUBLIC API
// ===========================

// Export functions for global access
window.AssistantConfiguration = {
    initialize: initializeAssistantConfiguration,
    onToolChange: onAssistantToolChange,
    updateStatus: updateAssistantStatus,
    updateTestButtons: updateTestButtonsState,
    testConnection: testAssistantConnection,
    testChat: chatWithAssistant
};

// Make functions globally available for onclick handlers
window.onAssistantToolChange = onAssistantToolChange;
window.testAssistantConnection = testAssistantConnection;
window.chatWithAssistant = chatWithAssistant;
window.updateTestButtonsState = updateTestButtonsState;
