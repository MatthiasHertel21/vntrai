/**
 * Sessions Management for Agent Edit Page
 * Handles loading, filtering, and managing agent sessions/runs
 */

// Global sessions data
let agentSessions = [];
let filteredSessions = [];

// Initialize sessions when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Sessions management script DOM ready, checking agent data...');
    if (window.agentData && window.agentData.id) {
        console.log('Loading sessions for agent:', window.agentData.id);
        loadSessions();
    } else {
        console.log('No agent data found or missing agent ID');
    }
});

// Load sessions from API
async function loadSessions() {
    console.log('loadSessions called for agent:', window.agentData?.id);
    try {
        const agentId = window.agentData.id;
        if (!agentId) {
            throw new Error('No agent ID available');
        }
        
        console.log('Fetching sessions from API:', `/agents/api/${agentId}/sessions`);
        const response = await fetch(`/agents/api/${agentId}/sessions`);
        
        console.log('Sessions API response status:', response.status);
        if (response.ok) {
            const data = await response.json();
            console.log('Sessions data received:', data);
            agentSessions = data.sessions || [];
            filteredSessions = [...agentSessions];
            updateSessionsDisplay();
        } else {
            throw new Error(`API returned ${response.status}: ${response.statusText}`);
        }
    } catch (error) {
        console.error('Error loading sessions:', error);
        showSessionsError('Failed to load sessions: ' + error.message);
    }
}

// Update sessions display
function updateSessionsDisplay() {
    console.log('updateSessionsDisplay called, filtered sessions:', filteredSessions.length);
    const loading = document.getElementById('sessionsLoading');
    const empty = document.getElementById('sessionsEmpty');
    const list = document.getElementById('sessionsList');
    const count = document.getElementById('sessionsCount');
    
    console.log('Elements found:', {
        loading: !!loading,
        empty: !!empty,
        list: !!list,
        count: !!count
    });
    
    // Hide loading
    if (loading) {
        loading.classList.add('hidden');
        console.log('Hidden loading indicator');
    }
    
    // Update count
    if (count) {
        count.textContent = `(${filteredSessions.length} session${filteredSessions.length !== 1 ? 's' : ''})`;
        console.log('Updated sessions count');
    }
    
    if (filteredSessions.length === 0) {
        // Show empty state
        if (empty) {
            empty.classList.remove('hidden');
            console.log('Showed empty state');
        }
        if (list) list.classList.add('hidden');
    } else {
        // Show sessions list
        if (empty) empty.classList.add('hidden');
        if (list) {
            list.classList.remove('hidden');
            renderSessionsList();
            console.log('Rendered sessions list with', filteredSessions.length, 'sessions');
        }
    }
}

// Render sessions list
function renderSessionsList() {
    const list = document.getElementById('sessionsList');
    if (!list) return;
    
    list.innerHTML = '';
    
    filteredSessions.forEach(session => {
        const sessionElement = createSessionElement(session);
        list.appendChild(sessionElement);
    });
}

// Create session element
function createSessionElement(session) {
    const div = document.createElement('div');
    div.className = 'px-3 py-2 border border-gray-200 rounded bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer';
    div.onclick = () => openSession(session.id);
    
    // Determine status display
    let statusIcon, statusColor, statusText;
    switch (session.status) {
        case 'active':
        case 'running':
            statusIcon = 'bi-play-circle-fill';
            statusColor = 'text-green-500';
            statusText = 'Active';
            break;
        case 'completed':
            statusIcon = 'bi-check-circle-fill';
            statusColor = 'text-blue-500';
            statusText = 'Completed';
            break;
        case 'failed':
        case 'error':
            statusIcon = 'bi-x-circle-fill';
            statusColor = 'text-red-500';
            statusText = 'Failed';
            break;
        case 'paused':
            statusIcon = 'bi-pause-circle-fill';
            statusColor = 'text-yellow-500';
            statusText = 'Paused';
            break;
        default:
            statusIcon = 'bi-circle';
            statusColor = 'text-gray-500';
            statusText = 'Created';
    }
    
    // Generate session name if not provided
    const sessionName = session.name || `Session ${session.id.substring(0, 8)}`;
    
    // Format last used date
    let lastUsedText = 'Never';
    if (session.last_activity) {
        try {
            const lastUsed = new Date(session.last_activity);
            const now = new Date();
            const diffHours = Math.floor((now - lastUsed) / (1000 * 60 * 60));
            
            if (diffHours < 1) {
                lastUsedText = 'Just now';
            } else if (diffHours < 24) {
                lastUsedText = `${diffHours}h ago`;
            } else {
                const diffDays = Math.floor(diffHours / 24);
                lastUsedText = `${diffDays}d ago`;
            }
        } catch (e) {
            lastUsedText = 'Unknown';
        }
    }
    
    div.innerHTML = `
        <div class="flex items-center justify-between">
            <div class="flex items-center flex-1 min-w-0">
                <!-- Status icon -->
                <div class="flex-shrink-0 mr-2">
                    <i class="bi ${statusIcon} ${statusColor}" title="${statusText}"></i>
                </div>
                
                <!-- Session info -->
                <div class="flex-1 min-w-0">
                    <div class="flex items-center">
                        <span class="font-medium text-gray-900 text-sm truncate">${sessionName}</span>
                        <span class="ml-2 text-xs text-gray-500">(${session.age_days}d old)</span>
                    </div>
                    <div class="text-xs text-gray-500">
                        Last used: ${lastUsedText} • ${session.completed_tasks}/${session.total_tasks} tasks completed
                    </div>
                </div>
            </div>
            
            <!-- Actions -->
            <div class="flex items-center ml-2">
                <button type="button" 
                        onclick="event.stopPropagation(); deleteSession('${session.id}')" 
                        class="p-1 text-red-500 hover:text-red-700 transition-colors"
                        title="Delete session">
                    <i class="bi bi-trash" style="font-size: 12px;"></i>
                </button>
            </div>
        </div>
    `;
    
    return div;
}

// Filter sessions
function filterSessions() {
    const filter = document.getElementById('sessionStatusFilter')?.value || 'all';
    
    if (filter === 'all') {
        filteredSessions = [...agentSessions];
    } else if (filter === 'active') {
        filteredSessions = agentSessions.filter(s => s.status === 'created' || s.status === 'open');
    } else {
        filteredSessions = agentSessions.filter(s => s.status === filter);
    }
    
    updateSessionsDisplay();
}

// Open session
function openSession(sessionUuid) {
    if (!sessionUuid) return;
    
    const agentId = window.agentData.id;
    // Open session in new tab/window
    window.open(`/agents/${agentId}/runs/${sessionUuid}`, '_blank');
}

// Delete session
async function deleteSession(sessionId) {
    if (!confirm('Are you sure you want to delete this session?')) {
        return;
    }
    
    try {
        const agentId = window.agentData.id;
        const response = await fetch(`/agents/api/${agentId}/sessions/${sessionId}`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': document.querySelector('input[name="csrf_token"]')?.value || ''
            }
        });
        
        if (response.ok) {
            // Remove from local data
            agentSessions = agentSessions.filter(s => s.id !== sessionId);
            filterSessions(); // Refresh display
            showNotificationSafe('Session deleted successfully', true);
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Failed to delete session');
        }
    } catch (error) {
        console.error('Error deleting session:', error);
        showNotificationSafe('Failed to delete session: ' + error.message, false);
    }
}

// Cleanup sessions
async function cleanupSessions() {
    const filter = document.getElementById('sessionStatusFilter')?.value || 'all';
    let confirmMessage = 'Are you sure you want to cleanup sessions?';
    
    if (filter === 'closed') {
        confirmMessage = 'Delete all closed sessions?';
    } else if (filter === 'error') {
        confirmMessage = 'Delete all error sessions?';
    } else {
        confirmMessage = 'Delete all closed and error sessions?';
    }
    
    if (!confirm(confirmMessage)) {
        return;
    }
    
    try {
        const agentId = window.agentData.id;
        let statusFilter = 'all';
        
        if (filter === 'closed' || filter === 'error') {
            statusFilter = filter;
        }
        
        const response = await fetch(`/agents/api/${agentId}/sessions/cleanup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('input[name="csrf_token"]')?.value || ''
            },
            body: JSON.stringify({ status_filter: statusFilter })
        });
        
        if (response.ok) {
            const result = await response.json();
            showNotificationSafe(`${result.deleted_count} sessions deleted`, true);
            // Reload sessions
            await loadSessions();
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Failed to cleanup sessions');
        }
    } catch (error) {
        console.error('Error cleaning up sessions:', error);
        showNotificationSafe('Failed to cleanup sessions: ' + error.message, false);
    }
}

// Toggle container visibility
function toggleContainer(containerId) {
    const content = document.getElementById(containerId + 'Content');
    const chevron = document.getElementById(containerId + 'Chevron');
    
    if (content && chevron) {
        if (content.classList.contains('hidden')) {
            content.classList.remove('hidden');
            chevron.classList.remove('rotate-[-90deg]');
        } else {
            content.classList.add('hidden');
            chevron.classList.add('rotate-[-90deg]');
        }
    }
}

// Show sessions error
function showSessionsError(message) {
    const loading = document.getElementById('sessionsLoading');
    const empty = document.getElementById('sessionsEmpty');
    const list = document.getElementById('sessionsList');
    
    if (loading) loading.classList.add('hidden');
    if (list) list.classList.add('hidden');
    
    if (empty) {
        empty.classList.remove('hidden');
        empty.innerHTML = `
            <i class="bi bi-exclamation-triangle text-2xl mb-2 text-red-500"></i>
            <p class="text-red-600">${message}</p>
            <button onclick="loadSessions()" class="mt-2 text-sm text-blue-600 hover:text-blue-800">
                Try again
            </button>
        `;
    }
}

// Safe notification function (compatible with existing notification system)
function showNotificationSafe(message, isSuccess) {
    if (typeof showNotification === 'function') {
        showNotification(message, isSuccess);
    } else {
        // Fallback to console and simple alert
        console.log((isSuccess ? 'SUCCESS: ' : 'ERROR: ') + message);
        if (!isSuccess) {
            alert('Error: ' + message);
        }
    }
}

// Make functions globally available
window.loadSessions = loadSessions;
window.filterSessions = filterSessions;
window.openSession = openSession;
window.deleteSession = deleteSession;
window.cleanupSessions = cleanupSessions;
window.toggleContainer = toggleContainer;

console.log('Sessions management functions exported to window:', {
    loadSessions: typeof window.loadSessions,
    filterSessions: typeof window.filterSessions,
    cleanupSessions: typeof window.cleanupSessions
});
