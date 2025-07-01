/**
 * Category Management Module
 * Handles custom category creation, storage, and selection for agents
 */

// ===========================
// CATEGORY MANAGEMENT CORE
// ===========================

// Initialize category management system
function initializeCategoryManagement() {
    const categorySelect = document.getElementById('category');
    const customCategoryInput = document.getElementById('customCategory');
    
    if (!categorySelect) return;
    
    // Load saved custom categories from localStorage
    loadCustomCategories();
    
    // Initialize category selection
    initializeCategorySelection();
    
    // Add event listener for category changes
    categorySelect.addEventListener('change', handleCategoryChange);
    
    // Handle form submission
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            if (categorySelect.value === '__NEW__') {
                e.preventDefault();
                showAddCategoryModal();
                return false;
            }
            
            // Set the custom category value for backend processing
            if (categorySelect.value && !getDefaultCategories().includes(categorySelect.value)) {
                if (customCategoryInput) {
                    customCategoryInput.value = categorySelect.value;
                }
            }
        });
    }
}

// Get default system categories
function getDefaultCategories() {
    return ['General', 'Content', 'Data', 'Marketing', 'Research', 'Support', 'Development', 'Finance', 'Education', 'Healthcare'];
}

// Load saved custom categories from localStorage
function loadCustomCategories() {
    const categorySelect = document.getElementById('category');
    if (!categorySelect) return;
    
    const savedCategories = JSON.parse(localStorage.getItem('agentCategories') || '[]');
    const defaultCategories = getDefaultCategories();
    
    // Add saved custom categories to the select
    savedCategories.forEach(category => {
        if (!defaultCategories.includes(category)) {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category;
            // Insert before the "Add New Category" option
            const addNewOption = categorySelect.querySelector('option[value="__NEW__"]');
            if (addNewOption) {
                categorySelect.insertBefore(option, addNewOption);
            } else {
                categorySelect.appendChild(option);
            }
        }
    });
}

// Initialize category selection based on current agent data
function initializeCategorySelection() {
    const categorySelect = document.getElementById('category');
    const customCategoryInput = document.getElementById('customCategory');
    
    if (!categorySelect) return;
    
    // Get current category from template context or input field
    let currentCategory = categorySelect.getAttribute('data-current-category');
    if (!currentCategory && customCategoryInput) {
        currentCategory = customCategoryInput.value;
    }
    
    if (currentCategory && currentCategory.trim()) {
        // If there's a custom category, select it or add it
        const existingOption = categorySelect.querySelector(`option[value="${currentCategory}"]`);
        if (!existingOption) {
            addCustomCategoryOption(currentCategory);
        }
        categorySelect.value = currentCategory;
    }
}

// Handle category selection changes
function handleCategoryChange() {
    const categorySelect = document.getElementById('category');
    if (!categorySelect) return;
    
    if (categorySelect.value === '__NEW__') {
        showAddCategoryModal();
    } else {
        const customCategoryInput = document.getElementById('customCategory');
        if (customCategoryInput) {
            customCategoryInput.value = '';
        }
    }
}

// Add a custom category option to the select dropdown
function addCustomCategoryOption(categoryName) {
    const categorySelect = document.getElementById('category');
    if (!categorySelect) return;
    
    const option = document.createElement('option');
    option.value = categoryName;
    option.textContent = categoryName;
    option.selected = true;
    
    // Insert before the "Add New Category" option
    const addNewOption = categorySelect.querySelector('option[value="__NEW__"]');
    if (addNewOption) {
        categorySelect.insertBefore(option, addNewOption);
    } else {
        categorySelect.appendChild(option);
    }
    
    // Save to localStorage
    saveCategoryToStorage(categoryName);
}

// Save category to localStorage
function saveCategoryToStorage(categoryName) {
    const savedCategories = JSON.parse(localStorage.getItem('agentCategories') || '[]');
    if (!savedCategories.includes(categoryName)) {
        savedCategories.push(categoryName);
        localStorage.setItem('agentCategories', JSON.stringify(savedCategories));
    }
}

// ===========================
// CATEGORY MODAL MANAGEMENT
// ===========================

// Show modal for adding new category
function showAddCategoryModal() {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div class="p-6">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Add New Category</h3>
                <form id="addCategoryForm">
                    <div class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Category Name</label>
                            <input type="text" id="newCategoryName" required 
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                                   placeholder="Enter category name">
                        </div>
                    </div>
                    <div class="flex gap-3 mt-6">
                        <button type="submit" class="btn btn-primary flex-1">
                            <i class="bi bi-plus mr-1"></i>
                            Add Category
                        </button>
                        <button type="button" onclick="closeAddCategoryModal(); resetCategorySelect();" 
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
    document.getElementById('addCategoryForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const categoryName = document.getElementById('newCategoryName').value.trim();
        
        if (categoryName) {
            addNewCategoryToSelect(categoryName);
            closeAddCategoryModal();
            
            // Show notification if available
            if (typeof showNotification === 'function') {
                showNotification(`Category "${categoryName}" added successfully!`, true);
            }
        }
    });
    
    // Focus on input
    document.getElementById('newCategoryName').focus();
}

// Close add category modal
function closeAddCategoryModal() {
    const modal = document.querySelector('.fixed.inset-0');
    if (modal) {
        modal.remove();
    }
}

// Reset category select when modal is cancelled
function resetCategorySelect() {
    const categorySelect = document.getElementById('category');
    if (!categorySelect) return;
    
    // Get current category from data attribute or fallback to General
    const currentCategory = categorySelect.getAttribute('data-current-category') || 'General';
    categorySelect.value = currentCategory;
}

// Add new category to select dropdown
function addNewCategoryToSelect(categoryName) {
    const categorySelect = document.getElementById('category');
    const customCategoryInput = document.getElementById('customCategory');
    
    if (!categorySelect) return;
    
    // Check if option already exists
    const existingOption = categorySelect.querySelector(`option[value="${categoryName}"]`);
    if (existingOption) {
        categorySelect.value = categoryName;
        return;
    }
    
    const option = document.createElement('option');
    option.value = categoryName;
    option.textContent = categoryName;
    option.selected = true;
    
    // Insert before the "Add New Category" option
    const addNewOption = categorySelect.querySelector('option[value="__NEW__"]');
    if (addNewOption) {
        categorySelect.insertBefore(option, addNewOption);
    } else {
        categorySelect.appendChild(option);
    }
    
    // Save to localStorage
    saveCategoryToStorage(categoryName);
    
    // Set custom category input for backend
    if (customCategoryInput) {
        customCategoryInput.value = categoryName;
    }
}

// ===========================
// PUBLIC API
// ===========================

// Export functions for global access
window.CategoryManagement = {
    initialize: initializeCategoryManagement,
    showAddModal: showAddCategoryModal,
    closeAddModal: closeAddCategoryModal,
    resetSelect: resetCategorySelect,
    addNewCategory: addNewCategoryToSelect
};

// Auto-initialize on DOM content loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeCategoryManagement();
});
