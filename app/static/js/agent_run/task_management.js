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
    localStorage.setItem(`agentRun_${uuid}_activeTask`, taskIndex.toString());
    fetch(`/api/agent_run/${uuid}/selected_task`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        body: JSON.stringify({ task_index: taskIndex })
    });
}

function showActiveTaskDetails(taskIndex) {
    const task = window.taskDefinitions[taskIndex];
    if (!task) return;
    const detailsContainer = document.getElementById('activeTaskDetails');
    const descriptionContainer = document.getElementById('taskDescription');
    const inputFieldsContainer = document.getElementById('taskInputFields');
    detailsContainer.classList.remove('hidden');
    descriptionContainer.textContent = task.definition?.description || 'No description available';
    inputFieldsContainer.innerHTML = '';
    if (task.definition && task.definition.input_schema) {
        const schema = task.definition.input_schema;
        for (const [fieldName, fieldConfig] of Object.entries(schema)) {
            createInputField(inputFieldsContainer, fieldName, fieldConfig, task);
        }
    } else if (task.type === 'ai') {
        createDefaultAIInputs(inputFieldsContainer, task);
    }
}

function createInputField(container, fieldName, fieldConfig, task) {
    const fieldDiv = document.createElement('div');
    fieldDiv.className = 'space-y-1';
    const label = document.createElement('label');
    label.className = 'block text-xs font-medium text-gray-600';
    label.textContent = fieldConfig.label || fieldName;
    let input;
    const savedValue = task.state?.inputs?.[fieldName] || fieldConfig.default || '';
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
    fetch(`/api/agent_run/${window.agentRunUuid}/task_input/${task.uuid}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        body: JSON.stringify({ inputs: inputData })
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
    fetch(`/task-management/run/${window.agentRunUuid}/tasks/${task.uuid}/execute`, {
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
