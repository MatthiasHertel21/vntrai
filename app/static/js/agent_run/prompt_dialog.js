/**
 * Prompt Dialog Manager for Agent Run View
 * Handles prompt display, fetching from server, and related functionality
 */

class PromptDialog {
    constructor() {
        this.languageNames = {
            'de': 'German',
            'en': 'English',
            'fr': 'French',
            'es': 'Spanish',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean'
        };
    }

    /**
     * Get the current agent run UUID
     * @returns {string} The agent run UUID
     */
    getAgentRunUuid() {
        return window.agentRunUuid || '';
    }

    /**
     * Show the prompt dialog for the active task
     */
    show() {
        if (window.activeTaskIndex === null || !window.taskDefinitions[window.activeTaskIndex]) {
            showNotification('No active task selected', 'error');
            return;
        }
        
        const agentRunUuid = this.getAgentRunUuid();
        if (!agentRunUuid) {
            showNotification('Agent run UUID not available. Please refresh the page.', 'error');
            return;
        }
        
        const task = window.taskDefinitions[window.activeTaskIndex];
        const modal = this.createModal(task);
        
        // Fetch the prompt from the server
        this.fetchTaskPrompt(task.uuid)
            .then(promptData => {
                this.displayPromptInDialog(promptData);
            })
            .catch(error => {
                console.error('Failed to fetch prompt from server:', error);
                // Fallback to client-side generation
                const contentPrompt = this.generateContentPrompt(task);
                this.displayPromptInDialog({
                    prompt: contentPrompt,
                    task_name: task.name || 'Task',
                    fallback: true
                });
            });
    }

    /**
     * Create the modal dialog structure
     * @param {Object} task - The task object
     * @returns {HTMLElement} The modal element
     */
    createModal(task) {
        // Create modal dialog with loading state
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        modal.onclick = (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        };
        
        const dialog = document.createElement('div');
        dialog.className = 'bg-white rounded-lg shadow-xl max-w-4xl max-h-[80vh] w-full mx-4 overflow-hidden';
        
        dialog.innerHTML = `
            <div class="border-b border-gray-200 px-6 py-4 flex justify-between items-center">
                <h3 class="text-lg font-medium text-gray-900 flex items-center">
                    <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: #0cc0df;">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                    </svg>
                    Content Prompt - ${task.name || 'Task'}
                </h3>
                <button onclick="this.closest('.fixed').remove()" class="text-gray-400 hover:text-gray-600">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
            <div class="p-6 overflow-y-auto max-h-[60vh]" id="promptContent">
                <div class="flex items-center justify-center py-8">
                    <svg class="animate-spin h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span class="ml-2 text-gray-600">Loading prompt...</span>
                </div>
            </div>
            <div class="border-t border-gray-200 px-6 py-4 flex justify-end space-x-3" id="promptActions">
                <button onclick="this.closest('.fixed').remove()" class="btn-sm bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 transition-colors duration-200">
                    Close
                </button>
            </div>
        `;
        
        modal.appendChild(dialog);
        document.body.appendChild(modal);
        
        return modal;
    }

    /**
     * Fetch the actual prompt from the server for a given task
     * @param {string} taskUuid - The task UUID
     * @returns {Promise} Promise resolving to prompt data
     */
    fetchTaskPrompt(taskUuid) {
        return new Promise((resolve, reject) => {
            // Collect current input field values
            const inputFields = document.querySelectorAll('#taskInputFields input, #taskInputFields textarea, #taskInputFields select');
            const inputs = {};
            inputFields.forEach(field => {
                if (field.value) {
                    inputs[field.name || field.id] = field.value;
                }
            });
            
            // Get current language selection
            const language = document.getElementById('globalLanguageSelect')?.value || 'auto';
            if (language !== 'auto') {
                inputs._language = language;
            }
            
            const agentRunUuid = this.getAgentRunUuid();
            if (!agentRunUuid) {
                reject(new Error('Agent run UUID not available. Current value: ' + agentRunUuid));
                return;
            }
            
            console.log('Fetching prompt for task:', taskUuid, 'from run:', agentRunUuid);
            
            // Make API call to get the prompt
            fetch(`/agents/api/agent_run/${agentRunUuid}/task/${taskUuid}/prompt`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    inputs: inputs
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    resolve(data);
                } else {
                    reject(new Error(data.error || 'Failed to fetch prompt'));
                }
            })
            .catch(error => {
                console.error('Error fetching prompt from server:', error);
                reject(error);
            });
        });
    }

    /**
     * Generate a fallback content prompt client-side
     * @param {Object} task - The task object
     * @returns {string} Generated prompt
     */
    generateContentPrompt(task) {
        const language = document.getElementById('globalLanguageSelect')?.value || 'auto';
        let prompt = '';
        
        // Add task description
        const description = task.description || task.definition?.description || '';
        if (description) {
            prompt += `Task: ${task.name || 'Unnamed Task'}\n`;
            prompt += `Description: ${description}\n\n`;
        }
        
        // Add language instruction if not auto
        if (language !== 'auto') {
            const languageName = this.languageNames[language] || language;
            prompt += `Please respond in ${languageName}.\n\n`;
        }
        
        // Add input field values
        const inputFields = document.querySelectorAll('#taskInputFields input, #taskInputFields textarea, #taskInputFields select');
        if (inputFields.length > 0) {
            prompt += 'Input Parameters:\n';
            inputFields.forEach(field => {
                const label = field.previousElementSibling?.textContent || field.name || field.id;
                const value = field.value;
                if (value) {
                    prompt += `- ${label}: ${value}\n`;
                }
            });
            prompt += '\n';
        }
        
        // Add AI-specific instructions
        if (task.type === 'ai' || task.definition?.type === 'ai') {
            const aiConfig = task.ai_config || task.definition?.ai_config;
            if (aiConfig?.prompt) {
                prompt += `Instructions:\n${aiConfig.prompt}\n\n`;
            }
        }
        
        // Add context instruction
        prompt += 'Please provide a comprehensive response based on the above information.';
        
        return prompt;
    }

    /**
     * Display the fetched prompt data in the dialog
     * @param {Object} promptData - The prompt data from server or fallback
     */
    displayPromptInDialog(promptData) {
        const promptContent = document.getElementById('promptContent');
        const promptActions = document.getElementById('promptActions');
        
        if (!promptContent) return;
        
        const isFallback = promptData.fallback || false;
        
        promptContent.innerHTML = `
            <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
                ${isFallback ? '<div class="mb-2 text-sm text-orange-600 font-medium">⚠️ Fallback: Client-side generated prompt (server unavailable)</div>' : ''}
                <pre class="whitespace-pre-wrap text-sm text-gray-800 font-mono">${promptData.prompt}</pre>
            </div>
        `;
        
        // Update actions to include copy button
        promptActions.innerHTML = `
            <button onclick="promptDialog.copyPromptToClipboard(\`${this.escapeForTemplate(promptData.prompt)}\`)" class="btn-sm text-white px-4 py-2 rounded transition-colors duration-200" style="background-color: #0cc0df;" onmouseover="this.style.backgroundColor='#0aa1c7'" onmouseout="this.style.backgroundColor='#0cc0df'">
                <svg class="w-4 h-4 mr-1 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                </svg>
                Copy
            </button>
            <button onclick="this.closest('.fixed').remove()" class="btn-sm bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 transition-colors duration-200">
                Close
            </button>
        `;
    }

    /**
     * Escape text for safe template insertion
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeForTemplate(text) {
        return text.replace(/`/g, '\\`').replace(/\\/g, '\\\\').replace(/\${/g, '\\${');
    }

    /**
     * Copy prompt to clipboard
     * @param {string} text - Text to copy
     */
    copyPromptToClipboard(text) {
        copyToClipboard(text, 'Prompt copied to clipboard!', 'Failed to copy prompt to clipboard');
    }
}

// Global variable to hold the prompt dialog instance
let promptDialog = null;

/**
 * Initialize the prompt dialog (called after global variables are set)
 */
function initializePromptDialog() {
    if (!promptDialog) {
        promptDialog = new PromptDialog();
    }
    return promptDialog;
}

// Export functions for global use
window.showPromptDialog = () => {
    const dialog = promptDialog || initializePromptDialog();
    dialog.show();
};

window.copyPromptToClipboard = (text) => {
    const dialog = promptDialog || initializePromptDialog();
    dialog.copyPromptToClipboard(text);
};

window.initializePromptDialog = initializePromptDialog;
window.promptDialog = null; // Will be set after initialization
