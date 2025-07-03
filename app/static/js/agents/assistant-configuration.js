/**
 * Assistant Configuration Module
 * Handles AI assistant tool configuration, testing, and status management
 */

// ===========================
// ASSISTANT CONFIGURATION CORE
// ===========================

// Initialize assistant configuration system
function initializeAssistantConfiguration() {
    try {
        // Update initial assistant status
        updateAssistantStatus();
        
        // Set up event listeners
        const assistantToolSelect = document.getElementById('ai_assistant_tool');
        if (assistantToolSelect) {
            // Remove any existing event listeners to prevent duplicates
            assistantToolSelect.removeEventListener('change', handleAssistantToolChange);
            
            // Add the event listener
            assistantToolSelect.addEventListener('change', handleAssistantToolChange);
            
            // Trigger initial configuration details display
            onAssistantToolChange(assistantToolSelect.value);
            updateTestButtonsState(); // Initial state
        }
    } catch (error) {
        console.warn('Error initializing assistant configuration:', error);
    }
}

// Event handler for assistant tool changes
function handleAssistantToolChange(event) {
    try {
        onAssistantToolChange(event.target.value);
    } catch (error) {
        console.error('Error handling assistant tool change:', error);
        // Don't show alert to user, just log the error
    }
}

// Handle assistant tool selection changes
function onAssistantToolChange(value) {
    // Safely update assistant status and test buttons
    try {
        updateAssistantStatus();
        updateTestButtonsState();
    } catch (error) {
        console.warn('Error updating assistant status:', error);
    }
    
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
    try {
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
    } catch (error) {
        console.warn('Error updating assistant status:', error);
    }
}

// Update test button states
function updateTestButtonsState() {
    try {
        const assistantTool = document.getElementById('ai_assistant_tool');
        const testConnectionBtn = document.getElementById('testConnectionBtn');
        const testChatBtn = document.getElementById('testChatBtn');
        const reassignAssistantBtn = document.getElementById('reassignAssistantBtn');
        const createAssistantBtn = document.getElementById('createAssistantBtn');
        
        if (!assistantTool) return;
        
        const hasValidTool = assistantTool.value && assistantTool.value.startsWith('tool:');
        const hasAssistantId = window.agentData?.assistant_id;
        
        // Enable/disable test buttons based on tool selection
        if (testConnectionBtn) {
            testConnectionBtn.disabled = !hasValidTool;
        }
        
        if (testChatBtn) {
            testChatBtn.disabled = !hasValidTool;
        }
        
        // Enable reassign button if agent has an assistant ID (regardless of tool selection)
        if (reassignAssistantBtn) {
            reassignAssistantBtn.disabled = !hasAssistantId;
        }
        
        // Enable create assistant button if tool is selected and agent doesn't have assistant
        if (createAssistantBtn) {
            createAssistantBtn.disabled = !hasValidTool || hasAssistantId;
        }
    } catch (error) {
        console.warn('Error updating test button states:', error);
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
                showNotificationSafe('Assistant Response: ' + responseMessage, true);
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

// Reassign assistant to agent
async function reassignAssistant() {
    const agentId = window.agentData?.id;
    if (!agentId) {
        showNotificationSafe('Agent ID not found', false);
        return;
    }
    
    // Get current assistant ID
    const currentAssistantId = window.agentData?.assistant_id;
    
    // Prompt for new assistant ID
    const newAssistantId = prompt(
        `Current Assistant ID: ${currentAssistantId || 'None'}\n\nEnter new Assistant ID to reassign:`,
        currentAssistantId || ''
    );
    
    if (!newAssistantId || newAssistantId === currentAssistantId) {
        return; // User cancelled or didn't change the ID
    }
    
    try {
        const response = await fetch(`/agents/api/${agentId}/reassign_assistant`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                new_assistant_id: newAssistantId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotificationSafe('Assistant reassigned successfully', true);
            
            // Update the agent data
            if (window.agentData) {
                window.agentData.assistant_id = newAssistantId;
            }
            
            // Update the assistant status display
            updateAssistantStatus();
            updateTestButtonsState();
            
            // Optional: Reload the page after a short delay to ensure all data is refreshed
            setTimeout(() => {
                window.location.reload();
            }, 1500);
            
        } else {
            showNotificationSafe(data.message || 'Failed to reassign assistant', false);
        }
        
    } catch (error) {
        console.error('Error reassigning assistant:', error);
        showNotificationSafe('Error reassigning assistant: ' + error.message, false);
    }
}

// Create and assign assistant with comprehensive traceability
async function createAndAssignAssistant() {
    const agentId = window.agentData?.id;
    if (!agentId) {
        showNotificationSafe('Agent ID not found', false);
        return;
    }
    
    // Get selected AI Assistant tool
    const assistantToolSelect = document.getElementById('ai_assistant_tool');
    if (!assistantToolSelect || !assistantToolSelect.value) {
        showNotificationSafe('Please select an AI Assistant tool first', false);
        return;
    }
    
    const toolValue = assistantToolSelect.value;
    if (!toolValue.startsWith('tool:')) {
        showNotificationSafe('Please select a valid AI Assistant tool', false);
        return;
    }
    
    // Confirm action with user
    const confirmMessage = `Create a new OpenAI Assistant for this agent?\n\n` +
                          `Agent: ${window.agentData?.name || 'Unknown'}\n` +
                          `Tool: ${assistantToolSelect.options[assistantToolSelect.selectedIndex].text}\n\n` +
                          `This will:\n` +
                          `• Create a new OpenAI Assistant\n` +
                          `• Configure it with agent parameters\n` +
                          `• Assign it to this agent\n` +
                          `• Provide detailed traceability logs`;
    
    if (!confirm(confirmMessage)) {
        return;
    }
    
    // Show loading state
    const createBtn = document.getElementById('createAssistantBtn');
    const originalText = createBtn.innerHTML;
    createBtn.innerHTML = '<i class="bi bi-hourglass-split mr-2 text-gray-400"></i>Creating...';
    createBtn.disabled = true;
    
    try {
        // Call API to create and assign assistant
        const response = await fetch(`/agents/api/${agentId}/create_assistant`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tool_id: toolValue.substring(5), // Remove 'tool:' prefix
                trace_level: 'detailed'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Show success with detailed information
            const details = data.details || {};
            let successMessage = 'Assistant created and assigned successfully!\n\n';
            
            if (details.assistant_id) {
                successMessage += `Assistant ID: ${details.assistant_id}\n`;
            }
            if (details.model) {
                successMessage += `Model: ${details.model}\n`;
            }
            if (details.tools_count) {
                successMessage += `Tools configured: ${details.tools_count}\n`;
            }
            if (details.files_count) {
                successMessage += `Files attached: ${details.files_count}\n`;
            }
            if (details.creation_time) {
                successMessage += `Created at: ${new Date(details.creation_time).toLocaleString()}\n`;
            }
            
            // Show traceability information
            if (data.trace_log && data.trace_log.length > 0) {
                successMessage += '\n=== Creation Log ===\n';
                data.trace_log.forEach((entry, index) => {
                    successMessage += `${index + 1}. ${entry.step}: ${entry.status}\n`;
                    if (entry.details) {
                        successMessage += `   ${entry.details}\n`;
                    }
                });
            }
            
            showNotification(successMessage, true);
            
            // Update the agent data
            if (window.agentData && details.assistant_id) {
                window.agentData.assistant_id = details.assistant_id;
            }
            
            // Update the assistant status display
            updateAssistantStatus();
            updateTestButtonsState();
            
            // Reload the page after a short delay to ensure all data is refreshed
            setTimeout(() => {
                window.location.reload();
            }, 2000);
            
        } else {
            let errorMessage = 'Failed to create assistant\n\n';
            errorMessage += `Error: ${data.message || 'Unknown error'}\n`;
            
            // Show error trace log if available
            if (data.trace_log && data.trace_log.length > 0) {
                errorMessage += '\n=== Error Log ===\n';
                data.trace_log.forEach((entry, index) => {
                    errorMessage += `${index + 1}. ${entry.step}: ${entry.status}\n`;
                    if (entry.error) {
                        errorMessage += `   Error: ${entry.error}\n`;
                    }
                    if (entry.details) {
                        errorMessage += `   Details: ${entry.details}\n`;
                    }
                });
            }
            
            showNotification(errorMessage, false);
        }
        
    } catch (error) {
        console.error('Error creating assistant:', error);
        showNotification(`Error creating assistant: ${error.message}\n\nPlease check the console for more details.`, false);
    } finally {
        // Restore button state
        createBtn.innerHTML = originalText;
        createBtn.disabled = false;
    }
}

// ===========================
// UTILITY FUNCTIONS
// ===========================

// Create and display a custom notification
function showNotification(message, isSuccess) {
    // Create notification element
    const notif = document.createElement('div');
    notif.className = `alert alert-${isSuccess ? 'success' : 'danger'} fixed-notification`;
    notif.style.position = 'fixed';
    notif.style.top = '20px';
    notif.style.right = '20px';
    notif.style.maxWidth = '400px';
    notif.style.zIndex = '9999';
    notif.style.padding = '15px 20px';
    notif.style.borderRadius = '4px';
    notif.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
    notif.style.backgroundColor = isSuccess ? '#d4edda' : '#f8d7da';
    notif.style.color = isSuccess ? '#155724' : '#721c24';
    notif.style.border = `1px solid ${isSuccess ? '#c3e6cb' : '#f5c6cb'}`;
    
    // Support for newlines in the message
    const messageContent = message.replace(/\n/g, '<br>');
    notif.innerHTML = messageContent;
    
    // Add close button
    const closeBtn = document.createElement('button');
    closeBtn.innerHTML = '&times;';
    closeBtn.style.position = 'absolute';
    closeBtn.style.right = '10px';
    closeBtn.style.top = '10px';
    closeBtn.style.background = 'transparent';
    closeBtn.style.border = 'none';
    closeBtn.style.fontSize = '20px';
    closeBtn.style.cursor = 'pointer';
    closeBtn.style.color = isSuccess ? '#155724' : '#721c24';
    closeBtn.onclick = function() {
        document.body.removeChild(notif);
    };
    
    notif.appendChild(closeBtn);
    document.body.appendChild(notif);
    
    // Auto remove after 10 seconds
    setTimeout(() => {
        if (document.body.contains(notif)) {
            document.body.removeChild(notif);
        }
    }, 10000);
}

// Safe notification function that checks if showNotification exists
function showNotificationSafe(message, isSuccess) {
    showNotification(message, isSuccess);
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
    testChat: chatWithAssistant,
    reassignAssistant: reassignAssistant,
    createAndAssignAssistant: createAndAssignAssistant
};

// Make functions globally available for onclick handlers
window.onAssistantToolChange = onAssistantToolChange;
window.testAssistantConnection = testAssistantConnection;
window.chatWithAssistant = chatWithAssistant;
window.updateTestButtonsState = updateTestButtonsState;
window.reassignAssistant = reassignAssistant;
window.createAndAssignAssistant = createAndAssignAssistant;
