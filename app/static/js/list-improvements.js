// Click-to-Open Funktionalität für Tabellenzeilen
document.addEventListener('DOMContentLoaded', function() {
    
    // Click-to-Open für Tools
    const toolRows = document.querySelectorAll('[data-tool-id]');
    toolRows.forEach(row => {
        row.addEventListener('click', function(e) {
            // Ignoriere Klicks auf Buttons und Links
            if (e.target.closest('button') || e.target.closest('a') || e.target.closest('.btn')) {
                return;
            }
            
            const toolId = this.getAttribute('data-tool-id');
            if (toolId) {
                window.location.href = `/tools/view/${toolId}`;
            }
        });
    });
    
    // Click-to-Open für Integrations
    const integrationRows = document.querySelectorAll('[data-integration-id]');
    integrationRows.forEach(row => {
        row.addEventListener('click', function(e) {
            // Ignoriere Klicks auf Buttons und Links
            if (e.target.closest('button') || e.target.closest('a') || e.target.closest('.btn')) {
                return;
            }
            
            const integrationId = this.getAttribute('data-integration-id');
            if (integrationId) {
                window.location.href = `/integrations/view/${integrationId}`;
            }
        });
    });
    
    // Hover-Effekte für bessere UX
    const clickableRows = document.querySelectorAll('.clickable-row');
    clickableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.cursor = 'pointer';
        });
    });
});

// Filter-Funktionen erweitern
function applyFilters() {
    const searchInput = document.querySelector('input[name="search"]');
    const filters = document.querySelectorAll('select[name]');
    
    // Auto-Submit für Suchfeld mit Debouncing
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            // Auto-Submit nach 500ms ohne weitere Eingabe
            this.closest('form').submit();
        }, 500));
    }
    
    // Auto-Submit für alle Select-Filter
    filters.forEach(filter => {
        filter.addEventListener('change', function() {
            this.closest('form').submit();
        });
    });
}

// Debounce-Funktion für Performance
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Filter-Toggle Funktionalität
function toggleFilterPanel() {
    const panel = document.querySelector('.filter-panel');
    if (panel) {
        panel.classList.toggle('hidden');
    }
}

// Initialisiere Filter beim Laden der Seite
document.addEventListener('DOMContentLoaded', applyFilters);
