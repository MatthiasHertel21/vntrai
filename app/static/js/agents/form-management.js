/**
 * Form Management Module
 * Handles form auto-save, validation, and change tracking for agent editing
 */

// ===========================
// FORM MANAGEMENT CORE
// ===========================

// Global variables for form management
let autoSaveTimeout = null;
let hasUnsavedChanges = false;
let initialFormData = {};

// Initialize form management system
function initializeFormManagement() {
    // Set up form change listeners
    setupFormChangeListeners();
    
    // Store initial form data for comparison
    storeInitialFormData();
    
    // Set up before unload warning
    setupBeforeUnloadWarning();
    
    // Set up form submission handling
    setupFormSubmissionHandling();
}

// Set up form change listeners
function setupFormChangeListeners() {
    const form = document.getElementById('agentEditForm');
    if (!form) return;
    
    const inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.addEventListener('change', handleFormChange);
        input.addEventListener('input', handleFormChange);
    });
}

// Handle form field changes
function handleFormChange(event) {
    markFormAsChanged();
    scheduleAutoSave();
    
    // Update specific field states if needed
    const element = event.target;
    
    if (element.id === 'name') {
        validateAgentName(element.value);
    } else if (element.id === 'description') {
        validateDescription(element.value);
    }
}

// Mark form as having unsaved changes
function markFormAsChanged() {
    hasUnsavedChanges = true;
    updateSaveButtonState();
}

// Mark form as saved
function markFormAsSaved() {
    hasUnsavedChanges = false;
    updateSaveButtonState();
}

// Update save button state
function updateSaveButtonState() {
    const saveButton = document.querySelector('button[type="submit"][form="agentEditForm"]');
    if (saveButton) {
        if (hasUnsavedChanges) {
            saveButton.classList.remove('btn-outline');
            saveButton.classList.add('btn-primary');
            saveButton.innerHTML = '<i class="bi bi-check-lg mr-2"></i>Save Changes';
        } else {
            saveButton.classList.remove('btn-primary');
            saveButton.classList.add('btn-outline');
            saveButton.innerHTML = '<i class="bi bi-check mr-2"></i>Saved';
        }
    }
}

// ===========================
// AUTO-SAVE FUNCTIONALITY
// ===========================

// Schedule auto-save
function scheduleAutoSave() {
    // Clear existing timeout
    if (autoSaveTimeout) {
        clearTimeout(autoSaveTimeout);
    }
    
    // Schedule new auto-save
    autoSaveTimeout = setTimeout(() => {
        performAutoSave();
    }, 2000); // Auto-save after 2 seconds of inactivity
}

// Perform auto-save
async function performAutoSave() {
    const form = document.getElementById('agentEditForm');
    if (!form || !hasUnsavedChanges) return;
    
    try {
        const formData = new FormData(form);
        formData.append('auto_save', 'true');
        
        const response = await fetch(form.action || window.location.pathname, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            markFormAsSaved();
            showAutoSaveIndicator(true);
            console.log('Auto-save successful');
        } else {
            showAutoSaveIndicator(false);
            console.error('Auto-save failed:', response.statusText);
        }
        
    } catch (error) {
        showAutoSaveIndicator(false);
        console.error('Auto-save error:', error);
    }
}

// Show auto-save indicator
function showAutoSaveIndicator(success) {
    // Remove existing indicators
    const existingIndicator = document.getElementById('autoSaveIndicator');
    if (existingIndicator) {
        existingIndicator.remove();
    }
    
    // Create new indicator
    const indicator = document.createElement('div');
    indicator.id = 'autoSaveIndicator';
    indicator.className = `fixed top-4 right-4 px-3 py-2 rounded-md text-sm font-medium z-50 ${
        success 
            ? 'bg-green-100 text-green-800 border border-green-200' 
            : 'bg-red-100 text-red-800 border border-red-200'
    }`;
    indicator.innerHTML = success 
        ? '<i class="bi bi-check-circle mr-1"></i>Auto-saved'
        : '<i class="bi bi-exclamation-circle mr-1"></i>Auto-save failed';
    
    document.body.appendChild(indicator);
    
    // Remove after 3 seconds
    setTimeout(() => {
        if (indicator.parentNode) {
            indicator.remove();
        }
    }, 3000);
}

// ===========================
// FORM VALIDATION
// ===========================

// Validate agent name
function validateAgentName(name) {
    const nameInput = document.getElementById('name');
    if (!nameInput) return true;
    
    const isValid = name.trim().length >= 3 && name.trim().length <= 100;
    
    if (isValid) {
        nameInput.classList.remove('border-red-500');
        nameInput.classList.add('border-green-500');
        removeFieldError('name');
    } else {
        nameInput.classList.remove('border-green-500');
        nameInput.classList.add('border-red-500');
        showFieldError('name', 'Agent name must be between 3 and 100 characters');
    }
    
    return isValid;
}

// Validate description
function validateDescription(description) {
    const descriptionInput = document.getElementById('description');
    if (!descriptionInput) return true;
    
    const isValid = description.length <= 1000;
    
    if (isValid) {
        descriptionInput.classList.remove('border-red-500');
        updateCharacterCount('description', description.length, 1000);
    } else {
        descriptionInput.classList.add('border-red-500');
        showFieldError('description', 'Description cannot exceed 1000 characters');
    }
    
    return isValid;
}

// Show field error
function showFieldError(fieldId, message) {
    removeFieldError(fieldId);
    
    const field = document.getElementById(fieldId);
    if (!field) return;
    
    const errorDiv = document.createElement('div');
    errorDiv.id = `${fieldId}_error`;
    errorDiv.className = 'text-red-500 text-xs mt-1';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

// Remove field error
function removeFieldError(fieldId) {
    const errorDiv = document.getElementById(`${fieldId}_error`);
    if (errorDiv) {
        errorDiv.remove();
    }
}

// Update character count
function updateCharacterCount(fieldId, currentLength, maxLength) {
    let countDiv = document.getElementById(`${fieldId}_count`);
    
    if (!countDiv) {
        const field = document.getElementById(fieldId);
        if (!field) return;
        
        countDiv = document.createElement('div');
        countDiv.id = `${fieldId}_count`;
        countDiv.className = 'text-xs text-gray-500 mt-1 text-right';
        field.parentNode.appendChild(countDiv);
    }
    
    countDiv.textContent = `${currentLength}/${maxLength} characters`;
    
    if (currentLength > maxLength) {
        countDiv.classList.remove('text-gray-500');
        countDiv.classList.add('text-red-500');
    } else {
        countDiv.classList.remove('text-red-500');
        countDiv.classList.add('text-gray-500');
    }
}

// ===========================
// FORM PERSISTENCE
// ===========================

// Store initial form data
function storeInitialFormData() {
    const form = document.getElementById('agentEditForm');
    if (!form) return;
    
    const formData = new FormData(form);
    initialFormData = {};
    
    for (const [key, value] of formData.entries()) {
        initialFormData[key] = value;
    }
}

// Check if form has been modified
function hasFormBeenModified() {
    const form = document.getElementById('agentEditForm');
    if (!form) return false;
    
    const currentFormData = new FormData(form);
    
    for (const [key, value] of currentFormData.entries()) {
        if (initialFormData[key] !== value) {
            return true;
        }
    }
    
    return false;
}

// ===========================
// NAVIGATION PROTECTION
// ===========================

// Set up before unload warning
function setupBeforeUnloadWarning() {
    window.addEventListener('beforeunload', function(e) {
        if (hasUnsavedChanges && hasFormBeenModified()) {
            e.preventDefault();
            e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
            return e.returnValue;
        }
    });
}

// Set up form submission handling
function setupFormSubmissionHandling() {
    const form = document.getElementById('agentEditForm');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        // Perform final validation
        if (!validateForm()) {
            e.preventDefault();
            return false;
        }
        
        // Mark as saved to prevent beforeunload warning
        markFormAsSaved();
        
        // Show loading state
        showFormSubmissionLoading();
    });
}

// Validate entire form
function validateForm() {
    let isValid = true;
    
    // Validate name
    const name = document.getElementById('name');
    if (name && !validateAgentName(name.value)) {
        isValid = false;
    }
    
    // Validate description
    const description = document.getElementById('description');
    if (description && !validateDescription(description.value)) {
        isValid = false;
    }
    
    // Validate AI assistant tool if required
    const assistantTool = document.getElementById('ai_assistant_tool');
    if (assistantTool && assistantTool.hasAttribute('required') && !assistantTool.value) {
        showFieldError('ai_assistant_tool', 'Please select an AI assistant tool');
        isValid = false;
    }
    
    return isValid;
}

// Show form submission loading state
function showFormSubmissionLoading() {
    const submitButton = document.querySelector('button[type="submit"][form="agentEditForm"]');
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="bi bi-hourglass-split mr-2"></i>Saving...';
    }
}

// ===========================
// UTILITY FUNCTIONS
// ===========================

// Reset form to initial state
function resetForm() {
    const form = document.getElementById('agentEditForm');
    if (!form) return;
    
    form.reset();
    markFormAsSaved();
    
    // Clear any validation errors
    const errorElements = form.querySelectorAll('[id$="_error"]');
    errorElements.forEach(element => element.remove());
    
    // Reset field styles
    const inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.classList.remove('border-red-500', 'border-green-500');
    });
}

// Get form data as object
function getFormDataAsObject() {
    const form = document.getElementById('agentEditForm');
    if (!form) return {};
    
    const formData = new FormData(form);
    const data = {};
    
    for (const [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    return data;
}

// ===========================
// PUBLIC API
// ===========================

// Export functions for global access
window.FormManagement = {
    initialize: initializeFormManagement,
    markChanged: markFormAsChanged,
    markSaved: markFormAsSaved,
    scheduleAutoSave: scheduleAutoSave,
    validateForm: validateForm,
    resetForm: resetForm,
    getFormData: getFormDataAsObject,
    hasChanges: () => hasUnsavedChanges
};

// Make functions globally available
window.scheduleAutoSave = scheduleAutoSave;
window.markFormAsChanged = markFormAsChanged;
window.markFormAsSaved = markFormAsSaved;

// Auto-initialize on DOM content loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeFormManagement();
});
