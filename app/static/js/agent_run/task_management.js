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
        console.log('Tool task detected - rendering tool input fields');
        
        // Look for tool_id in different locations
        let toolId = null;
        if (task.tool_id) {
            toolId = task.tool_id;
        } else if (task.definition && task.definition.tool_id) {
            toolId = task.definition.tool_id;
        } else if (task.config && task.config.tool_id) {
            toolId = task.config.tool_id;
        } else if (task.definition && task.definition.config && task.definition.config.tool_id) {
            toolId = task.definition.config.tool_id;
        }
        
        if (toolId) {
            // Try to render tool input fields
            renderToolInputFields(inputFieldsContainer, toolId, task);
        } else {
            const toolMessage = document.createElement('p');
            toolMessage.className = 'text-sm text-gray-500 italic';
            toolMessage.textContent = 'Tool input fields: tool_id not found in task definition';
            inputFieldsContainer.appendChild(toolMessage);
        }
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
    
    // Get the task UUID from the correct location
    const taskUuid = task.uuid || task.definition?.uuid;
    if (!taskUuid) {
        console.error('Task UUID not found for task:', task);
        return;
    }
    
    fetch(`/agents/api/agent_run/${window.agentRunUuid}/task_input/${taskUuid}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        body: JSON.stringify({ inputs: inputData })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update local task state
            if (!window.taskDefinitions[taskIndex].state) {
                window.taskDefinitions[taskIndex].state = {};
            }
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
    
    // Get the task UUID from the correct location
    const taskUuid = task.uuid || task.definition?.uuid;
    if (!taskUuid) {
        console.error('Task UUID not found for task:', task);
        return;
    }
    
    let inputData = {};
    if (taskIndex === window.activeTaskIndex) {
        const inputFields = document.querySelectorAll('#taskInputFields input, #taskInputFields textarea');
        inputFields.forEach(field => { inputData[field.name] = field.value; });
    } else {
        inputData = task.state?.inputs || {};
    }
    
    // Update UI to show execution is starting
    updateTaskStatus(taskIndex, 'running');
    
    // Clear previous output
    const outputElement = document.querySelector(`#taskResult-${taskIndex}`);
    if (outputElement) {
        outputElement.innerHTML = '<div class="text-gray-500 italic">Starting execution...</div>';
    }
    
    // Start streaming execution
    executeTaskWithStreaming(taskIndex, taskUuid, inputData);
}

function executeTaskWithStreaming(taskIndex, taskUuid, inputData) {
    const outputElement = document.querySelector(`#taskResult-${taskIndex}`);
    if (!outputElement) {
        console.error('Output element not found for task:', taskIndex);
        return;
    }
    
    // Initialize EventSource for server-sent events
    const eventSource = new EventSource('/agents/api/agent_run/' + window.agentRunUuid + '/task_execute/' + taskUuid + '/stream', {
        headers: {
            'Content-Type': 'application/json',
        }
    });
    
    // Since EventSource doesn't support POST, we need to use fetch for the initial request
    // and then connect to a streaming endpoint
    fetch(`/agents/api/agent_run/${window.agentRunUuid}/task_execute/${taskUuid}/stream`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
            'Accept': 'text/plain'
        },
        body: JSON.stringify({ inputs: inputData })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        // Handle streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        function readStream() {
            return reader.read().then(({ done, value }) => {
                if (done) {
                    console.log('Stream complete');
                    return;
                }
                
                // Decode the chunk
                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n');
                
                lines.forEach(line => {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            handleStreamData(data, taskIndex, outputElement);
                        } catch (e) {
                            console.error('Error parsing stream data:', e);
                        }
                    }
                });
                
                // Continue reading
                return readStream();
            });
        }
        
        return readStream();
    })
    .catch(error => {
        console.error('Streaming error:', error);
        updateTaskStatus(taskIndex, 'error');
        if (outputElement) {
            outputElement.innerHTML = '<div class="text-red-500">Error executing task: ' + error.message + '</div>';
        }
    });
}

function handleStreamData(data, taskIndex, outputElement) {
    switch (data.type) {
        case 'html_chunk':
            // Append HTML chunk to output
            outputElement.innerHTML += data.content;
            // Scroll to bottom of output
            outputElement.scrollTop = outputElement.scrollHeight;
            break;
            
        case 'complete':
            // Task execution completed
            updateTaskStatus(taskIndex, 'completed');
            // Save the complete HTML result to the task state
            if (window.taskDefinitions[taskIndex] && data.html_result) {
                if (!window.taskDefinitions[taskIndex].state) {
                    window.taskDefinitions[taskIndex].state = {};
                }
                if (!window.taskDefinitions[taskIndex].state.results) {
                    window.taskDefinitions[taskIndex].state.results = {};
                }
                window.taskDefinitions[taskIndex].state.results.html_output = data.html_result;
            }
            console.log('Task execution completed:', taskIndex);
            break;
            
        case 'error':
            // Handle execution error
            updateTaskStatus(taskIndex, 'error');
            outputElement.innerHTML += '<div class="text-red-500 p-4 bg-red-50 rounded-lg mt-4">❌ Execution Error: ' + data.error + '</div>';
            break;
            
        default:
            console.log('Unknown stream data type:', data.type);
    }
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

async function renderToolInputFields(container, toolId, task) {
    try {
        // Fetch tool definition from backend
        const response = await fetch(`/tools/api/config/${toolId}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch tool definition: ${response.status}`);
        }
        
        const result = await response.json();
        if (!result.success) {
            throw new Error(result.message || 'Failed to load tool config');
        }
        
        const toolData = result.tool;
        
        // Get input parameters from different sources
        let inputParams = [];
        
        // First check if tool has direct input_fields definition
        if (toolData.input_fields && Array.isArray(toolData.input_fields)) {
            inputParams = toolData.input_fields;
        } else {
            // Fallback: Create basic input params based on common tool patterns
            const commonInputs = getCommonToolInputs(toolData.tool_definition);
            if (commonInputs.length > 0) {
                inputParams = commonInputs;
            }
        }
        
        if (inputParams.length === 0) {
            const noFieldsMessage = document.createElement('p');
            noFieldsMessage.className = 'text-sm text-gray-500 italic';
            noFieldsMessage.textContent = `Tool: ${toolData.name} - Input fields definition not available`;
            container.appendChild(noFieldsMessage);
            return;
        }
        
        // Render input fields
        inputParams.forEach(param => {
            // Skip locked fields
            if (toolData.locked_inputs && toolData.locked_inputs.includes(param.name)) {
                return;
            }
            
            createToolInputField(container, param, task, toolData);
        });
        
    } catch (error) {
        console.error('Error rendering tool input fields:', error);
        const errorMessage = document.createElement('p');
        errorMessage.className = 'text-sm text-red-500 italic';
        errorMessage.textContent = `Error loading tool input fields: ${error.message}`;
        container.appendChild(errorMessage);
    }
}

function getCommonToolInputs(toolDefinition) {
    // Common input parameters for different tool types
    const commonInputMappings = {
        'ChatGPT': [
            {
                name: 'prompt',
                type: 'textarea',
                label: 'Prompt',
                description: 'Enter your question or request',
                required: true
            },
            {
                name: 'model',
                type: 'select',
                label: 'Model',
                description: 'OpenAI model to use',
                options: ['gpt-4', 'gpt-4-turbo-preview', 'gpt-3.5-turbo'],
                default: 'gpt-3.5-turbo'
            },
            {
                name: 'temperature',
                type: 'number',
                label: 'Temperature',
                description: 'Creativity level (0.0 - 2.0)',
                min: 0.0,
                max: 2.0,
                step: 0.1,
                default: 0.7
            }
        ],
        'Google Sheets': [
            {
                name: 'spreadsheet_id',
                type: 'text',
                label: 'Spreadsheet ID',
                description: 'Google Sheets spreadsheet ID',
                required: true
            },
            {
                name: 'range',
                type: 'text',
                label: 'Range',
                description: 'Cell range (e.g., A1:C10)',
                required: true
            }
        ],
        'OpenAI Assistant': [
            {
                name: 'message',
                type: 'textarea',
                label: 'Message',
                description: 'Message to send to the assistant',
                required: true
            }
        ]
    };
    
    return commonInputMappings[toolDefinition] || [];
}

function createToolInputField(container, param, task, toolData) {
    const fieldDiv = document.createElement('div');
    fieldDiv.className = 'space-y-1';
    
    const label = document.createElement('label');
    label.className = 'block text-xs font-medium text-gray-600';
    label.textContent = param.label || param.name;
    
    let input;
    const fieldName = param.name;
    
    // Get saved value from different possible locations
    let savedValue = '';
    if (task.state && task.state.inputs && task.state.inputs[fieldName]) {
        savedValue = task.state.inputs[fieldName];
    } else if (task.inputs && task.inputs[fieldName]) {
        savedValue = task.inputs[fieldName];
    } else if (toolData.prefilled_inputs && toolData.prefilled_inputs[fieldName]) {
        savedValue = toolData.prefilled_inputs[fieldName];
    } else if (param.default) {
        savedValue = param.default;
    }
    
    if (param.type === 'textarea') {
        input = document.createElement('textarea');
        input.className = 'w-full text-xs border border-gray-300 rounded px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:border-blue-500';
        input.rows = 3;
        input.value = savedValue;
    } else if (param.type === 'select') {
        input = document.createElement('select');
        input.className = 'w-full text-xs border border-gray-300 rounded px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:border-blue-500';
        
        // Add options
        if (param.options && Array.isArray(param.options)) {
            param.options.forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.value = option;
                optionElement.textContent = option;
                if (option === savedValue) {
                    optionElement.selected = true;
                }
                input.appendChild(optionElement);
            });
        }
    } else {
        input = document.createElement('input');
        input.type = param.type === 'number' ? 'number' : 'text';
        input.className = 'w-full text-xs border border-gray-300 rounded px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:border-blue-500';
        input.value = savedValue;
        
        if (param.type === 'number' && param.min !== undefined) {
            input.min = param.min;
        }
        if (param.type === 'number' && param.max !== undefined) {
            input.max = param.max;
        }
        if (param.type === 'number' && param.step !== undefined) {
            input.step = param.step;
        }
    }
    
    input.name = fieldName;
    input.placeholder = param.description || param.placeholder || '';
    
    if (param.required) {
        input.required = true;
        label.innerHTML += ' <span class="text-red-500">*</span>';
    }
    
    input.addEventListener('input', scheduleAutoSave);
    input.addEventListener('blur', autoSaveTaskInputs);
    
    fieldDiv.appendChild(label);
    fieldDiv.appendChild(input);
    container.appendChild(fieldDiv);
}

// Load saved task results on page load
function loadSavedTaskResults() {
    if (!window.taskDefinitions) return;
    
    window.taskDefinitions.forEach((task, index) => {
        const outputElement = document.querySelector(`#taskResult-${index}`);
        if (!outputElement) return;
        
        // Check if task has saved HTML results
        const htmlOutput = task.state?.results?.html_output;
        if (htmlOutput) {
            // Replace the placeholder content with saved results
            outputElement.innerHTML = htmlOutput;
            
            // Update task status if it was completed
            if (task.state?.status === 'completed') {
                updateTaskStatus(index, 'completed');
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', (event) => {
    // Initial setup - restore active task and load saved results
    const uuid = window.agentRunUuid;
    restoreActiveTask(uuid);
    loadSavedTaskResults();
});
