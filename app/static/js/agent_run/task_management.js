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
    
    // Handle different task data structures
    const description = task.description || task.definition?.description || 'No description available';
    descriptionContainer.textContent = description;
    
    inputFieldsContainer.innerHTML = '';
    
    // Check for input schema in different locations
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
    } else if (task.type === 'ai') {
        createDefaultAIInputs(inputFieldsContainer, task);
    } else {
        console.log('No input schema found, task type:', task.type);
    }
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
    createInputField(container, 'prompt', {
        type: 'textarea',
        label: 'Prompt',
        placeholder: 'Enter your prompt for this AI task...',
        required: false
    }, task);
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
    const statusIcon = taskItem.querySelector('.status-icon i');
    if (!statusIcon) return;
    statusIcon.className = statusIcon.className.replace(/fa-(check-circle|spinner|exclamation-circle|circle)/g, '');
    statusIcon.className = statusIcon.className.replace(/fa-spin/g, '');
    statusIcon.className = statusIcon.className.replace(/text-(green|blue|red|gray)-\d+/g, '');
    switch (status) {
        case 'completed':
            statusIcon.classList.add('fa-check-circle', 'text-green-600');
            statusIcon.title = 'Completed';
            break;
        case 'running':
            statusIcon.classList.add('fa-spinner', 'fa-spin', 'text-blue-600');
            statusIcon.title = 'Running';
            break;
        case 'error':
            statusIcon.classList.add('fa-exclamation-circle', 'text-red-600');
            statusIcon.title = 'Error';
            break;
        default:
            statusIcon.classList.add('fa-circle', 'text-gray-400');
            statusIcon.title = 'Pending';
    }
    if (window.taskDefinitions[taskIndex]) {
        window.taskDefinitions[taskIndex].status = status;
        window.taskDefinitions[taskIndex].state.status = status;
    }
}

function getCsrfToken() {
    return window.csrfToken || '';
}
