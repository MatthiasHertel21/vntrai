// UI logic for agent_run_view (menus, notifications, etc.)

function toggleRunActionsMenu(event) {
    event.stopPropagation();
    const menu = document.getElementById('run-actions-menu');
    if (menu) menu.classList.toggle('hidden');
}

function closeRunActionsMenu() {
    const menu = document.getElementById('run-actions-menu');
    if (menu) menu.classList.add('hidden');
}

document.addEventListener('click', function(event) {
    const menu = document.getElementById('run-actions-menu');
    const btn = document.getElementById('run-actions-btn');
    if (menu && btn && !menu.contains(event.target) && !btn.contains(event.target)) {
        closeRunActionsMenu();
    }
});

function refreshRunData(runUuid) {
    const notification = document.createElement('div');
    notification.className = 'alert alert-info alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
    notification.style.zIndex = '1050';
    notification.style.maxWidth = '400px';
    notification.innerHTML = `
        <i class="bi bi-arrow-clockwise mr-2"></i>
        Refreshing run data...
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(notification);
    setTimeout(() => {
        notification.remove();
        window.location.reload();
    }, 2000);
}

function copyJsonData() {
    const jsonCode = document.getElementById('jsonData');
    if (jsonCode) {
        navigator.clipboard.writeText(jsonCode.textContent).then(function() {
            const button = event.target.closest('button');
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-check mr-2"></i>Copied!';
            setTimeout(() => {
                button.innerHTML = originalText;
            }, 2000);
        });
    }
}
