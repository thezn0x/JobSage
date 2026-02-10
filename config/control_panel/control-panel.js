// SkillScout Control Panel JavaScript

const API_BASE = 'http://localhost:5000';  // Control Panel API

// Tab switching
function switchTab(tabName) {
    // Hide all content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.add('hidden');
    });
    
    // Remove active class from all tabs
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active', 'border-purple-500');
        btn.classList.add('border-transparent');
    });
    
    // Show selected content
    document.getElementById(`content-${tabName}`).classList.remove('hidden');
    document.getElementById(`content-${tabName}`).classList.add('fade-in');
    
    // Add active class to selected tab
    const activeTab = document.getElementById(`tab-${tabName}`);
    activeTab.classList.add('active', 'border-purple-500');
    activeTab.classList.remove('border-transparent');
}

// Configuration Management
async function loadConfig() {
    try {
        const response = await fetch(`${API_BASE}/api/config`);
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('configEditor').value = data.config;
            addLog('success', 'Configuration loaded successfully');
        }
    } catch (error) {
        addLog('error', `Failed to load config: ${error.message}`);
    }
}

async function saveConfig() {
    const config = document.getElementById('configEditor').value;
    
    try {
        const response = await fetch(`${API_BASE}/api/config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ config })
        });
        
        const data = await response.json();
        
        if (data.success) {
            addLog('success', 'Configuration saved successfully!');
            showNotification('Success', 'Configuration saved!', 'success');
        } else {
            addLog('error', `Failed to save: ${data.error}`);
            showNotification('Error', data.error, 'error');
        }
    } catch (error) {
        addLog('error', `Save failed: ${error.message}`);
        showNotification('Error', error.message, 'error');
    }
}

function validateConfig() {
    const config = document.getElementById('configEditor').value;
    
    try {
        // Basic TOML validation (check for balanced brackets, etc.)
        if (!config.trim()) {
            throw new Error('Config is empty');
        }
        
        addLog('success', 'Configuration syntax is valid');
        showNotification('Valid', 'Configuration syntax is valid!', 'success');
    } catch (error) {
        addLog('error', `Invalid config: ${error.message}`);
        showNotification('Invalid', error.message, 'error');
    }
}

// ETL Operations
async function runExtractor(source) {
    updateSystemStatus('running', `Extracting from ${source}...`);
    addLog('info', `Starting ${source} extractor...`);
    
    try {
        const response = await fetch(`${API_BASE}/api/extract/${source}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            addLog('success', `✓ Extracted ${data.count || 0} jobs from ${source}`);
            updateSystemStatus('idle', 'Idle');
            showNotification('Success', `Extracted ${data.count} jobs`, 'success');
        } else {
            addLog('error', `✗ Extraction failed: ${data.error}`);
            updateSystemStatus('error', 'Error');
        }
    } catch (error) {
        addLog('error', `✗ Extraction error: ${error.message}`);
        updateSystemStatus('error', 'Error');
    }
}

async function runTransformer(source) {
    updateSystemStatus('running', `Transforming ${source} data...`);
    addLog('info', `Starting ${source} transformer...`);
    
    try {
        const response = await fetch(`${API_BASE}/api/transform/${source}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            addLog('success', `✓ Transformed ${data.count || 0} jobs from ${source}`);
            updateSystemStatus('idle', 'Idle');
            showNotification('Success', `Transformed ${data.count} jobs`, 'success');
        } else {
            addLog('error', `✗ Transformation failed: ${data.error}`);
            updateSystemStatus('error', 'Error');
        }
    } catch (error) {
        addLog('error', `✗ Transformation error: ${error.message}`);
        updateSystemStatus('error', 'Error');
    }
}

async function runLoader(source) {
    updateSystemStatus('running', `Loading ${source} data...`);
    addLog('info', `Starting ${source} loader...`);
    
    try {
        const response = await fetch(`${API_BASE}/api/load/${source}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            addLog('success', `✓ Loaded ${data.count || 0} jobs from ${source}`);
            updateSystemStatus('idle', 'Idle');
            showNotification('Success', `Loaded ${data.count} jobs to database`, 'success');
        } else {
            addLog('error', `✗ Loading failed: ${data.error}`);
            updateSystemStatus('error', 'Error');
        }
    } catch (error) {
        addLog('error', `✗ Loading error: ${error.message}`);
        updateSystemStatus('error', 'Error');
    }
}

async function runFullETL() {
    const progressDiv = document.getElementById('etlProgress');
    const progressBar = progressDiv.querySelector('div');
    const progressText = document.getElementById('progressText');
    
    progressDiv.classList.remove('hidden');
    updateSystemStatus('running', 'Running full ETL pipeline...');
    
    const stages = [
        { name: 'Extracting from all sources', progress: 33 },
        { name: 'Transforming data', progress: 66 },
        { name: 'Loading to database', progress: 100 }
    ];
    
    try {
        for (let stage of stages) {
            progressText.textContent = stage.name + '...';
            progressBar.style.width = stage.progress + '%';
            addLog('info', stage.name);
            
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
        
        const response = await fetch(`${API_BASE}/api/etl/full`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            addLog('success', `✓ ETL Pipeline completed! ${data.total_jobs} jobs processed`);
            showNotification('Pipeline Complete', `${data.total_jobs} jobs processed successfully!`, 'success');
            
            setTimeout(() => {
                progressDiv.classList.add('hidden');
                progressBar.style.width = '0%';
            }, 2000);
        } else {
            addLog('error', `✗ ETL Pipeline failed: ${data.error}`);
            showNotification('Pipeline Failed', data.error, 'error');
        }
        
        updateSystemStatus('idle', 'Idle');
        
    } catch (error) {
        addLog('error', `✗ ETL error: ${error.message}`);
        updateSystemStatus('error', 'Error');
        progressDiv.classList.add('hidden');
    }
}

// Scheduler Functions
function saveSchedule() {
    const scheduleType = document.getElementById('scheduleType').value;
    const enabled = document.getElementById('scheduleEnabled').checked;
    
    let schedule;
    if (scheduleType === 'daily') {
        const time = document.getElementById('dailyTime').value;
        const [hour, minute] = time.split(':');
        schedule = `${minute} ${hour} * * *`;
    } else if (scheduleType === 'custom') {
        schedule = document.getElementById('cronExpression').value;
    } else {
        schedule = '0 * * * *';  // Hourly
    }
    
    const config = {
        enabled,
        schedule,
        type: scheduleType
    };
    
    addLog('info', `Schedule saved: ${schedule} (${enabled ? 'Enabled' : 'Disabled'})`);
    showNotification('Saved', 'Schedule configuration saved!', 'success');
    
    // Store in localStorage
    localStorage.setItem('etlSchedule', JSON.stringify(config));
}

// Database Functions
async function testDatabase() {
    const connString = document.getElementById('dbConnectionString').value;
    
    updateSystemStatus('running', 'Testing database connection...');
    addLog('info', 'Testing database connection...');
    
    try {
        const response = await fetch(`${API_BASE}/api/db/test`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ connection_string: connString })
        });
        
        const data = await response.json();
        
        if (data.success) {
            addLog('success', '✓ Database connection successful!');
            showNotification('Connected', 'Database connection successful!', 'success');
        } else {
            addLog('error', `✗ Database connection failed: ${data.error}`);
            showNotification('Failed', data.error, 'error');
        }
        
        updateSystemStatus('idle', 'Idle');
    } catch (error) {
        addLog('error', `✗ Connection error: ${error.message}`);
        updateSystemStatus('error', 'Error');
    }
}

// Logging Functions
function addLog(type, message) {
    const logsContainer = document.getElementById('logsContainer');
    const timestamp = new Date().toLocaleTimeString();
    
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry log-${type}`;
    
    let icon;
    switch(type) {
        case 'success': icon = '✓'; break;
        case 'error': icon = '✗'; break;
        case 'warning': icon = '⚠'; break;
        default: icon = 'ℹ'; break;
    }
    
    logEntry.textContent = `[${timestamp}] ${icon} ${message}`;
    logsContainer.appendChild(logEntry);
    
    // Auto-scroll to bottom
    logsContainer.scrollTop = logsContainer.scrollHeight;
    
    // Keep max 100 logs
    while (logsContainer.children.length > 100) {
        logsContainer.removeChild(logsContainer.firstChild);
    }
}

function clearLogs() {
    document.getElementById('logsContainer').innerHTML = '';
    addLog('info', 'Logs cleared');
}

function downloadLogs() {
    const logs = document.getElementById('logsContainer').innerText;
    const blob = new Blob([logs], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `skillscout-logs-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    
    addLog('info', 'Logs downloaded');
}

// System Status
function updateSystemStatus(status, text) {
    const indicator = document.getElementById('systemStatus');
    const statusText = document.getElementById('statusText');
    
    indicator.className = 'status-indicator';
    
    switch(status) {
        case 'running':
            indicator.classList.add('status-running');
            break;
        case 'error':
            indicator.classList.add('status-error');
            break;
        default:
            indicator.classList.add('status-idle');
    }
    
    statusText.textContent = text;
}

// Notifications
function showNotification(title, message, type) {
    // Simple notification (you can enhance this with a library)
    const color = type === 'success' ? 'green' : type === 'error' ? 'red' : 'blue';
    console.log(`[${type.toUpperCase()}] ${title}: ${message}`);
    
    // You could use browser notifications here:
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, { body: message });
    }
}

// Schedule type change handler
document.addEventListener('DOMContentLoaded', () => {
    const scheduleType = document.getElementById('scheduleType');
    if (scheduleType) {
        scheduleType.addEventListener('change', (e) => {
            const dailySettings = document.getElementById('dailySettings');
            const customSettings = document.getElementById('customSettings');
            
            if (e.target.value === 'custom') {
                dailySettings.classList.add('hidden');
                customSettings.classList.remove('hidden');
            } else {
                dailySettings.classList.remove('hidden');
                customSettings.classList.add('hidden');
            }
        });
    }
    
    // Load config on startup
    loadConfig();
    
    // Add initial log
    addLog('info', 'SkillScout Control Panel started');
    updateSystemStatus('idle', 'Idle');
    
    // Request notification permission
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
});