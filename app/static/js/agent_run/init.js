// Initializer for agent_run_view page

document.addEventListener('DOMContentLoaded', function() {
    // Set globals from template context
    window.taskDefinitions = window.taskDefinitions || [];
    window.agentRunUuid = window.agentRunUuid || '';
    
    // Restore active task
    restoreActiveTask(window.agentRunUuid);
     // Setup action buttons
    const executeBtn = document.getElementById('executeActiveTaskBtn');
    if (executeBtn) {
        executeBtn.addEventListener('click', function() {
            if (window.activeTaskIndex !== null) {
                executeTask(window.activeTaskIndex);
            }
        });
    }

    const saveBtn = document.getElementById('saveActiveTaskBtn');
    if (saveBtn) {
        saveBtn.addEventListener('click', function() {
            autoSaveTaskInputs();
        });
    }
});
