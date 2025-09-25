let socket;
let selectedFile = null;

const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const startBtn = document.getElementById('startBtn');
const fileName = document.getElementById('fileName');
const languageSelect = document.getElementById('languageSelect');
const connectionStatus = document.getElementById('connectionStatus');
const debugInfo = document.getElementById('debugInfo');
const status = document.getElementById('status');
const transcriptionText = document.getElementById('transcriptionText');
const languageInfo = document.getElementById('languageInfo');

// Debug function
function debugLog(message) {
    console.log('[DEBUG]', message);
    const timestamp = new Date().toLocaleTimeString();
    debugInfo.innerHTML += `<div>[${timestamp}] ${message}</div>`;
    debugInfo.scrollTop = debugInfo.scrollHeight;
}

// Initialize Socket.IO connection
function initSocket() {
    try {
        debugLog('Initializing Socket.IO connection...');
        socket = io();

        socket.on('connect', function() {
            debugLog('Socket.IO connected successfully');
            connectionStatus.textContent = '🟢 Connected to server';
            connectionStatus.className = 'connection-status connected';
        });

        socket.on('connect_error', function(error) {
            debugLog('Socket.IO connection error: ' + error);
            connectionStatus.textContent = '🔴 Connection failed: ' + error;
            connectionStatus.className = 'connection-status error';
        });

        socket.on('disconnect', function() {
            debugLog('Socket.IO disconnected');
            connectionStatus.textContent = '🟡 Disconnected from server';
            connectionStatus.className = 'connection-status disconnected';
        });

        socket.on('status', function(data) {
            debugLog('Status update: ' + data.message);
            showStatus(data.message, 'processing');
        });

        socket.on('transcription_segment', function(data) {
            debugLog('Received transcription segment: ' + data.text.substring(0, 50) + '...');
            const currentText = transcriptionText.value;
            transcriptionText.value = currentText + data.text;
            transcriptionText.scrollTop = transcriptionText.scrollHeight;
        });

        socket.on('transcription_complete', function(data) {
            debugLog('Transcription complete. Language: ' + data.language);
            transcriptionText.value = data.text;
            languageInfo.textContent = `Detected language: ${data.language}`;
            languageInfo.classList.remove('hidden');
            showStatus('Transcription completed!', '');
        });

        socket.on('error', function(data) {
            debugLog('Server error: ' + data.message);
            showStatus(data.message, 'error');
        });

    } catch (error) {
        debugLog('Failed to initialize Socket.IO: ' + error.message);
        connectionStatus.textContent = '🔴 Socket.IO initialization failed';
        connectionStatus.className = 'connection-status error';
    }
}

// File selection handler
uploadBtn.addEventListener('click', function() {
    debugLog('Upload button clicked');
    fileInput.click();
});

fileInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        debugLog('File selected: ' + file.name + ' (size: ' + file.size + ' bytes)');
        selectedFile = file;
        fileName.textContent = file.name;
        startBtn.classList.remove('hidden');
        showStatus('File selected. Click "Start Transcription" to begin.', '');
    }
});

// Start transcription handler
startBtn.addEventListener('click', function() {
    if (!selectedFile) {
        debugLog('No file selected for transcription');
        showStatus('Please select a file first', 'error');
        return;
    }

    if (!socket || !socket.connected) {
        debugLog('Socket not connected, cannot start transcription');
        showStatus('Not connected to server. Please refresh the page.', 'error');
        return;
    }

    debugLog('Starting transcription for file: ' + selectedFile.name);
    uploadFile(selectedFile);
});

function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    // Get selected language
    const selectedLanguage = languageSelect.value;
    formData.append('language', selectedLanguage);
    debugLog('Selected language: ' + selectedLanguage);

    debugLog('Uploading file to server...');
    showStatus('Uploading file...', 'processing');
    transcriptionText.value = '';
    languageInfo.classList.add('hidden');

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        debugLog('Upload response status: ' + response.status);
        return response.json();
    })
    .then(data => {
        debugLog('Upload response data: ' + JSON.stringify(data));
        if (data.error) {
            showStatus(data.error, 'error');
        } else {
            showStatus('File uploaded. Processing with ' + getLanguageName(selectedLanguage) + '...', 'processing');
        }
    })
    .catch(error => {
        debugLog('Upload failed: ' + error.message);
        showStatus('Upload failed: ' + error.message, 'error');
    });
}

function getLanguageName(languageCode) {
    const languages = {
        'auto': 'Auto-detect',
        'ru-RU': 'Russian',
        'en-US': 'English (US)',
        'en-GB': 'English (UK)',
        'es-ES': 'Spanish',
        'fr-FR': 'French',
        'de-DE': 'German',
        'it-IT': 'Italian',
        'pt-BR': 'Portuguese',
        'ja-JP': 'Japanese',
        'ko-KR': 'Korean',
        'zh-CN': 'Chinese',
        'ar-SA': 'Arabic',
        'hi-IN': 'Hindi',
        'tr-TR': 'Turkish',
        'nl-NL': 'Dutch'
    };
    return languages[languageCode] || languageCode;
}

function showStatus(message, type = '') {
    status.textContent = message;
    status.className = 'status';
    if (type) {
        status.classList.add(type);
    }
    status.classList.remove('hidden');
}

function hideStatus() {
    status.classList.add('hidden');
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    debugLog('Page loaded, initializing application...');
    initSocket();
});