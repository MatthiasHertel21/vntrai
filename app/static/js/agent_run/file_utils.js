/**
 * File Utilities for Agent Run View
 * Handles file downloads and content processing
 */

/**
 * Extract text content from HTML
 * @param {string} html - HTML content
 * @returns {string} Plain text content
 */
function getTextContent(html) {
    const temp = document.createElement('div');
    temp.innerHTML = html;
    return temp.textContent || temp.innerText || '';
}

/**
 * Download a file with given content
 * @param {string} content - File content
 * @param {string} filename - Name of the file
 * @param {string} contentType - MIME type of the file
 */
function downloadFile(content, filename, contentType) {
    const blob = new Blob([content], { type: contentType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @param {string} successMessage - Success notification message
 * @param {string} errorMessage - Error notification message
 */
function copyToClipboard(text, successMessage = 'Copied to clipboard!', errorMessage = 'Failed to copy to clipboard') {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification(successMessage, 'success');
        }).catch(err => {
            console.error('Failed to copy to clipboard:', err);
            showNotification(errorMessage, 'error');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            const successful = document.execCommand('copy');
            if (successful) {
                showNotification(successMessage, 'success');
            } else {
                showNotification(errorMessage, 'error');
            }
        } catch (err) {
            console.error('Fallback copy failed:', err);
            showNotification(errorMessage, 'error');
        }
        
        document.body.removeChild(textArea);
    }
}

/**
 * Generate timestamp for file names
 * @returns {string} Formatted timestamp
 */
function getTimestamp() {
    const now = new Date();
    return now.toISOString().slice(0, 19).replace(/[:.]/g, '-');
}

// Export functions for global use
window.getTextContent = getTextContent;
window.downloadFile = downloadFile;
window.copyToClipboard = copyToClipboard;
window.getTimestamp = getTimestamp;
