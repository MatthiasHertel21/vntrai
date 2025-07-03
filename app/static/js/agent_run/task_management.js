// Task management logic for agent_run_view
// Handles active task selection, input autosave, and execution

window.activeTaskIndex = null;
window.taskDefinitions = window.taskDefinitions || [];
window.autoSaveTimeout = null;

function restoreActiveTask(uuid) {
    if (window.taskDefinitions.length === 0) return;
    
    // Use localStorage only since API endpoints don't exist yet
    const savedActiveTask = localStorage.getItem(`agentRun_${uuid}_activeTask`);
    if (savedActiveTask !== null && parseInt(savedActiveTask) < window.taskDefinitions.length) {
        selectTask(parseInt(savedActiveTask), uuid);
    } else {
        selectTask(0, uuid); // Default to first task
    }
}

function selectTask(taskIndex, uuid) {
    if (taskIndex < 0 || taskIndex >= window.taskDefinitions.length) return;
    document.querySelectorAll('.task-item').forEach(item => item.classList.remove('active'));
    const selectedTaskItem = document.querySelector(`[data-task-index="${taskIndex}"]`);
    if (selectedTaskItem) selectedTaskItem.classList.add('active');
    window.activeTaskIndex = taskIndex;
    saveActiveTaskSelection(taskIndex, uuid);
    showActiveTaskDetails(taskIndex);
}

function saveActiveTaskSelection(taskIndex, uuid) {
    // Save to localStorage  
    localStorage.setItem(`agentRun_${uuid}_activeTask`, taskIndex.toString());
    
    // Try to save to backend, but don't fail if it doesn't work
    fetch(`/agents/api/agent_run/${uuid}/selected_task`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        body: JSON.stringify({ task_index: taskIndex })
    }).catch(error => {
        console.log('Backend save failed, using localStorage only:', error);
    });
}

function showActiveTaskDetails(taskIndex) {
    console.log('showActiveTaskDetails called with taskIndex:', taskIndex);
    console.log('window.taskDefinitions:', window.taskDefinitions);
    
    const task = window.taskDefinitions[taskIndex];
    if (!task) {
        console.error('Task not found at index:', taskIndex);
        return;
    }
    
    console.log('Task data:', task);
    
    const detailsContainer = document.getElementById('activeTaskDetails');
    const descriptionContainer = document.getElementById('taskDescription');
    const inputFieldsContainer = document.getElementById('taskInputFields');
    
    if (!detailsContainer || !descriptionContainer || !inputFieldsContainer) {
        console.error('Required DOM elements not found');
        return;
    }
    
    detailsContainer.classList.remove('hidden');
    
    // Handle different task data structures - get description
    const description = task.description || 
                       task.definition?.description || 
                       'No description available';
    descriptionContainer.textContent = description;
    
    inputFieldsContainer.innerHTML = '';
    
    // Handle input fields based on task type and structure
    if (task.type === 'ai' || (task.definition && task.definition.type === 'ai')) {
        // For AI tasks, look for input_fields in ai_config
        const aiConfig = task.ai_config || task.definition?.ai_config;
        if (aiConfig && aiConfig.input_fields && Array.isArray(aiConfig.input_fields)) {
            aiConfig.input_fields.forEach(field => {
                createInputFieldFromDefinition(inputFieldsContainer, field, task);
            });
        } else {
            // Fallback: create default AI inputs if no input_fields defined
            createDefaultAIInputs(inputFieldsContainer, task);
        }
    } else if (task.type === 'tool' || (task.definition && task.definition.type === 'tool')) {
        // For tool tasks, we need to look up the tool definition
        // For now, create a placeholder - this would need integration with tool manager
        console.log('Tool task detected - tool definition lookup needed');
        const toolMessage = document.createElement('p');
        toolMessage.className = 'text-sm text-gray-500 italic';
        toolMessage.textContent = 'Tool input fields will be loaded dynamically...';
        inputFieldsContainer.appendChild(toolMessage);
    } else {
        // Check for input schema in different locations (fallback)
        let inputSchema = null;
        if (task.definition && task.definition.input_schema) {
            inputSchema = task.definition.input_schema;
        } else if (task.input_schema) {
            inputSchema = task.input_schema;
        } else if (task.config && task.config.input_schema) {
            inputSchema = task.config.input_schema;
        }
        
        if (inputSchema) {
            for (const [fieldName, fieldConfig] of Object.entries(inputSchema)) {
                createInputField(inputFieldsContainer, fieldName, fieldConfig, task);
            }
        } else {
            console.log('No input fields found for task type:', task.type);
        }
    }
}

function createInputFieldFromDefinition(container, fieldDef, task) {
    const fieldDiv = document.createElement('div');
    fieldDiv.className = 'space-y-1';
    
    const label = document.createElement('label');
    label.className = 'block text-xs font-medium text-gray-600';
    label.textContent = fieldDef.display_label || fieldDef.field_name || 'Field';
    
    let input;
    const fieldName = fieldDef.field_name;
    
    // Get saved value from different possible locations
    let savedValue = '';
    if (task.state && task.state.inputs && task.state.inputs[fieldName]) {
        savedValue = task.state.inputs[fieldName];
    } else if (task.inputs && task.inputs[fieldName]) {
        savedValue = task.inputs[fieldName];
    } else if (fieldDef.default_value) {
        savedValue = fieldDef.default_value;
    }
    
    if (fieldDef.field_type === 'textarea') {
        input = document.createElement('textarea');
        input.className = 'w-full text-xs border border-gray-300 rounded px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:border-blue-500';
        input.rows = 3;
        input.value = savedValue;
    } else {
        input = document.createElement('input');
        input.type = fieldDef.field_type || 'text';
        input.className = 'w-full text-xs border border-gray-300 rounded px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:border-blue-500';
        input.value = savedValue;
    }
    
    input.name = fieldName;
    input.placeholder = fieldDef.description || '';
    
    if (fieldDef.required) {
        input.required = true;
        label.innerHTML += ' <span class="text-red-500">*</span>';
    }
    
    input.addEventListener('input', scheduleAutoSave);
    input.addEventListener('blur', autoSaveTaskInputs);
    fieldDiv.appendChild(label);
    fieldDiv.appendChild(input);
    container.appendChild(fieldDiv);
}

function createInputField(container, fieldName, fieldConfig, task) {
    const fieldDiv = document.createElement('div');
    fieldDiv.className = 'space-y-1';
    const label = document.createElement('label');
    label.className = 'block text-xs font-medium text-gray-600';
    label.textContent = fieldConfig.label || fieldName;
    
    let input;
    
    // Get saved value from different possible locations
    let savedValue = '';
    if (task.state && task.state.inputs && task.state.inputs[fieldName]) {
        savedValue = task.state.inputs[fieldName];
    } else if (task.inputs && task.inputs[fieldName]) {
        savedValue = task.inputs[fieldName];
    } else if (fieldConfig.default) {
        savedValue = fieldConfig.default;
    }
    
    if (fieldConfig.type === 'textarea') {
        input = document.createElement('textarea');
        input.className = 'w-full text-xs border border-gray-300 rounded px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:border-blue-500';
        input.rows = 3;
        input.value = savedValue;
    } else {
        input = document.createElement('input');
        input.type = fieldConfig.type || 'text';
        input.className = 'w-full text-xs border border-gray-300 rounded px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:border-blue-500';
        input.value = savedValue;
    }
    
    input.name = fieldName;
    input.placeholder = fieldConfig.placeholder || '';
    
    if (fieldConfig.required) {
        input.required = true;
        label.innerHTML += ' <span class="text-red-500">*</span>';
    }
    
    input.addEventListener('input', scheduleAutoSave);
    input.addEventListener('blur', autoSaveTaskInputs);
    fieldDiv.appendChild(label);
    fieldDiv.appendChild(input);
    container.appendChild(fieldDiv);
}

function createDefaultAIInputs(container, task) {
    // Create a message indicating that input fields are not defined
    const messageDiv = document.createElement('div');
    messageDiv.className = 'text-sm text-gray-500 italic p-2 bg-gray-50 rounded border';
    messageDiv.textContent = 'No input fields defined for this AI task. Input fields will be determined from the task configuration.';
    container.appendChild(messageDiv);
}

function scheduleAutoSave() {
    if (window.autoSaveTimeout) clearTimeout(window.autoSaveTimeout);
    window.autoSaveTimeout = setTimeout(autoSaveTaskInputs, 3000);
}

function autoSaveTaskInputs() {
    if (window.activeTaskIndex === null) return;
    const inputFields = document.querySelectorAll('#taskInputFields input, #taskInputFields textarea');
    const inputData = {};
    inputFields.forEach(field => { inputData[field.name] = field.value; });
    saveTaskInputs(window.activeTaskIndex, inputData);
}

function saveTaskInputs(taskIndex, inputData) {
    const task = window.taskDefinitions[taskIndex];
    if (!task) return;
    fetch(`/agents/api/agent_run/${window.agentRunUuid}/task_input/${task.uuid}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        body: JSON.stringify({ inputs: inputData })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update local task state
            window.taskDefinitions[taskIndex].state.inputs = inputData;
            console.log('Task inputs saved successfully');
        } else {
            console.error('Failed to save task inputs:', data.error);
        }
    })
    .catch(error => {
        console.error('Error saving task inputs:', error);
    });
}

function executeTask(taskIndex) {
    const task = window.taskDefinitions[taskIndex];
    if (!task) return;
    let inputData = {};
    if (taskIndex === window.activeTaskIndex) {
        const inputFields = document.querySelectorAll('#taskInputFields input, #taskInputFields textarea');
        inputFields.forEach(field => { inputData[field.name] = field.value; });
    } else {
        inputData = task.state?.inputs || {};
    }
    updateTaskStatus(taskIndex, 'running');
    fetch(`/api/task_management/run/${window.agentRunUuid}/tasks/${task.uuid}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        body: JSON.stringify({ inputs: inputData })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateTaskStatus(taskIndex, 'completed');
            if (data.results) {
                window.taskDefinitions[taskIndex].state.results = data.results;
            }
        } else {
            updateTaskStatus(taskIndex, 'error');
        }
    })
    .catch(() => {
        updateTaskStatus(taskIndex, 'error');
    });
}

function updateTaskStatus(taskIndex, status) {
    const taskItem = document.querySelector(`[data-task-index="${taskIndex}"]`);
    if (!taskItem) return;
    
    const statusIcon = taskItem.querySelector('.status-icon svg');
    if (!statusIcon) return;
    
    // Update status icon based on new status
    switch (status) {
        case 'completed':
            statusIcon.innerHTML = '<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>';
            statusIcon.className = 'w-4 h-4 text-green-600';
            statusIcon.setAttribute('title', 'Completed');
            break;
        case 'running':
            statusIcon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>';
            statusIcon.className = 'w-4 h-4 text-blue-600 animate-spin';
            statusIcon.setAttribute('fill', 'none');
            statusIcon.setAttribute('stroke', 'currentColor');
            statusIcon.setAttribute('title', 'Running');
            break;
        case 'error':
            statusIcon.innerHTML = '<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>';
            statusIcon.className = 'w-4 h-4 text-red-600';
            statusIcon.setAttribute('title', 'Error');
            break;
        default:
            statusIcon.innerHTML = '<circle cx="10" cy="10" r="8"></circle>';
            statusIcon.className = 'w-4 h-4 text-gray-400';
            statusIcon.setAttribute('title', 'Pending');
    }
    
    // Update task definition status
    if (window.taskDefinitions[taskIndex]) {
        window.taskDefinitions[taskIndex].status = status;
        if (window.taskDefinitions[taskIndex].state) {
            window.taskDefinitions[taskIndex].state.status = status;
        }
    }
}

function getCsrfToken() {
    return window.csrfToken || '';
}
