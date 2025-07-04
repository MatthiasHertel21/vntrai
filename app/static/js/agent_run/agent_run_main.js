/**
 * Main initialization script for Agent Run View
 * Sets up global variables and coordinates module initialization
 */

/**
 * Agent Run Main Controller
 * Manages global state and module coordination
 */
class AgentRunMain {
    constructor() {
        this.initialized = false;
        this.modules = {};
    }

    /**
     * Initialize the agent run view
     * @param {Object} config - Configuration object containing taskDefinitions and agentRunUuid
     */
    init(config) {
        if (this.initialized) {
            console.warn('AgentRunMain already initialized');
            return;
        }

        // Set global variables
        window.taskDefinitions = config.taskDefinitions || [];
        window.agentRunUuid = config.agentRunUuid;
        window.activeTaskIndex = null;

        // Initialize modules
        this.initializeModules();

        // Set up global event listeners
        this.setupGlobalEventListeners();

        // Load initial state
        this.loadInitialState();

        this.initialized = true;
        console.log('AgentRunMain initialized successfully');
    }

    /**
     * Initialize all modules
     */
    initializeModules() {
        // Initialize prompt dialog after global variables are set
        if (window.initializePromptDialog) {
            const promptDialog = window.initializePromptDialog();
            window.promptDialog = promptDialog;
            console.log('Prompt dialog initialized');
        }
        
        // Modules are initialized by their own files
        // This method can be used for any cross-module setup
        console.log('Initializing AgentRun modules...');
    }

    /**
     * Set up global event listeners
     */
    setupGlobalEventListeners() {
        // Listen for language changes
        document.addEventListener('languageChanged', (event) => {
            console.log('Language changed to:', event.detail.language);
            // Broadcast to other modules if needed
        });

        // Listen for task selection changes
        document.addEventListener('taskSelectionChanged', (event) => {
            window.activeTaskIndex = event.detail.taskIndex;
            console.log('Active task changed to index:', window.activeTaskIndex);
        });

        // Listen for task status updates
        document.addEventListener('taskStatusChanged', (event) => {
            console.log('Task status changed:', event.detail);
            this.updateTaskStatus(event.detail.taskIndex, event.detail.status);
        });

        // Global keyboard shortcuts
        document.addEventListener('keydown', (event) => {
            this.handleGlobalKeyboardShortcuts(event);
        });
    }

    /**
     * Load initial state from localStorage or defaults
     */
    loadInitialState() {
        // Load last active task if available
        const lastActiveTask = localStorage.getItem(`lastActiveTask_${window.agentRunUuid}`);
        if (lastActiveTask !== null && window.taskDefinitions.length > 0) {
            const taskIndex = parseInt(lastActiveTask);
            if (taskIndex >= 0 && taskIndex < window.taskDefinitions.length) {
                // Trigger task selection (handled by task management module)
                setTimeout(() => {
                    if (window.selectTask) {
                        window.selectTask(taskIndex, window.agentRunUuid);
                    }
                }, 100);
            }
        } else if (window.taskDefinitions.length > 0) {
            // Select first task by default
            setTimeout(() => {
                if (window.selectTask) {
                    window.selectTask(0, window.agentRunUuid);
                }
            }, 100);
        }
    }

    /**
     * Handle global keyboard shortcuts
     * @param {KeyboardEvent} event - The keyboard event
     */
    handleGlobalKeyboardShortcuts(event) {
        // Escape key - close modals
        if (event.key === 'Escape') {
            const modals = document.querySelectorAll('.fixed.inset-0');
            modals.forEach(modal => {
                if (modal.classList.contains('z-50')) {
                    modal.remove();
                }
            });
        }

        // Ctrl/Cmd + Enter - Execute active task
        if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
            event.preventDefault();
            if (window.activeTaskIndex !== null && window.executeTask) {
                window.executeTask(window.activeTaskIndex);
            }
        }

        // Ctrl/Cmd + P - Show prompt dialog
        if ((event.ctrlKey || event.metaKey) && event.key === 'p') {
            event.preventDefault();
            if (window.showPromptDialog) {
                window.showPromptDialog();
            }
        }
    }

    /**
     * Update task status in the UI
     * @param {number} taskIndex - Index of the task
     * @param {string} status - New status
     */
    updateTaskStatus(taskIndex, status) {
        const taskItems = document.querySelectorAll('.task-item');
        if (taskItems[taskIndex]) {
            const statusIcon = taskItems[taskIndex].querySelector('.status-icon svg');
            if (statusIcon) {
                // Update icon based on status
                this.updateStatusIcon(statusIcon, status);
            }
        }
    }

    /**
     * Update status icon based on status
     * @param {SVGElement} iconElement - The icon element
     * @param {string} status - The new status
     */
    updateStatusIcon(iconElement, status) {
        // Remove existing classes
        iconElement.className = iconElement.className.replace(/text-\w+-\d+/g, '').replace(/animate-spin/g, '');

        switch (status) {
            case 'completed':
                iconElement.classList.add('text-green-600');
                iconElement.innerHTML = '<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>';
                break;
            case 'running':
                iconElement.classList.add('text-blue-600', 'animate-spin');
                iconElement.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>';
                break;
            case 'error':
                iconElement.classList.add('text-red-600');
                iconElement.innerHTML = '<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>';
                break;
            default:
                iconElement.classList.add('text-gray-400');
                iconElement.innerHTML = '<circle cx="10" cy="10" r="8"></circle>';
        }
    }

    /**
     * Save current state to localStorage
     */
    saveState() {
        if (window.activeTaskIndex !== null) {
            localStorage.setItem(`lastActiveTask_${window.agentRunUuid}`, window.activeTaskIndex.toString());
        }
    }

    /**
     * Get module instance
     * @param {string} moduleName - Name of the module
     * @returns {Object|null} Module instance or null
     */
    getModule(moduleName) {
        return this.modules[moduleName] || null;
    }

    /**
     * Register a module
     * @param {string} moduleName - Name of the module
     * @param {Object} moduleInstance - Module instance
     */
    registerModule(moduleName, moduleInstance) {
        this.modules[moduleName] = moduleInstance;
    }
}

// Create global instance
const agentRunMain = new AgentRunMain();

// Export for global access
window.agentRunMain = agentRunMain;

// Auto-save state before page unload
window.addEventListener('beforeunload', () => {
    agentRunMain.saveState();
});

console.log('AgentRunMain module loaded');
