/**
 * Tool Integration Manager
 * Handles tool loading, selection, and configuration for task creation/editing
 */

/**
 * Load available tools for the modal
 */
async function loadAvailableToolsForModal() {
    try {
        const response = await fetch('/agents/api/tools');
        const data = await response.json();
        
        if (data.success) {
            availableTools = data.tools;
            populateToolSelectModal();
        } else {
            console.error('Failed to load tools:', data.error);
        }
    } catch (error) {
        console.error('Error loading tools:', error);
    }
}

/**
 * Populate tool select dropdown in creation modal
 */
function populateToolSelectModal() {
    const toolSelect = document.getElementById('toolSelect');
    if (!toolSelect) return;
    
    // Clear existing options except the first one
    toolSelect.innerHTML = '<option value="">Choose a tool...</option>';
    
    // Group tools by category
    const aiTools = availableTools.filter(tool => tool.category === 'AI' || tool.node_type === 'Agent');
    const otherTools = availableTools.filter(tool => tool.category !== 'AI' && tool.node_type !== 'Agent');
    
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

/**
 * Load tool-specific input fields when a tool is selected
 */
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
    const selectedTool = availableTools.find(tool => tool.uuid === selectedToolUuid);
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
                    ${generateInputField(input, index, '')}
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

/**
 * Generate HTML for different input field types
 */
function generateInputField(input, index, value = '') {
    const fieldName = `tool_input_${index}`;
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

/**
 * Load available tools for edit modal
 */
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
            availableTools = data.tools;
            console.log('Available tools loaded:', availableTools.length);
            populateEditToolSelectModal();
        } else {
            console.error('Failed to load tools:', data.error || 'No tools data');
            // Fallback: show error in select
            const toolSelect = document.getElementById('editToolSelect');
            if (toolSelect) {
                toolSelect.innerHTML = '<option value="">Error loading tools</option>';
            }
        }
    } catch (error) {
        console.error('Error loading tools:', error);
        // Fallback: show error in select
        const toolSelect = document.getElementById('editToolSelect');
        if (toolSelect) {
            toolSelect.innerHTML = '<option value="">Error loading tools</option>';
        }
    }
}

/**
 * Populate tool select dropdown in edit modal
 */
function populateEditToolSelectModal() {
    const toolSelect = document.getElementById('editToolSelect');
    if (!toolSelect) {
        console.error('editToolSelect element not found');
        return;
    }
    
    console.log('Populating tool select with', availableTools.length, 'tools');
    
    // Clear existing options except the first one
    toolSelect.innerHTML = '<option value="">Choose a tool...</option>';
    
    if (!availableTools || availableTools.length === 0) {
        toolSelect.innerHTML = '<option value="">No tools available</option>';
        return;
    }
    
    // Group tools by category
    const aiTools = availableTools.filter(tool => tool.category === 'AI' || tool.node_type === 'Agent');
    const otherTools = availableTools.filter(tool => tool.category !== 'AI' && tool.node_type !== 'Agent');
    
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

/**
 * Load tool input fields for edit modal
 */
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
    const selectedTool = availableTools.find(tool => tool.uuid === selectedToolUuid);
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

/**
 * Generate edit input field HTML
 */
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

// Make functions globally available
window.loadAvailableToolsForModal = loadAvailableToolsForModal;
window.loadToolInputFields = loadToolInputFields;
window.loadAvailableToolsForEditModal = loadAvailableToolsForEditModal;
window.loadEditToolInputFields = loadEditToolInputFields;
window.populateToolSelectModal = populateToolSelectModal;
window.populateEditToolSelectModal = populateEditToolSelectModal;
