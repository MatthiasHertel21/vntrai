// ===========================
// LEGACY TASK MANAGEMENT & KNOWLEDGE FUNCTIONS
// ===========================

class LegacyManager {
    constructor() {
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            // Initialize legacy functions
            this.setupLegacySupport();
        });
    }

    setupLegacySupport() {
        console.log('Legacy manager initialized for backward compatibility');
    }

    // ===========================
    // LEGACY TASK MANAGEMENT (DEPRECATED)
    // ===========================

    // Task Management Functions
    addNewTaskOld() {
        if (typeof showNotification === 'function') {
            showNotification('Task creation is now handled through the new Task Editor. This feature will be available in Sprint 18.', false);
        }
        console.log('Add Task clicked - Feature in development for Sprint 18');
    }

    deleteTaskOld(taskId) {
        if (confirm('Are you sure you want to delete this task?')) {
            if (typeof showNotification === 'function') {
                showNotification('Task deletion will be available in Sprint 18.', false);
            }
            console.log('Delete Task clicked for task:', taskId);
        }
    }

    // Knowledge Management Functions
    addNewKnowledgeItem() {
        if (typeof showNotification === 'function') {
            showNotification('Knowledge Item creation is being developed. This feature will be available soon.', false);
        }
        console.log('Add Knowledge Item clicked - Feature in development');
    }

    editKnowledgeItem(knowledgeId) {
        if (typeof showNotification === 'function') {
            showNotification('Knowledge Item editing will be available soon.', false);
        }
        console.log('Edit Knowledge Item clicked for item:', knowledgeId);
    }

    deleteKnowledgeItem(knowledgeId) {
        if (confirm('Are you sure you want to delete this knowledge item?')) {
            if (typeof showNotification === 'function') {
                showNotification('Knowledge Item deletion will be available soon.', false);
            }
            console.log('Delete Knowledge Item clicked for item:', knowledgeId);
        }
    }

    // Add debug button (for testing only)
    addDebugButton() {
        if (document.getElementById('debugTaskButton')) return; // Already added
        
        const debugButton = document.createElement('button');
        debugButton.id = 'debugTaskButton';
        debugButton.type = 'button';
        debugButton.className = 'btn btn-sm btn-warning';
        debugButton.innerHTML = '<i class="bi bi-bug"></i> Debug API';
        debugButton.onclick = () => {
            if (typeof debugTaskAPI === 'function') {
                debugTaskAPI();
            }
        };
        
        const buttonContainer = document.querySelector('.flex.gap-2');
        if (buttonContainer) {
            buttonContainer.appendChild(debugButton);
        }
    }
}

// Global legacy manager instance
const legacyManager = new LegacyManager();

// Global functions for backward compatibility
function addNewTaskOld() {
    legacyManager.addNewTaskOld();
}

function deleteTaskOld(taskId) {
    legacyManager.deleteTaskOld(taskId);
}

function addNewKnowledgeItem() {
    legacyManager.addNewKnowledgeItem();
}

function editKnowledgeItem(knowledgeId) {
    legacyManager.editKnowledgeItem(knowledgeId);
}

function deleteKnowledgeItem(knowledgeId) {
    legacyManager.deleteKnowledgeItem(knowledgeId);
}

function addDebugButton() {
    legacyManager.addDebugButton();
}
