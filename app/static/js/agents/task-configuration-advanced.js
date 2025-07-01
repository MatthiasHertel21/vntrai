/**
 * Task Configuration Advanced Module
 * Handles complex task configuration features including tool loading, field generation, and form data collection
 */

// ===========================
// TASK CONFIGURATION CORE
// ===========================

// Global configuration object to avoid variable conflicts
window.TaskConfiguration = window.TaskConfiguration || {
    availableTools: [],
    taskInputFields: [],
    editTaskInputFields: []
};

// Flag to prevent double initialization
let taskConfigurationInitialized = false;

// Initialize task configuration system
function initializeTaskConfiguration() {
    if (taskConfigurationInitialized) {
        console.log('Task configuration already initialized, skipping...');
        return;
    }
    
    taskConfigurationInitialized = true;
    console.log('Initializing task configuration...');
    
    // Load available tools when needed
    loadAvailableToolsForModal();
    
    // Set up event listeners for task configuration
    setupTaskConfigurationListeners();
}

// Set up event listeners for task configuration
function setupTaskConfigurationListeners() {
    // Tool selection change handlers
    document.addEventListener('change', function(e) {
        if (e.target.id === 'toolSelect') {
            loadToolInputFields();
        }
        if (e.target.id === 'editToolSelect') {
            loadEditToolInputFields();
        }
        if (e.target.id === 'taskType') {
            toggleTaskTypeFields();
        }
        if (e.target.id === 'editTaskType') {
            toggleEditTaskTypeFields();
        }
    });
}

// ===========================
// TASK TYPE TOGGLE FUNCTIONS
// ===========================

// Toggle between AI and Tool task configuration
function toggleTaskTypeFields() {
    const taskType = document.getElementById('taskType');
    const aiConfig = document.getElementById('aiTaskConfig');
    const toolConfig = document.getElementById('toolTaskConfig');
    
    if (!taskType || !aiConfig || !toolConfig) return;
    
    if (taskType.value === 'ai') {
        aiConfig.classList.remove('hidden');
        toolConfig.classList.add('hidden');
    } else {
        aiConfig.classList.add('hidden');
        toolConfig.classList.remove('hidden');
    }
}

// Toggle edit task type fields
function toggleEditTaskTypeFields() {
    const taskType = document.getElementById('editTaskType');
    const aiConfig = document.getElementById('editAiTaskConfig');
    const toolConfig = document.getElementById('editToolTaskConfig');
    
    if (!taskType || !aiConfig || !toolConfig) return;
    
    if (taskType.value === 'ai') {
        aiConfig.classList.remove('hidden');
        toolConfig.classList.add('hidden');
    } else {
        aiConfig.classList.add('hidden');
        toolConfig.classList.remove('hidden');
    }
}

// ===========================
// TOOL LOADING FUNCTIONS
// ===========================

// Load available tools for the modal
async function loadAvailableToolsForModal() {
    try {
        const response = await fetch('/agents/api/tools');
        const data = await response.json();
        
        if (data.success) {
            window.TaskConfiguration.availableTools = data.tools;
            // Use requestAnimationFrame to avoid forced reflow
            requestAnimationFrame(() => {
                populateToolSelectModal();
            });
        } else {
            console.error('Failed to load tools:', data.error);
        }
    } catch (error) {
        console.error('Error loading tools:', error);
    }
}

// Populate tool select modal
function populateToolSelectModal() {
    const toolSelect = document.getElementById('toolSelect');
    if (!toolSelect) return;
    
    // Clear existing options except the first one
    toolSelect.innerHTML = '<option value="">Choose a tool...</option>';
    
    // Group tools by category
    const tools = window.TaskConfiguration.availableTools;
    const aiTools = tools.filter(tool => tool.category === 'AI' || tool.node_type === 'Agent');
    const otherTools = tools.filter(tool => tool.category !== 'AI' && tool.node_type !== 'Agent');
    
    // Add AI Tools group
    if (aiTools.length > 0) {
        const aiGroup = document.createElement('optgroup');
        aiGroup.label = 'AI Tools';
        aiTools.forEach(tool => {
            const option = document.createElement('option');
            option.value = tool.uuid;
            option.textContent = `${tool.name} - ${(tool.description || '').substring(0, 50)}${(tool.description || '').length > 50 ? '...' : ''}`;
            aiGroup.appendChild(option);
        });
        toolSelect.appendChild(aiGroup);
    }
    
    // Add Other Tools group
    if (otherTools.length > 0) {
        const toolsGroup = document.createElement('optgroup');
        toolsGroup.label = 'System Tools';
        otherTools.forEach(tool => {
            const option = document.createElement('option');
            option.value = tool.uuid;
            option.textContent = `${tool.name} - ${(tool.description || '').substring(0, 50)}${(tool.description || '').length > 50 ? '...' : ''}`;
            toolsGroup.appendChild(option);
        });
        toolSelect.appendChild(toolsGroup);
    }
}

// Load available tools for edit modal
async function loadAvailableToolsForEditModal() {
    try {
        console.log('Loading tools for edit modal...');
        const response = await fetch('/agents/api/tools');
        console.log('Tools response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Tools data received:', data);
        
        if (data.success && data.tools) {
            window.TaskConfiguration.availableTools = data.tools;
            console.log('Available tools loaded:', window.TaskConfiguration.availableTools.length);
            populateEditToolSelectModal();
        } else {
            console.error('Failed to load tools:', data.error || 'No tools data');
            const toolSelect = document.getElementById('editToolSelect');
            if (toolSelect) {
                toolSelect.innerHTML = '<option value="">Error loading tools</option>';
            }
        }
    } catch (error) {
        console.error('Error loading tools:', error);
        const toolSelect = document.getElementById('editToolSelect');
        if (toolSelect) {
            toolSelect.innerHTML = '<option value="">Error loading tools</option>';
        }
    }
}

// Populate edit tool select modal
function populateEditToolSelectModal() {
    const toolSelect = document.getElementById('editToolSelect');
    if (!toolSelect) {
        console.error('editToolSelect element not found');
        return;
    }
    
    const tools = window.TaskConfiguration.availableTools;
    console.log('Populating tool select with', tools.length, 'tools');
    
    // Clear existing options except the first one
    toolSelect.innerHTML = '<option value="">Choose a tool...</option>';
    
    if (!tools || tools.length === 0) {
        toolSelect.innerHTML = '<option value="">No tools available</option>';
        return;
    }
    
    // Group tools by category
    const aiTools = tools.filter(tool => tool.category === 'AI' || tool.node_type === 'Agent');
    const otherTools = tools.filter(tool => tool.category !== 'AI' && tool.node_type !== 'Agent');
    
    console.log('AI Tools:', aiTools.length, 'Other Tools:', otherTools.length);
    
    // Add AI Tools group
    if (aiTools.length > 0) {
        const aiGroup = document.createElement('optgroup');
        aiGroup.label = 'AI Tools';
        aiTools.forEach(tool => {
            const option = document.createElement('option');
            option.value = tool.uuid;
            option.textContent = `${tool.name} - ${(tool.description || '').substring(0, 50)}${(tool.description || '').length > 50 ? '...' : ''}`;
            aiGroup.appendChild(option);
        });
        toolSelect.appendChild(aiGroup);
    }
    
    // Add Other Tools group
    if (otherTools.length > 0) {
        const toolsGroup = document.createElement('optgroup');
        toolsGroup.label = 'System Tools';
        otherTools.forEach(tool => {
            const option = document.createElement('option');
            option.value = tool.uuid;
            option.textContent = `${tool.name} - ${(tool.description || '').substring(0, 50)}${(tool.description || '').length > 50 ? '...' : ''}`;
            toolsGroup.appendChild(option);
        });
        toolSelect.appendChild(toolsGroup);
    }
    
    console.log('Tool select populated with options:', toolSelect.options.length);
}

// ===========================
// TOOL INPUT FIELD FUNCTIONS
// ===========================

// Load tool-specific input fields when a tool is selected
function loadToolInputFields() {
    const toolSelect = document.getElementById('toolSelect');
    const toolInputsContainer = document.getElementById('toolInputsContainer');
    
    if (!toolSelect || !toolInputsContainer) return;
    
    const selectedToolUuid = toolSelect.value;
    
    if (!selectedToolUuid) {
        toolInputsContainer.innerHTML = '<p class="text-sm text-gray-500">Select a tool to configure its inputs.</p>';
        return;
    }
    
    // Find the selected tool
    const selectedTool = window.TaskConfiguration.availableTools.find(tool => tool.uuid === selectedToolUuid);
    if (!selectedTool) {
        toolInputsContainer.innerHTML = '<p class="text-sm text-red-500">Tool not found.</p>';
        return;
    }
    
    // Display tool information
    let toolInputsHtml = `
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
            <h6 class="font-medium text-blue-900">${selectedTool.name}</h6>
            <p class="text-sm text-blue-700">${selectedTool.description || 'No description available'}</p>
        </div>
    `;
    
    // Load tool inputs from integration or tool definition
    const toolInputs = selectedTool.inputs || [];
    
    if (toolInputs.length > 0) {
        toolInputsHtml += '<div class="space-y-3">';
        toolInputs.forEach((input, index) => {
            toolInputsHtml += `
                <div class="border border-gray-200 rounded-lg p-3">
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                        ${input.display_name || input.name}
                        ${input.required ? '<span class="text-red-500">*</span>' : ''}
                    </label>
                    ${generateInputField(input, index)}
                    ${input.description ? `<p class="text-xs text-gray-500 mt-1">${input.description}</p>` : ''}
                </div>
            `;
        });
        toolInputsHtml += '</div>';
    } else {
        toolInputsHtml += '<p class="text-sm text-gray-500">This tool has no configurable inputs.</p>';
    }
    
    toolInputsContainer.innerHTML = toolInputsHtml;
}

// Load edit tool input fields
function loadEditToolInputFields(existingInputs = {}) {
    const toolSelect = document.getElementById('editToolSelect');
    const toolInputsContainer = document.getElementById('editToolInputsContainer');
    
    if (!toolSelect || !toolInputsContainer) return;
    
    const selectedToolUuid = toolSelect.value;
    
    if (!selectedToolUuid) {
        toolInputsContainer.innerHTML = '<p class="text-sm text-gray-500">Select a tool to configure its inputs.</p>';
        return;
    }
    
    // Find the selected tool
    const selectedTool = window.TaskConfiguration.availableTools.find(tool => tool.uuid === selectedToolUuid);
    if (!selectedTool) {
        toolInputsContainer.innerHTML = '<p class="text-sm text-red-500">Tool not found.</p>';
        return;
    }
    
    // Display tool information
    let toolInputsHtml = `
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
            <h6 class="font-medium text-blue-900">${selectedTool.name}</h6>
            <p class="text-sm text-blue-700">${selectedTool.description || 'No description available'}</p>
        </div>
    `;
    
    // Load tool inputs from integration or tool definition
    const toolInputs = selectedTool.inputs || [];
    
    if (toolInputs.length > 0) {
        toolInputsHtml += '<div class="space-y-3">';
        toolInputs.forEach((input, index) => {
            const existingValue = existingInputs[input.name] || input.default || '';
            toolInputsHtml += `
                <div class="border border-gray-200 rounded-lg p-3">
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                        ${input.display_name || input.name}
                        ${input.required ? '<span class="text-red-500">*</span>' : ''}
                    </label>
                    ${generateEditInputField(input, index, existingValue)}
                    ${input.description ? `<p class="text-xs text-gray-500 mt-1">${input.description}</p>` : ''}
                </div>
            `;
        });
        toolInputsHtml += '</div>';
    } else {
        toolInputsHtml += '<p class="text-sm text-gray-500">This tool has no configurable inputs.</p>';
    }
    
    toolInputsContainer.innerHTML = toolInputsHtml;
}

// ===========================
// INPUT FIELD GENERATION
// ===========================

// Generate HTML for different input field types
function generateInputField(input, index) {
    const fieldName = `tool_input_${index}`;
    const fieldType = input.type || 'text';
    const required = input.required ? 'required' : '';
    const value = input.default || '';
    
    switch (fieldType) {
        case 'textarea':
            return `<textarea name="${fieldName}" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500" rows="3" ${required} placeholder="${input.placeholder || ''}">${escapeHtml(value)}</textarea>`;
        
        case 'number':
            return `<input type="number" name="${fieldName}" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500" ${required} value="${escapeHtml(value)}" placeholder="${input.placeholder || ''}" ${input.min ? `min="${input.min}"` : ''} ${input.max ? `max="${input.max}"` : ''}>`;
        
        case 'date':
            return `<input type="date" name="${fieldName}" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500" ${required} value="${escapeHtml(value)}">`;
        
        case 'select':
            let selectHtml = `<select name="${fieldName}" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500" ${required}>`;
            if (!required) {
                selectHtml += '<option value="">Select an option...</option>';
            }
            if (input.options) {
                input.options.forEach(option => {
                    const selected = option.value === value ? 'selected' : '';
                    selectHtml += `<option value="${option.value}" ${selected}>${option.label}</option>`;
                });
            }
            selectHtml += '</select>';
            return selectHtml;
        
        case 'option':
        case 'radio':
            let radioHtml = '<div class="space-y-2">';
            if (input.options) {
                input.options.forEach((option, optIndex) => {
                    const checked = option.value === value ? 'checked' : '';
                    radioHtml += `
                        <label class="flex items-center">
                            <input type="radio" name="${fieldName}" value="${option.value}" ${checked} ${required} class="mr-2">
                            <span class="text-sm">${option.label}</span>
                        </label>
                    `;
                });
            }
            radioHtml += '</div>';
            return radioHtml;
        
        default: // text
            return `<input type="text" name="${fieldName}" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500" ${required} value="${escapeHtml(value)}" placeholder="${input.placeholder || ''}">`;
    }
}

// Generate edit input field
function generateEditInputField(input, index, value) {
    const fieldName = `edit_tool_input_${index}`;
    const fieldType = input.type || 'text';
    const required = input.required ? 'required' : '';
    
    switch (fieldType) {
        case 'textarea':
            return `<textarea name="${fieldName}" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500" rows="3" ${required} placeholder="${input.placeholder || ''}">${escapeHtml(value)}</textarea>`;
        
        case 'number':
            return `<input type="number" name="${fieldName}" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500" ${required} value="${escapeHtml(value)}" placeholder="${input.placeholder || ''}" ${input.min ? `min="${input.min}"` : ''} ${input.max ? `max="${input.max}"` : ''}>`;
        
        case 'date':
            return `<input type="date" name="${fieldName}" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500" ${required} value="${escapeHtml(value)}">`;
        
        case 'select':
            let selectHtml = `<select name="${fieldName}" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500" ${required}>`;
            if (!required) {
                selectHtml += '<option value="">Select an option...</option>';
            }
            if (input.options) {
                input.options.forEach(option => {
                    const selected = option.value === value ? 'selected' : '';
                    selectHtml += `<option value="${option.value}" ${selected}>${option.label}</option>`;
                });
            }
            selectHtml += '</select>';
            return selectHtml;
        
        case 'option':
        case 'radio':
            let radioHtml = '<div class="space-y-2">';
            if (input.options) {
                input.options.forEach((option, optIndex) => {
                    const checked = option.value === value ? 'checked' : '';
                    radioHtml += `
                        <label class="flex items-center">
                            <input type="radio" name="${fieldName}" value="${option.value}" ${checked} ${required} class="mr-2">
                            <span class="text-sm">${option.label}</span>
                        </label>
                    `;
                });
            }
            radioHtml += '</div>';
            return radioHtml;
        
        default: // text
            return `<input type="text" name="${fieldName}" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500" ${required} value="${escapeHtml(value)}" placeholder="${input.placeholder || ''}">`;
    }
}

// ===========================
// INPUT FIELD MANAGEMENT
// ===========================

// Populate edit input fields
function populateEditInputFields(inputFields) {
    const container = document.getElementById('editInputFieldsContainer');
    if (!container) return;
    
    window.TaskConfiguration.editTaskInputFields = [];
    
    if (!inputFields || inputFields.length === 0) {
        container.innerHTML = '<p class="text-sm text-gray-500">No input fields defined yet.</p>';
        return;
    }
    
    container.innerHTML = '';
    
    inputFields.forEach((field, index) => {
        window.TaskConfiguration.editTaskInputFields.push({ index, data: field });
        const fieldHtml = `
            <div class="border border-gray-200 rounded p-2 bg-gray-50" data-field-index="${index}">
                <div class="flex justify-between items-start mb-2">
                    <div class="flex items-center gap-2">
                        <span class="text-xs font-medium text-gray-700">Field ${index + 1}</span>
                        <label class="flex items-center">
                            <input type="checkbox" name="edit_input_field_required_${index}" 
                                   class="mr-1 text-xs" ${field.required ? 'checked' : ''}>
                            <span class="text-xs text-gray-600">Required</span>
                        </label>
                    </div>
                    <button type="button" onclick="removeEditInputField(${index})" 
                            class="text-red-500 hover:text-red-700 text-xs">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
                <div class="grid grid-cols-3 gap-2 mb-2">
                    <div>
                        <label class="block text-xs text-gray-600 mb-1">Name *</label>
                        <input type="text" name="edit_input_field_name_${index}" 
                               class="w-full px-2 py-1 text-xs border border-gray-300 rounded focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                               placeholder="field_name" value="${escapeHtml(field.field_name || '')}">
                    </div>
                    <div>
                        <label class="block text-xs text-gray-600 mb-1">Type</label>
                        <select name="edit_input_field_type_${index}" 
                                class="w-full px-2 py-1 text-xs border border-gray-300 rounded focus:ring-1 focus:ring-blue-500 focus:border-blue-500">
                            <option value="text" ${field.field_type === 'text' ? 'selected' : ''}>Text</option>
                            <option value="textarea" ${field.field_type === 'textarea' ? 'selected' : ''}>Textarea</option>
                            <option value="number" ${field.field_type === 'number' ? 'selected' : ''}>Number</option>
                            <option value="date" ${field.field_type === 'date' ? 'selected' : ''}>Date</option>
                            <option value="select" ${field.field_type === 'select' ? 'selected' : ''}>Select</option>
                            <option value="option" ${field.field_type === 'option' ? 'selected' : ''}>Radio</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs text-gray-600 mb-1">Default</label>
                        <input type="text" name="edit_input_field_default_${index}" 
                               class="w-full px-2 py-1 text-xs border border-gray-300 rounded focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                               placeholder="Default value" value="${escapeHtml(field.default_value || '')}">
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-2 mb-2">
                    <div>
                        <label class="block text-xs text-gray-600 mb-1">Label</label>
                        <input type="text" name="edit_input_field_label_${index}" 
                               class="w-full px-2 py-1 text-xs border border-gray-300 rounded focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                               placeholder="Display Label" value="${escapeHtml(field.display_label || '')}">
                    </div>
                    <div>
                        <label class="block text-xs text-gray-600 mb-1">Description</label>
                        <input type="text" name="edit_input_field_description_${index}" 
                               class="w-full px-2 py-1 text-xs border border-gray-300 rounded focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                               placeholder="Help text" value="${escapeHtml(field.description || '')}">
                    </div>
                </div>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', fieldHtml);
    });
}

// Add edit input field
function addEditInputField() {
    const container = document.getElementById('editInputFieldsContainer');
    if (!container) return;
    
    // Remove "no fields" message if present
    const noFieldsMsg = container.querySelector('p');
    if (noFieldsMsg && noFieldsMsg.textContent.includes('No input fields')) {
        noFieldsMsg.remove();
    }
    
    const fieldIndex = window.TaskConfiguration.editTaskInputFields.length;
    
    const fieldHtml = `
        <div class="border border-gray-200 rounded p-2 bg-gray-50" data-field-index="${fieldIndex}">
            <div class="flex justify-between items-start mb-2">
                <div class="flex items-center gap-2">
                    <span class="text-xs font-medium text-gray-700">Field ${fieldIndex + 1}</span>
                    <label class="flex items-center">
                        <input type="checkbox" name="edit_input_field_required_${fieldIndex}" 
                               class="mr-1 text-xs">
                        <span class="text-xs text-gray-600">Required</span>
                    </label>
                </div>
                <button type="button" onclick="removeEditInputField(${fieldIndex})" 
                        class="text-red-500 hover:text-red-700 text-xs">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
            <div class="grid grid-cols-3 gap-2 mb-2">
                <div>
                    <label class="block text-xs text-gray-600 mb-1">Name *</label>
                    <input type="text" name="edit_input_field_name_${fieldIndex}" 
                           class="w-full px-2 py-1 text-xs border border-gray-300 rounded focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                           placeholder="field_name" value="field_${fieldIndex + 1}">
                </div>
                <div>
                    <label class="block text-xs text-gray-600 mb-1">Type</label>
                    <select name="edit_input_field_type_${fieldIndex}" 
                            class="w-full px-2 py-1 text-xs border border-gray-300 rounded focus:ring-1 focus:ring-blue-500 focus:border-blue-500">
                        <option value="text">Text</option>
                        <option value="textarea">Textarea</option>
                        <option value="number">Number</option>
                        <option value="date">Date</option>
                        <option value="select">Select</option>
                        <option value="option">Radio</option>
                    </select>
                </div>
                <div>
                    <label class="block text-xs text-gray-600 mb-1">Default</label>
                    <input type="text" name="edit_input_field_default_${fieldIndex}" 
                           class="w-full px-2 py-1 text-xs border border-gray-300 rounded focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                           placeholder="Default value">
                </div>
            </div>
            <div class="grid grid-cols-2 gap-2 mb-2">
                <div>
                    <label class="block text-xs text-gray-600 mb-1">Label</label>
                    <input type="text" name="edit_input_field_label_${fieldIndex}" 
                           class="w-full px-2 py-1 text-xs border border-gray-300 rounded focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                           placeholder="Display Label" value="Field ${fieldIndex + 1}">
                </div>
                <div>
                    <label class="block text-xs text-gray-600 mb-1">Description</label>
                    <input type="text" name="edit_input_field_description_${fieldIndex}" 
                           class="w-full px-2 py-1 text-xs border border-gray-300 rounded focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                           placeholder="Help text">
                </div>
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', fieldHtml);
    window.TaskConfiguration.editTaskInputFields.push({ index: fieldIndex });
}

// Remove edit input field
function removeEditInputField(fieldIndex) {
    const fieldElement = document.querySelector(`[data-field-index="${fieldIndex}"]`);
    if (fieldElement) {
        fieldElement.remove();
        window.TaskConfiguration.editTaskInputFields = window.TaskConfiguration.editTaskInputFields.filter(f => f.index !== fieldIndex);
        
        // Show "no fields" message if no fields remain
        const container = document.getElementById('editInputFieldsContainer');
        if (container && container.children.length === 0) {
            container.innerHTML = '<p class="text-sm text-gray-500">No input fields defined yet.</p>';
        }
    }
}

// ===========================
// FORM DATA COLLECTION
// ===========================

// Collect edit task form data
function collectEditTaskFormData() {
    const formData = {
        name: document.getElementById('editTaskName')?.value || '',
        type: document.getElementById('editTaskType')?.value || 'ai',
        description: document.getElementById('editTaskDescription')?.value || '',
        output_variable: document.getElementById('editOutputVariable')?.value || '',
        output_type: document.getElementById('editOutputType')?.value || '',
        output_description: document.getElementById('editOutputDescription')?.value || '',
        output_rendering: document.getElementById('editOutputRendering')?.value || ''
    };
    
    if (formData.type === 'ai') {
        // Collect AI task configuration
        formData.ai_config = {
            instructions: document.getElementById('editAiInstructions')?.value || '',
            goals: document.getElementById('editAiGoals')?.value || '',
            input_fields: []
        };
        
        // Collect input fields
        window.TaskConfiguration.editTaskInputFields.forEach(field => {
            const fieldIndex = field.index;
            const inputField = {
                field_name: document.querySelector(`[name="edit_input_field_name_${fieldIndex}"]`)?.value || '',
                field_type: document.querySelector(`[name="edit_input_field_type_${fieldIndex}"]`)?.value || 'text',
                display_label: document.querySelector(`[name="edit_input_field_label_${fieldIndex}"]`)?.value || '',
                description: document.querySelector(`[name="edit_input_field_description_${fieldIndex}"]`)?.value || '',
                default_value: document.querySelector(`[name="edit_input_field_default_${fieldIndex}"]`)?.value || '',
                required: document.querySelector(`[name="edit_input_field_required_${fieldIndex}"]`)?.checked || false
            };
            
            if (inputField.field_name.trim()) {
                formData.ai_config.input_fields.push(inputField);
            }
        });
        
    } else if (formData.type === 'tool') {
        // Collect Tool task configuration
        const selectedToolUuid = document.getElementById('editToolSelect')?.value || '';
        const selectedTool = window.TaskConfiguration.availableTools.find(tool => tool.uuid === selectedToolUuid);
        
        formData.tool_config = {
            tool_uuid: selectedToolUuid,
            tool_name: selectedTool ? selectedTool.name : '',
            inputs: {}
        };
        
        // Collect tool-specific inputs
        if (selectedTool && selectedTool.inputs) {
            selectedTool.inputs.forEach((input, index) => {
                const fieldName = `edit_tool_input_${index}`;
                const inputElement = document.querySelector(`[name="${fieldName}"]`);
                if (inputElement) {
                    formData.tool_config.inputs[input.name] = inputElement.value;
                }
            });
        }
    }
    
    return formData;
}

// ===========================
// TASK INITIALIZATION
// ===========================

// Initialize edit task form
function initializeEditTaskForm(task) {
    // Load available tools first
    loadAvailableToolsForEditModal().then(() => {
        // Set task type and toggle fields
        toggleEditTaskTypeFields();
        
        if (task.type === 'ai' && task.ai_config) {
            // Populate AI task input fields
            populateEditInputFields(task.ai_config.input_fields || []);
        } else if (task.type === 'tool' && task.tool_config) {
            // Select tool and populate tool inputs
            const editToolSelect = document.getElementById('editToolSelect');
            if (editToolSelect && task.tool_config.tool_uuid) {
                editToolSelect.value = task.tool_config.tool_uuid;
                loadEditToolInputFields(task.tool_config.inputs || {});
            }
        }
    });
}

// ===========================
// UTILITY FUNCTIONS
// ===========================

// Escape HTML to prevent XSS
function escapeHtml(text) {
    if (typeof text !== 'string') return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ===========================
// PUBLIC API
// ===========================

// Export functions to global scope for backward compatibility
window.toggleTaskTypeFields = toggleTaskTypeFields;
window.toggleEditTaskTypeFields = toggleEditTaskTypeFields;
window.loadAvailableToolsForModal = loadAvailableToolsForModal;
window.loadAvailableToolsForEditModal = loadAvailableToolsForEditModal;
window.loadToolInputFields = loadToolInputFields;
window.loadEditToolInputFields = loadEditToolInputFields;
window.populateEditInputFields = populateEditInputFields;
window.addEditInputField = addEditInputField;
window.removeEditInputField = removeEditInputField;
window.collectEditTaskFormData = collectEditTaskFormData;
window.initializeEditTaskForm = initializeEditTaskForm;

// Initialize when DOM is ready (but only if not already initialized by template)
document.addEventListener('DOMContentLoaded', function() {
    // Small delay to allow template initialization to run first
    setTimeout(() => {
        initializeTaskConfiguration();
    }, 100);
});

console.log('Task Configuration Advanced module loaded successfully');
