/**
 * Task Modal Management
 * Handles creation and management of task creation and edit modals
 */

// Global variables for task modal management
let taskInputFields = [];
let editTaskInputFields = [];
// let availableTools = []; // Removed to avoid conflicts - use window.TaskConfiguration.availableTools instead

/**
 * Add new task with modal
 */
function addNewTask() {
    // Create task creation modal
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div class="p-6">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-lg font-medium text-gray-900">Add New Task</h3>
                    <button type="button" onclick="this.closest('.fixed').remove()" 
                            class="text-gray-400 hover:text-gray-600">
                        <i class="bi bi-x-lg"></i>
                    </button>
                </div>
                <form id="taskCreateForm">
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <!-- Left Column: Basic Information -->
                        <div class="space-y-4">
                            <h4 class="text-md font-medium text-gray-900 border-b pb-2">Basic Information</h4>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Task Name *</label>
                                <input type="text" id="taskName" name="name" required 
                                       class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                                       placeholder="Enter task name">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Task Type *</label>
                                <select id="taskType" name="type" onchange="toggleTaskTypeFields()" 
                                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
                                    <option value="ai">AI Task (OpenAI Assistant)</option>
                                    <option value="tool">Tool Task (External Tools)</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
                                <textarea id="taskDescription" name="description" rows="3"
                                          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                                          placeholder="Describe what this task does..."></textarea>
                            </div>
                            
                            <!-- Output Configuration -->
                            <div class="border-t pt-4">
                                <h5 class="text-sm font-medium text-gray-900 mb-3">Output Configuration</h5>
                                <div class="grid grid-cols-2 gap-3">
                                    <div>
                                        <label class="block text-sm font-medium text-gray-700 mb-1">Output Variable</label>
                                        <input type="text" id="outputVariable" name="output_variable"
                                               class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                                               placeholder="e.g., analysis_result">
                                    </div>
                                    <div>
                                        <label class="block text-sm font-medium text-gray-700 mb-1">Output Type</label>
                                        <select id="outputType" name="output_type" 
                                                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
                                            <option value="text">Text</option>
                                            <option value="image">Image</option>
                                            <option value="json">JSON</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="mt-3">
                                    <label class="block text-sm font-medium text-gray-700 mb-1">Output Description</label>
                                    <textarea id="outputDescription" name="output_description" rows="2"
                                              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                                              placeholder="Describe what this task outputs..."></textarea>
                                </div>
                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-1">Output Rendering</label>
                                    <select id="outputRendering" name="output_rendering" 
                                            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
                                        <option value="text">Plain Text</option>
                                        <option value="markup">Markdown</option>
                                        <option value="html">HTML</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Right Column: Type-specific Configuration -->
                        <div class="space-y-4">
                            <!-- AI Task Configuration -->
                            <div id="aiTaskConfig" class="task-config">
                                <h4 class="text-md font-medium text-gray-900 border-b pb-2 flex items-center">
                                    <i class="bi bi-robot mr-2 text-blue-500"></i>
                                    AI Task Configuration
                                </h4>
                                <div class="space-y-4">
                                    <div>
                                        <label class="block text-sm font-medium text-gray-700 mb-1">Instructions *</label>
                                        <textarea id="aiInstructions" name="instructions" rows="4"
                                                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                                                  placeholder="Detailed instructions for the AI assistant..."></textarea>
                                    </div>
                                    <div>
                                        <label class="block text-sm font-medium text-gray-700 mb-1">Goals</label>
                                        <textarea id="aiGoals" name="goals" rows="2"
                                                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                                                  placeholder="What should be achieved by this task..."></textarea>
                                    </div>
                                    
                                    <!-- Input Fields Configuration -->
                                    <div class="border-t pt-4">
                                        <div class="flex justify-between items-center mb-3">
                                            <h5 class="text-sm font-medium text-gray-900">Input Fields</h5>
                                            <button type="button" onclick="addInputField()" 
                                                    class="btn btn-sm btn-outline text-xs">
                                                <i class="bi bi-plus mr-1"></i>Add Field
                                            </button>
                                        </div>
                                        <div id="inputFieldsContainer" class="space-y-3">
                                            <p class="text-sm text-gray-500">No input fields defined yet.</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Tool Task Configuration -->
                            <div id="toolTaskConfig" class="task-config hidden">
                                <h4 class="text-md font-medium text-gray-900 border-b pb-2 flex items-center">
                                    <i class="bi bi-tools mr-2 text-green-500"></i>
                                    Tool Task Configuration
                                </h4>
                                <div class="space-y-4">
                                    <div>
                                        <label class="block text-sm font-medium text-gray-700 mb-1">Select Tool *</label>
                                        <select id="toolSelect" name="tool_uuid" onchange="loadToolInputFields()"
                                                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
                                            <option value="">Choose a tool...</option>
                                        </select>
                                    </div>
                                    <div id="toolInputsContainer" class="space-y-3">
                                        <p class="text-sm text-gray-500">Select a tool to configure its inputs.</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="flex gap-3 mt-6 pt-4 border-t">
                        <button type="submit" class="btn btn-primary flex-1">
                            <i class="bi bi-plus mr-1"></i>
                            Create Task
                        </button>
                        <button type="button" onclick="this.closest('.fixed').remove()" 
                                class="btn btn-outline flex-1">
                            Cancel
                        </button>
                    </div>
                </form>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Initialize form
    loadAvailableToolsForModal();
    toggleTaskTypeFields();
    
    // Handle form submission
    document.getElementById('taskCreateForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        const formData = collectTaskFormData();
        await createTask(formData);
        modal.remove();
    });
    
    // Focus on name input
    document.getElementById('taskName').focus();
}

/**
 * Create a new task via API
 */
async function createTask(taskData) {
    try {
        console.log('Creating task with data:', taskData);
        
        const response = await fetch('/agents/api/task', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.csrfToken || ''
            },
            body: JSON.stringify({
                agent_id: window.agentData?.id || window.agentData?.uuid,
                task: taskData
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            console.log('Task created successfully:', result);
            // Show success notification
            if (typeof showNotification === 'function') {
                showNotification('Task created successfully!', true);
            }
            
            // Reload the page to show the new task
            setTimeout(() => {
                window.location.reload();
            }, 1000);
            
            return result;
        } else {
            console.error('Failed to create task:', result.error);
            if (typeof showNotification === 'function') {
                showNotification(`Failed to create task: ${result.error}`, false);
            }
            throw new Error(result.error || 'Failed to create task');
        }
    } catch (error) {
        console.error('Error creating task:', error);
        if (typeof showNotification === 'function') {
            showNotification(`Error creating task: ${error.message}`, false);
        }
        throw error;
    }
}

/**
 * Toggle between AI and Tool task configuration
 */
function toggleTaskTypeFields() {
    const taskType = document.getElementById('taskType')?.value;
    const aiConfig = document.getElementById('aiTaskConfig');
    const toolConfig = document.getElementById('toolTaskConfig');
    
    if (!taskType || !aiConfig || !toolConfig) return;
    
    if (taskType === 'ai') {
        aiConfig.classList.remove('hidden');
        toolConfig.classList.add('hidden');
    } else {
        aiConfig.classList.add('hidden');
        toolConfig.classList.remove('hidden');
    }
}

/**
 * Collect task form data
 */
function collectTaskFormData() {
    const formData = {
        name: document.getElementById('taskName')?.value || '',
        type: document.getElementById('taskType')?.value || 'ai',
        description: document.getElementById('taskDescription')?.value || '',
        output_variable: document.getElementById('outputVariable')?.value || '',
        output_type: document.getElementById('outputType')?.value || 'text',
        output_description: document.getElementById('outputDescription')?.value || '',
        output_rendering: document.getElementById('outputRendering')?.value || 'text'
    };
    
    if (formData.type === 'ai') {
        // Collect AI task configuration
        formData.ai_config = {
            instructions: document.getElementById('aiInstructions')?.value || '',
            goals: document.getElementById('aiGoals')?.value || '',
            input_fields: collectInputFields()
        };
    } else if (formData.type === 'tool') {
        // Collect Tool task configuration
        const selectedToolUuid = document.getElementById('toolSelect')?.value || '';
        const selectedTool = (window.TaskConfiguration?.availableTools || []).find(tool => tool.uuid === selectedToolUuid);
        
        formData.tool_config = {
            tool_uuid: selectedToolUuid,
            tool_name: selectedTool ? selectedTool.name : '',
            inputs: collectToolInputs(selectedTool)
        };
    }
    
    return formData;
}

/**
 * Collect input fields from the form
 */
function collectInputFields() {
    const inputFields = [];
    
    taskInputFields.forEach((field, index) => {
        const inputField = {
            field_name: document.querySelector(`[name="input_field_name_${index}"]`)?.value || '',
            field_type: document.querySelector(`[name="input_field_type_${index}"]`)?.value || 'text',
            display_label: document.querySelector(`[name="input_field_label_${index}"]`)?.value || '',
            description: document.querySelector(`[name="input_field_description_${index}"]`)?.value || '',
            default_value: document.querySelector(`[name="input_field_default_${index}"]`)?.value || '',
            required: document.querySelector(`[name="input_field_required_${index}"]`)?.checked || false
        };
        
        if (inputField.field_name.trim()) {
            inputFields.push(inputField);
        }
    });
    
    return inputFields;
}

/**
 * Collect tool-specific inputs
 */
function collectToolInputs(selectedTool) {
    const inputs = {};
    
    if (selectedTool && selectedTool.inputs) {
        selectedTool.inputs.forEach((input, index) => {
            const fieldName = `tool_input_${index}`;
            const inputElement = document.querySelector(`[name="${fieldName}"]`);
            if (inputElement) {
                inputs[input.name] = inputElement.value;
            }
        });
    }
    
    return inputs;
}

/**
 * Close edit task modal
 */
function closeEditTaskModal() {
    const modal = document.querySelector('.fixed.inset-0');
    if (modal) {
        modal.remove();
    }
    currentEditingTaskUuid = null;
}

/**
 * Edit existing task
 */
function editTask(taskUuid) {
    if (!taskUuid) {
        showNotification('Invalid task ID', false);
        return;
    }
    
    // Find the task in the global agent data
    const task = window.agentTasks ? window.agentTasks.find(t => t.uuid === taskUuid) : null;
    
    if (!task) {
        showNotification('Task not found', false);
        console.error('Task not found:', taskUuid);
        return;
    }
    
    console.log('Editing task:', task);
    
    // Set current editing task
    currentEditingTaskUuid = taskUuid;
    
    // Create edit task modal
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div class="p-6">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-lg font-medium text-gray-900">Edit Task: ${escapeHtml(task.name)}</h3>
                    <button type="button" onclick="closeEditTaskModal()" 
                            class="text-gray-400 hover:text-gray-600">
                        <i class="bi bi-x-lg"></i>
                    </button>
                </div>
                <form id="taskEditForm">
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <!-- Left Column: Basic Information -->
                        <div class="space-y-4">
                            <h4 class="text-md font-medium text-gray-900 border-b pb-2">Basic Information</h4>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Task Name *</label>
                                <input type="text" id="editTaskName" name="name" required 
                                       value="${escapeHtml(task.name || '')}"
                                       class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                                       placeholder="Enter task name">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Task Type *</label>
                                <select id="editTaskType" name="type" onchange="toggleEditTaskTypeFields()" 
                                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
                                    <option value="ai" ${task.type === 'ai' ? 'selected' : ''}>AI Task (OpenAI Assistant)</option>
                                    <option value="tool" ${task.type === 'tool' ? 'selected' : ''}>Tool Task (External Tools)</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
                                <textarea id="editTaskDescription" name="description" rows="3"
                                          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                                          placeholder="Describe what this task does...">${escapeHtml(task.description || '')}</textarea>
                            </div>
                        </div>
                        
                        <!-- Right Column: Output Configuration -->
                        <div class="space-y-4">
                            <h4 class="text-md font-medium text-gray-900 border-b pb-2">Output Configuration</h4>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Output Variable</label>
                                <input type="text" id="editOutputVariable" name="output_variable" 
                                       value="${escapeHtml(task.output_variable || '')}"
                                       class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                                       placeholder="Variable name for output">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Output Type</label>
                                <select id="editOutputType" name="output_type" 
                                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
                                    <option value="text" ${task.output_type === 'text' ? 'selected' : ''}>Text</option>
                                    <option value="image" ${task.output_type === 'image' ? 'selected' : ''}>Image</option>
                                    <option value="json" ${task.output_type === 'json' ? 'selected' : ''}>JSON</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Output Description</label>
                                <textarea id="editOutputDescription" name="output_description" rows="2"
                                          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                                          placeholder="Describe the expected output...">${escapeHtml(task.output_description || '')}</textarea>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Output Rendering</label>
                                <select id="editOutputRendering" name="output_rendering" 
                                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
                                    <option value="text" ${task.output_rendering === 'text' ? 'selected' : ''}>Plain Text</option>
                                    <option value="markup" ${task.output_rendering === 'markup' ? 'selected' : ''}>Markdown</option>
                                    <option value="html" ${task.output_rendering === 'html' ? 'selected' : ''}>HTML</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Task Type Specific Configuration -->
                    <div class="mt-6">
                        <!-- AI Task Configuration -->
                        <div id="editAiTaskConfig" class="${task.type === 'ai' ? '' : 'hidden'}">
                            <h4 class="text-md font-medium text-gray-900 border-b pb-2 mb-4">AI Assistant Configuration</h4>
                            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-1">Instructions</label>
                                    <textarea id="editAiInstructions" name="ai_instructions" rows="4"
                                              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                                              placeholder="Instructions for the AI assistant...">${escapeHtml(task.ai_config?.instructions || '')}</textarea>
                                </div>
                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-1">Goals</label>
                                    <textarea id="editAiGoals" name="ai_goals" rows="4"
                                              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                                              placeholder="Goals for this task...">${escapeHtml(task.ai_config?.goals || '')}</textarea>
                                </div>
                            </div>
                            
                            <!-- Input Fields Configuration -->
                            <div class="mt-4">
                                <div class="flex justify-between items-center mb-3">
                                    <label class="block text-sm font-medium text-gray-700">Input Fields</label>
                                    <button type="button" onclick="addEditInputField()" 
                                            class="btn btn-sm btn-outline">
                                        <i class="bi bi-plus mr-1"></i>
                                        Add Field
                                    </button>
                                </div>
                                <div id="editInputFieldsContainer">
                                    <!-- Input fields will be populated by JavaScript -->
                                </div>
                            </div>
                        </div>
                        
                        <!-- Tool Task Configuration -->
                        <div id="editToolTaskConfig" class="${task.type === 'tool' ? '' : 'hidden'}">
                            <h4 class="text-md font-medium text-gray-900 border-b pb-2 mb-4">Tool Configuration</h4>
                            <div class="space-y-4">
                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-1">Select Tool *</label>
                                    <select id="editToolSelect" name="tool_uuid" onchange="loadEditToolInputFields()" 
                                            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
                                        <option value="">Choose a tool...</option>
                                    </select>
                                </div>
                                <div id="editToolInputsContainer">
                                    <p class="text-sm text-gray-500">Select a tool to configure its inputs.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="flex gap-3 mt-6">
                        <button type="submit" class="btn btn-primary flex-1">
                            <i class="bi bi-check mr-1"></i>
                            Update Task
                        </button>
                        <button type="button" onclick="closeEditTaskModal()" 
                                class="btn btn-outline flex-1">
                            Cancel
                        </button>
                    </div>
                </form>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Initialize the edit form
    if (typeof initializeEditTaskForm === 'function') {
        initializeEditTaskForm(task);
    }
    
    // Handle form submission
    document.getElementById('taskEditForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        try {
            const formData = collectEditTaskFormData();
            console.log('Updating task with data:', formData);
            
            const agentId = window.agentData?.id;
            if (!agentId) {
                throw new Error('Agent ID not found');
            }
            
            const response = await fetch(`/agents/api/${agentId}/tasks/${taskUuid}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('input[name="csrf_token"]')?.value || ''
                },
                body: JSON.stringify(formData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                showNotification('Task updated successfully!', true);
                closeEditTaskModal();
                // Reload page to show updated task
                window.location.reload();
            } else {
                showNotification('Failed to update task: ' + result.error, false);
            }
        } catch (error) {
            console.error('Error updating task:', error);
            showNotification('Error updating task: ' + error.message, false);
        }
    });
    
    // Focus on task name input
    setTimeout(() => {
        document.getElementById('editTaskName')?.focus();
    }, 100);
}

// Make functions globally available
window.addNewTask = addNewTask;
window.editTask = editTask;
window.createTask = createTask;
window.toggleTaskTypeFields = toggleTaskTypeFields;
window.closeEditTaskModal = closeEditTaskModal;
window.collectTaskFormData = collectTaskFormData;
