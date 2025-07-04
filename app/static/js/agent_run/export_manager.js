/**
 * Export Manager for Agent Run View
 * Handles export functionality and language selection
 */

class ExportManager {
    constructor() {
        this.globalExportBtn = null;
        this.globalExportDropdown = null;
        this.globalLanguageSelect = null;
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.setupElements();
            this.setupEventListeners();
            this.loadLanguagePreference();
        });
    }

    setupElements() {
        this.globalExportBtn = document.getElementById('globalExportBtn');
        this.globalExportDropdown = document.getElementById('globalExportDropdown');
        this.globalLanguageSelect = document.getElementById('globalLanguageSelect');
    }

    setupEventListeners() {
        // Global Export Button Toggle
        if (this.globalExportBtn && this.globalExportDropdown) {
            this.globalExportBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.globalExportDropdown.classList.toggle('hidden');
            });
            
            // Close dropdown when clicking outside
            document.addEventListener('click', (e) => {
                if (!this.globalExportBtn.contains(e.target) && !this.globalExportDropdown.contains(e.target)) {
                    this.globalExportDropdown.classList.add('hidden');
                }
            });
        }
        
        // Global Export Actions
        document.querySelectorAll('.global-export-action').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const action = button.dataset.action;
                const selectedLanguage = this.globalLanguageSelect?.value || 'auto';
                
                const allResults = this.getAllTaskResults();
                
                if (allResults.length === 0) {
                    showNotification('No task results available to export.', 'warning');
                    return;
                }
                
                this.handleExportAction(action, allResults, selectedLanguage);
                this.globalExportDropdown.classList.add('hidden');
            });
        });
        
        // Global Language Selection Change
        if (this.globalLanguageSelect) {
            this.globalLanguageSelect.addEventListener('change', () => {
                const selectedLanguage = this.globalLanguageSelect.value;
                console.log('Global language changed to:', selectedLanguage);
                
                // Store the preference
                localStorage.setItem('preferredLanguage', selectedLanguage);
                
                // Trigger language change event for other components
                document.dispatchEvent(new CustomEvent('languageChanged', {
                    detail: { language: selectedLanguage }
                }));
            });
        }
    }

    loadLanguagePreference() {
        if (this.globalLanguageSelect) {
            const savedLanguage = localStorage.getItem('preferredLanguage');
            if (savedLanguage) {
                this.globalLanguageSelect.value = savedLanguage;
            }
        }
    }

    getAllTaskResults() {
        const allResults = [];
        document.querySelectorAll('.task-result-section').forEach((section, index) => {
            const taskName = section.querySelector('h4')?.textContent || `Task ${index + 1}`;
            const resultArea = section.querySelector('.result-output-area');
            const content = resultArea?.innerHTML || '';
            
            if (content && !content.includes('Execute task to see results')) {
                allResults.push({
                    taskName: taskName,
                    content: content,
                    index: index
                });
            }
        });
        return allResults;
    }

    handleExportAction(action, results, language) {
        const timestamp = getTimestamp();
        
        switch(action) {
            case 'clipboard':
                this.exportToClipboard(results, language);
                break;
            case 'text':
                this.exportToText(results, language, timestamp);
                break;
            case 'markdown':
                this.exportToMarkdown(results, language, timestamp);
                break;
            case 'word':
                this.exportToWord(results, language, timestamp);
                break;
            case 'pdf':
                this.exportToPdf(results, language, timestamp);
                break;
            default:
                showNotification(`Export format "${action}" not implemented yet.`, 'warning');
        }
    }

    exportToClipboard(results, language) {
        const text = results.map(r => `${r.taskName}:\n${getTextContent(r.content)}\n`).join('\n');
        copyToClipboard(text, 'Results copied to clipboard!', 'Failed to copy results to clipboard');
    }

    exportToText(results, language, timestamp) {
        const text = results.map(r => `${r.taskName}:\n${getTextContent(r.content)}\n`).join('\n');
        downloadFile(text, `agent-results-${timestamp}.txt`, 'text/plain');
        showNotification('Text file downloaded successfully!', 'success');
    }

    exportToMarkdown(results, language, timestamp) {
        const markdown = results.map(r => `# ${r.taskName}\n\n${getTextContent(r.content)}\n`).join('\n');
        downloadFile(markdown, `agent-results-${timestamp}.md`, 'text/markdown');
        showNotification('Markdown file downloaded successfully!', 'success');
    }

    exportToWord(results, language, timestamp) {
        // Basic HTML to Word conversion
        const html = `
            <html>
            <head>
                <meta charset="utf-8">
                <title>Agent Results - ${timestamp}</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    h1 { color: #0cc0df; border-bottom: 2px solid #0cc0df; padding-bottom: 10px; }
                    hr { border: 1px solid #ddd; margin: 30px 0; }
                    .task-content { margin: 20px 0; }
                </style>
            </head>
            <body>
                <h1>Agent Run Results</h1>
                <p>Generated on: ${new Date().toLocaleString()}</p>
                <p>Language: ${language}</p>
                <hr>
                ${results.map(r => `
                    <h2>${r.taskName}</h2>
                    <div class="task-content">${r.content}</div>
                    <hr>
                `).join('')}
            </body>
            </html>
        `;
        downloadFile(html, `agent-results-${timestamp}.doc`, 'application/msword');
        showNotification('Word document downloaded successfully!', 'success');
    }

    exportToPdf(results, language, timestamp) {
        // This would require a PDF library like jsPDF
        // For now, we'll show a placeholder message
        showNotification('PDF export coming soon! Use Word export as alternative.', 'info');
    }

    // Public methods for external access
    getSelectedLanguage() {
        return this.globalLanguageSelect?.value || 'auto';
    }

    setSelectedLanguage(language) {
        if (this.globalLanguageSelect) {
            this.globalLanguageSelect.value = language;
            localStorage.setItem('preferredLanguage', language);
        }
    }
}

// Initialize export manager
const exportManager = new ExportManager();

// Export for global access
window.exportManager = exportManager;
