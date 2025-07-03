// YouTube URL validation regex patterns
const YOUTUBE_REGEX = [
    /^https?:\/\/(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/,
    /^https?:\/\/(www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]{11})/,
    /^https?:\/\/(www\.)?youtube\.com\/v\/([a-zA-Z0-9_-]{11})/,
    /^https?:\/\/(www\.)?youtube\.com\/playlist\?list=([a-zA-Z0-9_-]+)/
];

// DOM elements
const form = document.getElementById('downloadForm');
const urlInput = document.getElementById('youtubeUrl');
const downloadBtn = document.getElementById('downloadBtn');
const statusDiv = document.getElementById('status');
const errorDiv = document.getElementById('urlError');
const downloadLinkDiv = document.getElementById('downloadLink');

// Backend API endpoint (adjust based on your Flask server setup)
const API_BASE_URL = window.location.origin;
const DOWNLOAD_ENDPOINT = `${API_BASE_URL}/download`;

/**
 * Validate YouTube URL using regex patterns
 * @param {string} url - The URL to validate
 * @returns {boolean} - True if valid YouTube URL
 */
function isValidYouTubeUrl(url) {
    if (!url || typeof url !== 'string') {
        return false;
    }
    
    return YOUTUBE_REGEX.some(regex => regex.test(url.trim()));
}

/**
 * Show error message for URL input
 * @param {string} message - Error message to display
 */
function showUrlError(message) {
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    urlInput.classList.add('error');
}

/**
 * Clear URL error message
 */
function clearUrlError() {
    errorDiv.textContent = '';
    errorDiv.style.display = 'none';
    urlInput.classList.remove('error');
}

/**
 * Show status message
 * @param {string} message - Status message
 * @param {string} type - Message type: 'success', 'error', 'loading'
 */
function showStatus(message, type = 'loading') {
    statusDiv.textContent = message;
    statusDiv.className = `status-message ${type}`;
    statusDiv.style.display = 'block';
}

/**
 * Clear status message
 */
function clearStatus() {
    statusDiv.textContent = '';
    statusDiv.className = 'status-message';
    statusDiv.style.display = 'none';
}

/**
 * Show download link
 * @param {string} downloadUrl - URL to download the file
 * @param {string} filename - Name of the downloaded file
 */
function showDownloadLink(downloadUrl, filename) {
    downloadLinkDiv.innerHTML = `
        <a href="${downloadUrl}" download="${filename}" target="_blank">
            Download ${filename}
        </a>
    `;
    downloadLinkDiv.style.display = 'block';
}

/**
 * Clear download link
 */
function clearDownloadLink() {
    downloadLinkDiv.innerHTML = '';
    downloadLinkDiv.style.display = 'none';
}

/**
 * Set loading state for the download button
 * @param {boolean} isLoading - Whether to show loading state
 */
function setLoadingState(isLoading) {
    downloadBtn.disabled = isLoading;
    downloadBtn.textContent = isLoading ? 'Processing...' : 'Download Video';
    
    if (isLoading) {
        downloadBtn.classList.add('loading');
    } else {
        downloadBtn.classList.remove('loading');
    }
}

/**
 * Send download request to Flask backend
 * @param {string} url - YouTube URL to download
 */
async function sendDownloadRequest(url) {
    try {
        const response = await fetch(DOWNLOAD_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: url.trim()
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || `HTTP error! status: ${response.status}`);
        }

        if (data.success) {
            showStatus('Download completed successfully!', 'success');
            
            // Show download link if provided
            if (data.download_url && data.filename) {
                showDownloadLink(data.download_url, data.filename);
            }
        } else {
            throw new Error(data.error || 'Download failed');
        }

    } catch (error) {
        console.error('Download error:', error);
        showStatus(`Error: ${error.message}`, 'error');
    } finally {
        setLoadingState(false);
    }
}

/**
 * Handle form submission
 * @param {Event} event - Form submit event
 */
function handleFormSubmit(event) {
    event.preventDefault();
    
    // Clear previous messages
    clearUrlError();
    clearStatus();
    clearDownloadLink();
    
    const url = urlInput.value.trim();
    
    // Validate URL
    if (!url) {
        showUrlError('Please enter a YouTube URL');
        return;
    }
    
    if (!isValidYouTubeUrl(url)) {
        showUrlError('Please enter a valid YouTube URL (e.g., https://www.youtube.com/watch?v=...)');
        return;
    }
    
    // Start download process
    setLoadingState(true);
    showStatus('Processing your request...', 'loading');
    
    sendDownloadRequest(url);
}

/**
 * Handle URL input validation on input
 */
function handleUrlInput() {
    const url = urlInput.value.trim();
    
    if (url && !isValidYouTubeUrl(url)) {
        showUrlError('Invalid YouTube URL format');
    } else {
        clearUrlError();
    }
}

// Event listeners
form.addEventListener('submit', handleFormSubmit);

// Real-time URL validation (debounced)
let validationTimeout;
urlInput.addEventListener('input', () => {
    clearTimeout(validationTimeout);
    validationTimeout = setTimeout(handleUrlInput, 500);
});

// Clear error on focus
urlInput.addEventListener('focus', clearUrlError);

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('YouTube Downloader initialized');
    clearStatus();
    clearDownloadLink();
});

created with Comet Assistant
