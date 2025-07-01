/**
 * Knowledge Management Module
 * Handles knowledge base items creation, editing, and deletion
 */

// ===========================
// KNOWLEDGE MANAGEMENT CORE
// ===========================

// Global variables for knowledge management
let knowledgeItems = [];

// Initialize knowledge management system
function initializeKnowledgeManagement(agentData = {}) {
    // Load existing knowledge items
    if (agentData.knowledge_base) {
        knowledgeItems = [...agentData.knowledge_base];
    } else {
        knowledgeItems = [];
    }
    
    // Update knowledge count
    updateKnowledgeCount();
    
    // Set up event listeners for knowledge management
    setupKnowledgeEventListeners();
}

// Update knowledge items count display
function updateKnowledgeCount() {
    const knowledgeCountElements = document.querySelectorAll('[data-knowledge-count]');
    knowledgeCountElements.forEach(element => {
        element.textContent = knowledgeItems.length;
    });
}

// Set up event listeners for knowledge management
function setupKnowledgeEventListeners() {
    // Add event listeners for knowledge item buttons
    document.addEventListener('click', function(e) {
        if (e.target.matches('[data-knowledge-action="add"]')) {
            e.preventDefault();
            addNewKnowledgeItem();
        } else if (e.target.matches('[data-knowledge-action="edit"]')) {
            e.preventDefault();
            const knowledgeId = e.target.getAttribute('data-knowledge-id');
            editKnowledgeItem(knowledgeId);
        } else if (e.target.matches('[data-knowledge-action="delete"]')) {
            e.preventDefault();
            const knowledgeId = e.target.getAttribute('data-knowledge-id');
            deleteKnowledgeItem(knowledgeId);
        }
    });
}

// ===========================
// KNOWLEDGE ITEM MANAGEMENT
// ===========================

// Add new knowledge item
function addNewKnowledgeItem() {
    showKnowledgeModal();
}

// Edit existing knowledge item
function editKnowledgeItem(knowledgeId) {
    const knowledge = knowledgeItems.find(item => item.id === knowledgeId);
    if (knowledge) {
        showKnowledgeModal(knowledge);
    } else {
        showNotificationSafe('Knowledge item editing will be available soon.', false);
        console.log('Edit Knowledge Item clicked for item:', knowledgeId);
    }
}

// Delete knowledge item
function deleteKnowledgeItem(knowledgeId) {
    if (confirm('Are you sure you want to delete this knowledge item?')) {
        // For now, show placeholder message
        showNotificationSafe('Knowledge Item deletion will be available soon.', false);
        console.log('Delete Knowledge Item clicked for item:', knowledgeId);
        
        // TODO: Implement actual deletion
        // removeKnowledgeItem(knowledgeId);
    }
}

// ===========================
// KNOWLEDGE MODAL MANAGEMENT
// ===========================

// Show knowledge item creation/editing modal
function showKnowledgeModal(knowledge = null) {
    const isEditing = knowledge !== null;
    const modalTitle = isEditing ? 'Edit Knowledge Item' : 'Add Knowledge Item';
    
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div class="p-6">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-lg font-medium text-gray-900">${modalTitle}</h3>
                    <button type="button" onclick="closeKnowledgeModal()" 
                            class="text-gray-400 hover:text-gray-600">
                        <i class="bi bi-x-lg"></i>
                    </button>
                </div>
                
                <form id="knowledgeForm">
                    <div class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">
                                Title <span class="text-red-500">*</span>
                            </label>
                            <input type="text" id="knowledgeTitle" required 
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                                   placeholder="Enter knowledge item title"
                                   value="${knowledge?.title || ''}">
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">
                                Use Case
                            </label>
                            <input type="text" id="knowledgeUseCase" 
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                                   placeholder="When should this knowledge be used?"
                                   value="${knowledge?.use_case || ''}">
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">
                                Content <span class="text-red-500">*</span>
                            </label>
                            <textarea id="knowledgeContent" required rows="6"
                                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                                      placeholder="Enter the knowledge content...">${knowledge?.content || ''}</textarea>
                        </div>
                        
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">
                                    Type
                                </label>
                                <select id="knowledgeType" 
                                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
                                    <option value="general" ${knowledge?.type === 'general' ? 'selected' : ''}>General</option>
                                    <option value="factual" ${knowledge?.type === 'factual' ? 'selected' : ''}>Factual</option>
                                    <option value="procedural" ${knowledge?.type === 'procedural' ? 'selected' : ''}>Procedural</option>
                                    <option value="contextual" ${knowledge?.type === 'contextual' ? 'selected' : ''}>Contextual</option>
                                </select>
                            </div>
                            
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">
                                    Rating (1-5)
                                </label>
                                <select id="knowledgeRating" 
                                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
                                    <option value="">No rating</option>
                                    <option value="1" ${knowledge?.rating === 1 ? 'selected' : ''}>1 - Low</option>
                                    <option value="2" ${knowledge?.rating === 2 ? 'selected' : ''}>2 - Fair</option>
                                    <option value="3" ${knowledge?.rating === 3 ? 'selected' : ''}>3 - Good</option>
                                    <option value="4" ${knowledge?.rating === 4 ? 'selected' : ''}>4 - Very Good</option>
                                    <option value="5" ${knowledge?.rating === 5 ? 'selected' : ''}>5 - Excellent</option>
                                </select>
                            </div>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">
                                Tags (comma-separated)
                            </label>
                            <input type="text" id="knowledgeTags" 
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                                   placeholder="tag1, tag2, tag3"
                                   value="${knowledge?.tags ? knowledge.tags.join(', ') : ''}">
                        </div>
                    </div>
                    
                    <div class="flex gap-3 mt-6">
                        <button type="submit" class="btn btn-primary flex-1">
                            <i class="bi bi-${isEditing ? 'check' : 'plus'} mr-1"></i>
                            ${isEditing ? 'Update' : 'Add'} Knowledge Item
                        </button>
                        <button type="button" onclick="closeKnowledgeModal()" 
                                class="btn btn-outline flex-1">
                            Cancel
                        </button>
                    </div>
                </form>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Handle form submission
    document.getElementById('knowledgeForm').addEventListener('submit', function(e) {
        e.preventDefault();
        handleKnowledgeFormSubmit(isEditing, knowledge?.id);
    });
    
    // Focus on title input
    document.getElementById('knowledgeTitle').focus();
}

// Close knowledge modal
function closeKnowledgeModal() {
    const modal = document.querySelector('.fixed.inset-0');
    if (modal) {
        modal.remove();
    }
}

// Handle knowledge form submission
function handleKnowledgeFormSubmit(isEditing, knowledgeId) {
    const formData = collectKnowledgeFormData();
    
    if (!formData.title.trim() || !formData.content.trim()) {
        showNotificationSafe('Please fill in all required fields', false);
        return;
    }
    
    if (isEditing) {
        updateKnowledgeItem(knowledgeId, formData);
    } else {
        createKnowledgeItem(formData);
    }
}

// Collect data from knowledge form
function collectKnowledgeFormData() {
    const tags = document.getElementById('knowledgeTags').value
        .split(',')
        .map(tag => tag.trim())
        .filter(tag => tag.length > 0);
    
    return {
        title: document.getElementById('knowledgeTitle').value.trim(),
        use_case: document.getElementById('knowledgeUseCase').value.trim(),
        content: document.getElementById('knowledgeContent').value.trim(),
        type: document.getElementById('knowledgeType').value,
        rating: document.getElementById('knowledgeRating').value ? parseInt(document.getElementById('knowledgeRating').value) : null,
        tags: tags
    };
}

// ===========================
// KNOWLEDGE CRUD OPERATIONS
// ===========================

// Create new knowledge item
function createKnowledgeItem(formData) {
    // For now, show development message
    showNotificationSafe('Knowledge Item creation is being developed. This feature will be available soon.', false);
    console.log('Creating knowledge item:', formData);
    
    // TODO: Implement actual creation
    // const newKnowledge = {
    //     id: generateKnowledgeId(),
    //     ...formData,
    //     created_at: new Date().toISOString()
    // };
    // knowledgeItems.push(newKnowledge);
    // updateKnowledgeCount();
    // closeKnowledgeModal();
    // showNotificationSafe('Knowledge item created successfully!', true);
}

// Update existing knowledge item
function updateKnowledgeItem(knowledgeId, formData) {
    // For now, show development message
    showNotificationSafe('Knowledge Item updating is being developed. This feature will be available soon.', false);
    console.log('Updating knowledge item:', knowledgeId, formData);
    
    // TODO: Implement actual update
    // const index = knowledgeItems.findIndex(item => item.id === knowledgeId);
    // if (index !== -1) {
    //     knowledgeItems[index] = { ...knowledgeItems[index], ...formData, updated_at: new Date().toISOString() };
    //     closeKnowledgeModal();
    //     showNotificationSafe('Knowledge item updated successfully!', true);
    // }
}

// Remove knowledge item
function removeKnowledgeItem(knowledgeId) {
    const index = knowledgeItems.findIndex(item => item.id === knowledgeId);
    if (index !== -1) {
        knowledgeItems.splice(index, 1);
        updateKnowledgeCount();
        showNotificationSafe('Knowledge item deleted successfully!', true);
    }
}

// ===========================
// UTILITY FUNCTIONS
// ===========================

// Generate unique knowledge ID
function generateKnowledgeId() {
    return 'knowledge_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Safe notification function
function showNotificationSafe(message, isSuccess) {
    if (typeof showNotification === 'function') {
        showNotification(message, isSuccess);
    } else {
        console.log(`${isSuccess ? 'SUCCESS' : 'ERROR'}: ${message}`);
    }
}

// ===========================
// PUBLIC API
// ===========================

// Export functions for global access
window.KnowledgeManagement = {
    initialize: initializeKnowledgeManagement,
    add: addNewKnowledgeItem,
    edit: editKnowledgeItem,
    delete: deleteKnowledgeItem,
    showModal: showKnowledgeModal,
    closeModal: closeKnowledgeModal
};

// Make functions globally available for onclick handlers
window.addNewKnowledgeItem = addNewKnowledgeItem;
window.editKnowledgeItem = editKnowledgeItem;
window.deleteKnowledgeItem = deleteKnowledgeItem;
window.closeKnowledgeModal = closeKnowledgeModal;
