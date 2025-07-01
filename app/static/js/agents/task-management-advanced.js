/**
 * Task Management Advanced Module
 * Handles advanced task operations like migration, reordering, and API interactions
 */

// ===========================
// TASK MANAGEMENT CORE
// ===========================

// Global variables for task management
// let agentTasks = []; // Removed to avoid conflicts - use window.agentTasks instead
let currentEditingTaskUuid = null;

// Initialize task management system
function initializeTaskManagement(agentData = {}) {
    // Initialize global agentTasks if not already set
    if (!window.agentTasks) {
        window.agentTasks = [];
    }
    
    // Load existing tasks
    if (agentData.tasks) {
        window.agentTasks = [...agentData.tasks];
    } else {
        window.agentTasks = [];
    }
    
    // Check if migration is needed
    checkMigrationNeeded(agentData);
    
    // Update task count
    updateTaskCount();
}

// Check if legacy migration is needed
function checkMigrationNeeded(agentData = {}) {
    const hasInstructions = agentData?.instructions && agentData.instructions.trim() !== '';
    const hasInputFields = agentData?.input_fields && agentData.input_fields.length > 0;
    const hasTasks = window.agentTasks.length > 0;
    
    const migrationAlert = document.getElementById('migrationAlert');
    if (!migrationAlert) return;
    
    if ((hasInstructions || hasInputFields) && !hasTasks) {
        migrationAlert.classList.remove('hidden');
    } else {
        migrationAlert.classList.add('hidden');
    }
}

// Update task count display
function updateTaskCount() {
    const taskCountElement = document.getElementById('taskCount');
    if (taskCountElement) {
        taskCountElement.textContent = window.agentTasks.length;
    }
}

// ===========================
// TASK MIGRATION FUNCTIONS
// ===========================

// Migrate legacy instructions to new task system
async function migrateLegacyInstructions(agentData = {}) {
    if (!confirm('This will create a new AI task from your existing instructions. Continue?')) {
        return;
    }
    
    try {
        const instructions = agentData?.instructions || '';
        const inputFields = agentData?.input_fields || [];
        
        const taskData = {
            name: 'Legacy Instructions',
            type: 'ai',
            description: 'Migrated from legacy agent instructions',
            ai_config: {
                instructions: instructions,
                input_fields: inputFields,
                goals: []
            }
        };
        
        // Use the createTask function from task-modals.js if available
        if (typeof createTask === 'function') {
            await createTask(taskData);
        } else {
            console.error('createTask function not available for migration');
            showNotificationSafe('Migration failed: createTask function not available', false);
            return;
        }
        
        // Hide migration alert
        const migrationAlert = document.getElementById('migrationAlert');
        if (migrationAlert) {
            migrationAlert.classList.add('hidden');
        }
        
        showNotificationSafe('Legacy instructions migrated successfully!', true);
        
    } catch (error) {
        console.error('Error migrating instructions:', error);
        showNotificationSafe('Error migrating instructions: ' + error.message, false);
    }
}

// ===========================
// TASK REORDERING FUNCTIONS
// ===========================

// Move task up in the list
async function moveTaskUp(taskUuid) {
    try {
        const agentId = getAgentIdFromPage();
        if (!agentId) {
            showNotificationSafe('Agent ID not found', false);
            return;
        }
        
        const response = await fetch(`/agents/api/${agentId}/tasks/${taskUuid}/move-up`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotificationSafe('Task moved up successfully', true);
            // Reload page to show new order
            window.location.reload();
        } else {
            showNotificationSafe('Failed to move task: ' + result.error, false);
        }
    } catch (error) {
        console.error('Error moving task up:', error);
        showNotificationSafe('Error moving task: ' + error.message, false);
    }
}

// Move task down in the list
async function moveTaskDown(taskUuid) {
    try {
        const agentId = getAgentIdFromPage();
        if (!agentId) {
            showNotificationSafe('Agent ID not found', false);
            return;
        }
        
        const response = await fetch(`/agents/api/${agentId}/tasks/${taskUuid}/move-down`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotificationSafe('Task moved down successfully', true);
            // Reload page to show new order
            window.location.reload();
        } else {
            showNotificationSafe('Failed to move task: ' + result.error, false);
        }
    } catch (error) {
        console.error('Error moving task down:', error);
        showNotificationSafe('Error moving task: ' + error.message, false);
    }
}

// ===========================
// TASK API FUNCTIONS
// ===========================

// Debug function to test API connectivity
async function debugTaskAPI() {
    try {
        const agentId = getAgentIdFromPage();
        if (!agentId) {
            showNotificationSafe('Agent ID not found for debugging', false);
            return;
        }
        
        const debugUrl = `/agents/api/${agentId}/tasks/debug`;
        
        console.log('Testing debug endpoint:', debugUrl);
        
        const response = await fetch(debugUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({test: 'debug'})
        });
        
        const result = await response.json();
        console.log('Debug response:', result);
        showNotificationSafe('Debug test completed. Check console for details.', true);
        
    } catch (error) {
        console.error('Debug test failed:', error);
        showNotificationSafe('Debug test failed: ' + error.message, false);
    }
}

// Add debug button (for development/testing)
function addDebugButton() {
    if (document.getElementById('debugTaskButton')) return; // Already added
    
    const debugButton = document.createElement('button');
    debugButton.id = 'debugTaskButton';
    debugButton.type = 'button';
    debugButton.className = 'btn btn-sm btn-warning';
    debugButton.innerHTML = '<i class="bi bi-bug"></i> Debug API';
    debugButton.onclick = debugTaskAPI;
    
    const buttonContainer = document.querySelector('.flex.gap-2');
    if (buttonContainer) {
        buttonContainer.appendChild(debugButton);
    }
}

// ===========================
// MODAL MANAGEMENT
// ===========================

// Close edit task modal
function closeEditTaskModal() {
    const modal = document.querySelector('.fixed.inset-0');
    if (modal) {
        modal.remove();
    }
}

// ===========================
// UTILITY FUNCTIONS
// ===========================

// Get agent ID from the page (from template or URL)
function getAgentIdFromPage() {
    // Try to get from window.agentData first
    if (window.agentData && window.agentData.id) {
        return window.agentData.id;
    }
    
    // Try to extract from URL
    const pathParts = window.location.pathname.split('/');
    const agentIndex = pathParts.indexOf('agents');
    if (agentIndex !== -1 && pathParts[agentIndex + 1]) {
        return pathParts[agentIndex + 1];
    }
    
    // Try to get from a hidden input or data attribute
    const agentIdInput = document.querySelector('input[name="agent_id"]');
    if (agentIdInput) {
        return agentIdInput.value;
    }
    
    return null;
}

// Get CSRF token from the page
function getCSRFToken() {
    const csrfInput = document.querySelector('input[name="csrf_token"]');
    if (csrfInput) {
        return csrfInput.value;
    }
    
    // Try to get from meta tag
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    if (csrfMeta) {
        return csrfMeta.getAttribute('content');
    }
    
    return '';
}

// Safe notification function
function showNotificationSafe(message, isSuccess) {
    if (typeof showNotification === 'function') {
        showNotification(message, isSuccess);
    } else {
        console.log(`${isSuccess ? 'SUCCESS' : 'ERROR'}: ${message}`);
    }
}

// ===========================
// LEGACY FUNCTION STUBS
// ===========================

// Legacy task management functions (deprecated)
function addNewTaskOld() {
    showNotificationSafe('Task creation is now handled through the new Task Editor. This feature will be available in Sprint 18.', false);
    console.log('Add Task clicked - Feature in development for Sprint 18');
}

function deleteTaskOld(taskId) {
    if (confirm('Are you sure you want to delete this task?')) {
        showNotificationSafe('Task deletion will be available in Sprint 18.', false);
        console.log('Delete Task clicked for task:', taskId);
    }
}

/**
 * Delete a task
 */
async function deleteTask(taskUuid) {
    if (!taskUuid) {
        showNotificationSafe('Invalid task ID', false);
        return;
    }
    
    // Find the task to get its name for confirmation
    const task = window.agentTasks ? window.agentTasks.find(t => t.uuid === taskUuid) : null;
    const taskName = task ? task.name : 'this task';
    
    if (!confirm(`Are you sure you want to delete "${taskName}"? This action cannot be undone.`)) {
        return;
    }
    
    try {
        const agentId = getAgentIdFromPage();
        if (!agentId) {
            showNotificationSafe('Agent ID not found', false);
            return;
        }
        
        const response = await fetch(`/agents/api/${agentId}/tasks/${taskUuid}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotificationSafe('Task deleted successfully', true);
            // Reload page to show updated task list
            window.location.reload();
        } else {
            showNotificationSafe('Failed to delete task: ' + result.error, false);
        }
    } catch (error) {
        console.error('Error deleting task:', error);
        showNotificationSafe('Error deleting task: ' + error.message, false);
    }
}

// ===========================
// PUBLIC API
// ===========================

// Export functions for global access
window.TaskManagementAdvanced = {
    initialize: initializeTaskManagement,
    checkMigration: checkMigrationNeeded,
    updateCount: updateTaskCount,
    migrateLegacy: migrateLegacyInstructions,
    moveUp: moveTaskUp,
    moveDown: moveTaskDown,
    debugAPI: debugTaskAPI,
    closeEditModal: closeEditTaskModal
};

// Make functions globally available for onclick handlers
window.migrateLegacyInstructions = migrateLegacyInstructions;
window.moveTaskUp = moveTaskUp;
window.moveTaskDown = moveTaskDown;
window.closeEditTaskModal = closeEditTaskModal;
window.debugTaskAPI = debugTaskAPI;
window.addNewTaskOld = addNewTaskOld;
window.deleteTaskOld = deleteTaskOld;
