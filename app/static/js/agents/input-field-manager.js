/**
 * Input Field Management
 * Handles dynamic input field creation, editing, and management for tasks
 */

/**
 * Add new input field to the creation form
 */
function addInputField() {
    const container = document.getElementById('inputFieldsContainer');
    if (!container) return;
    
    // Remove "no fields" message if present
    const noFieldsMsg = container.querySelector('p');
    if (noFieldsMsg && noFieldsMsg.textContent.includes('No input fields')) {
        noFieldsMsg.remove();
    }
    
    const fieldIndex = taskInputFields.length;
    
    const fieldHtml = `
        <div class="border border-gray-200 rounded p-3 bg-gray-50" data-field-index="${fieldIndex}">
            <div class="flex justify-between items-start mb-3">
                <div class="flex items-center gap-2">
                    <span class="text-sm font-medium text-gray-700">Field ${fieldIndex + 1}</span>
                    <label class="flex items-center">
                        <input type="checkbox" name="input_field_required_${fieldIndex}" class="mr-1">
                        <span class="text-sm text-gray-600">Required</span>
                    </label>
                </div>
                <button type="button" onclick="removeInputField(${fieldIndex})" 
                        class="text-red-500 hover:text-red-700">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Field Name *</label>
                    <input type="text" name="input_field_name_${fieldIndex}" 
                           class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                           placeholder="field_name" value="field_${fieldIndex + 1}">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Field Type</label>
                    <select name="input_field_type_${fieldIndex}" 
                            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
                        <option value="text">Text</option>
                        <option value="textarea">Textarea</option>
                        <option value="number">Number</option>
                        <option value="date">Date</option>
                        <option value="select">Select</option>
                        <option value="option">Radio Options</option>
                    </select>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Display Label</label>
                    <input type="text" name="input_field_label_${fieldIndex}" 
                           class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                           placeholder="Display Label" value="Field ${fieldIndex + 1}">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Default Value</label>
                    <input type="text" name="input_field_default_${fieldIndex}" 
                           class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                           placeholder="Default value">
                </div>
            </div>
            <div class="mt-3">
                <label class="block text-sm font-medium text-gray-700 mb-1">Description/Help Text</label>
                <textarea name="input_field_description_${fieldIndex}" rows="2"
                          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                          placeholder="Help text for this field..."></textarea>
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', fieldHtml);
    taskInputFields.push({ index: fieldIndex });
}

/**
 * Remove input field from the creation form
 */
function removeInputField(fieldIndex) {
    const fieldElement = document.querySelector(`[data-field-index="${fieldIndex}"]`);
    if (fieldElement) {
        fieldElement.remove();
        taskInputFields = taskInputFields.filter(f => f.index !== fieldIndex);
        
        // Show "no fields" message if no fields remain
        const container = document.getElementById('inputFieldsContainer');
        if (container && container.children.length === 0) {
            container.innerHTML = '<p class="text-sm text-gray-500">No input fields defined yet.</p>';
        }
    }
}

/**
 * Add new input field to the edit form
 */
function addEditInputField() {
    const container = document.getElementById('editInputFieldsContainer');
    if (!container) return;
    
    // Remove "no fields" message if present
    const noFieldsMsg = container.querySelector('p');
    if (noFieldsMsg && noFieldsMsg.textContent.includes('No input fields')) {
        noFieldsMsg.remove();
    }
    
    const fieldIndex = editTaskInputFields.length;
    
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
            <!-- Name, Type, Default in one row -->
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
            <!-- Label and Description in one row -->
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
    editTaskInputFields.push({ index: fieldIndex });
}

/**
 * Remove input field from the edit form
 */
function removeEditInputField(fieldIndex) {
    const fieldElement = document.querySelector(`[data-field-index="${fieldIndex}"]`);
    if (fieldElement) {
        fieldElement.remove();
        editTaskInputFields = editTaskInputFields.filter(f => f.index !== fieldIndex);
        
        // Show "no fields" message if no fields remain
        const container = document.getElementById('editInputFieldsContainer');
        if (container && container.children.length === 0) {
            container.innerHTML = '<p class="text-sm text-gray-500">No input fields defined yet.</p>';
        }
    }
}

/**
 * Populate edit input fields with existing data
 */
function populateEditInputFields(inputFields) {
    const container = document.getElementById('editInputFieldsContainer');
    if (!container) return;
    
    editTaskInputFields = [];
    
    if (!inputFields || inputFields.length === 0) {
        container.innerHTML = '<p class="text-sm text-gray-500">No input fields defined yet.</p>';
        return;
    }
    
    container.innerHTML = '';
    
    inputFields.forEach((field, index) => {
        editTaskInputFields.push({ index, data: field });
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
                <!-- Name, Type, Default in one row -->
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
                <!-- Label and Description in one row -->
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

// Make functions globally available
window.addInputField = addInputField;
window.removeInputField = removeInputField;
window.addEditInputField = addEditInputField;
window.removeEditInputField = removeEditInputField;
window.populateEditInputFields = populateEditInputFields;
