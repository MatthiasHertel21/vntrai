// Initializer for agent_run_view page

document.addEventListener('DOMContentLoaded', function() {
    // Set globals from template context
    window.taskDefinitions = window.taskDefinitions || [];
    window.agentRunUuid = window.agentRunUuid || '';
    
    // Restore active task
    restoreActiveTask(window.agentRunUuid);
    
    // Load saved task results
    loadSavedTaskResults();
    
     // Setup action buttons
    const executeBtn = document.getElementById('executeActiveTaskBtn');
    if (executeBtn) {
        executeBtn.addEventListener('click', function() {
            if (window.activeTaskIndex !== null) {
                executeTask(window.activeTaskIndex);
            }
        });
    }

    const stopBtn = document.getElementById('stopActiveTaskBtn');
    if (stopBtn) {
        stopBtn.addEventListener('click', function() {
            stopActiveTask();
        });
    }

    const saveBtn = document.getElementById('saveActiveTaskBtn');
    if (saveBtn) {
        saveBtn.addEventListener('click', function() {
            autoSaveTaskInputs();
        });
    }
});
