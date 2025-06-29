// VNTRAI JavaScript Functions
document.addEventListener('DOMContentLoaded', function() {
    // Context Area Toggle Functionality
    initContextAreaToggle();
    
    // Sidebar Enhancements
    initSidebarEnhancements();
    
    // Flash Messages Auto-Hide
    initFlashMessages();
    
    // Layout Management
    initLayoutManagement();
});

// Context Area Toggle Functions
function initContextAreaToggle() {
    const contextArea = document.getElementById('vntrContextArea');
    const toggleBtn = document.getElementById('sidebarContextToggleBtn');
    const collapseBtn = document.getElementById('contextCollapseBtn');
    const expandBtn = document.getElementById('contextExpandBtn');
    
    if (!contextArea) return;
    
    // Load saved state from localStorage
    const savedState = localStorage.getItem('vntrContextState');
    if (savedState === 'collapsed') {
        contextArea.classList.add('collapsed');
        if (expandBtn) expandBtn.style.display = 'flex';
        if (toggleBtn) toggleBtn.classList.add('active');
    }
    
    // Toggle button click handler
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function(e) {
            e.preventDefault();
            toggleContextArea();
        });
    }
    
    // Collapse button click handler
    if (collapseBtn) {
        collapseBtn.addEventListener('click', function() {
            toggleContextArea();
        });
    }
    
    // Expand button click handler
    if (expandBtn) {
        expandBtn.addEventListener('click', function() {
            toggleContextArea();
        });
    }
}

function toggleContextArea() {
    const contextArea = document.getElementById('vntrContextArea');
    const toggleBtn = document.getElementById('sidebarContextToggleBtn');
    const expandBtn = document.getElementById('contextExpandBtn');
    
    if (!contextArea) return;
    
    const isCollapsed = contextArea.classList.contains('collapsed');
    
    if (isCollapsed) {
        // Expand context area
        contextArea.classList.remove('collapsed');
        if (expandBtn) expandBtn.style.display = 'none';
        if (toggleBtn) toggleBtn.classList.remove('active');
        localStorage.setItem('vntrContextState', 'expanded');
    } else {
        // Collapse context area
        contextArea.classList.add('collapsed');
        if (expandBtn) expandBtn.style.display = 'flex';
        if (toggleBtn) toggleBtn.classList.add('active');
        localStorage.setItem('vntrContextState', 'collapsed');
    }
}

// Sidebar Enhancement Functions
function initSidebarEnhancements() {
    const sidebar = document.getElementById('vntrSidebar');
    if (!sidebar) return;
    
    // Auto-Expand/Collapse functionality
    let expandTimer;
    let collapseTimer;
    
    sidebar.addEventListener('mouseenter', function() {
        clearTimeout(collapseTimer);
        expandTimer = setTimeout(() => {
            sidebar.classList.add('expanded');
            sidebar.classList.remove('collapsed');
        }, 200); // Kurze Verzögerung für bessere UX
    });
    
    sidebar.addEventListener('mouseleave', function() {
        clearTimeout(expandTimer);
        collapseTimer = setTimeout(() => {
            sidebar.classList.remove('expanded');
            sidebar.classList.add('collapsed');
        }, 300); // Etwas längere Verzögerung beim Verlassen
    });
    
    // Initialer Zustand: collapsed
    sidebar.classList.add('collapsed');
    
    // Add smooth hover effects for individual links
    const navLinks = sidebar.querySelectorAll('.vntr-nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            // Add any additional hover effects here
        });
        
        link.addEventListener('mouseleave', function() {
            // Remove any additional hover effects here
        });
    });
}

// Flash Messages Auto-Hide
function initFlashMessages() {
    const flashMessages = document.querySelectorAll('.vntr-flash-message');
    
    flashMessages.forEach(message => {
        // Auto-hide after 5 seconds
        setTimeout(() => {
            message.style.transition = 'opacity 0.5s ease';
            message.style.opacity = '0';
            
            setTimeout(() => {
                if (message.parentNode) {
                    message.parentNode.removeChild(message);
                }
            }, 500);
        }, 5000);
        
        // Add click-to-dismiss functionality
        message.addEventListener('click', function() {
            this.style.transition = 'opacity 0.3s ease';
            this.style.opacity = '0';
            
            setTimeout(() => {
                if (this.parentNode) {
                    this.parentNode.removeChild(this);
                }
            }, 300);
        });
    });
}

// Layout Management based on Content Type
function initLayoutManagement() {
    const contentContainer = document.getElementById('content-container');
    const hasContextArea = document.querySelector('.vntr-context-area') !== null;
    
    if (contentContainer) {
        if (hasContextArea) {
            contentContainer.classList.remove('no-context');
            contentContainer.classList.add('with-context');
        } else {
            contentContainer.classList.remove('with-context');
            contentContainer.classList.add('no-context');
        }
    }
}

// Utility Functions
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `vntr-flash-message alert alert-${type}`;
    notification.textContent = message;
    notification.style.cursor = 'pointer';
    
    // Find flash messages container or create one
    let container = document.querySelector('.vntr-flash-messages');
    if (!container) {
        container = document.createElement('div');
        container.className = 'vntr-flash-messages';
        const contentArea = document.querySelector('.vntr-content-area');
        if (contentArea) {
            contentArea.insertBefore(container, contentArea.firstChild);
        }
    }
    
    // Add notification to container
    container.appendChild(notification);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        notification.style.transition = 'opacity 0.5s ease';
        notification.style.opacity = '0';
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 500);
    }, 5000);
    
    // Click to dismiss
    notification.addEventListener('click', function() {
        this.style.transition = 'opacity 0.3s ease';
        this.style.opacity = '0';
        
        setTimeout(() => {
            if (this.parentNode) {
                this.parentNode.removeChild(this);
            }
        }, 300);
    });
}

// Export functions for global use
window.vntrApp = {
    toggleContextArea,
    showNotification
};
