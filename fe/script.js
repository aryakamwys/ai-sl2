// Configuration
const API_BASE_URL = 'http://localhost:8000';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkAPIStatus();
    getHealthCheck();
    initNavigation();
});

// Navigation
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.classList.remove('active');
        item.classList.add('text-slate-600', 'hover:bg-slate-100');
    });
    const activeItem = document.querySelector('.nav-item.active');
    if (activeItem) {
        activeItem.classList.remove('text-slate-600', 'hover:bg-slate-100');
        activeItem.classList.add('bg-blue-50', 'text-blue-600');
    }
}

function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.add('hidden');
    });
    
    // Show selected tab
    document.getElementById(tabName).classList.remove('hidden');
    
    // Update navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active', 'bg-blue-50', 'text-blue-600');
        item.classList.add('text-slate-600', 'hover:bg-slate-100');
    });
    
    const activeItem = document.querySelector(`[data-tab="${tabName}"]`);
    if (activeItem) {
        activeItem.classList.add('active', 'bg-blue-50', 'text-blue-600');
        activeItem.classList.remove('text-slate-600', 'hover:bg-slate-100');
    }
    
    // Update page title
    const titles = {
        'dashboard': 'Dashboard',
        'pollution': 'Pollution Analysis',
        'recommendations': 'Recommendations',
        'data': 'Google Sheets Data',
        'ai': 'AI & RAG System'
    };
    document.getElementById('pageTitle').textContent = titles[tabName] || 'Dashboard';
}

// API Status Check
async function checkAPIStatus() {
    const statusEl = document.getElementById('sidebarApiStatus');
    
    try {
        const response = await fetch(`${API_BASE_URL}/`);
        if (response.ok) {
            statusEl.innerHTML = `
                <div class="w-2 h-2 rounded-full bg-green-500"></div>
                <span class="text-xs text-slate-600 font-medium">API Online</span>
            `;
            statusEl.classList.remove('bg-slate-50');
            statusEl.classList.add('bg-green-50');
        }
    } catch (error) {
        statusEl.innerHTML = `
            <div class="w-2 h-2 rounded-full bg-red-500"></div>
            <span class="text-xs text-slate-600 font-medium">API Offline</span>
        `;
        statusEl.classList.remove('bg-slate-50');
        statusEl.classList.add('bg-red-50');
    }
}

// Health Check
async function getHealthCheck() {
    const resultEl = document.getElementById('healthCheck');
    showLoading(resultEl);

    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        let html = '<div class="space-y-3">';
        html += `<div class="flex items-center justify-between">`;
        html += `<span class="text-sm font-medium text-slate-700">Status</span>`;
        html += `<span class="px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">${data.status}</span>`;
        html += `</div>`;
        html += `<div class="flex items-center justify-between">`;
        html += `<span class="text-sm font-medium text-slate-700">Environment</span>`;
        html += `<span class="text-sm text-slate-600">${data.environment}</span>`;
        html += `</div>`;
        html += '<div class="pt-3 border-t border-slate-200">';
        html += '<p class="text-sm font-medium text-slate-700 mb-2">Services</p>';
        html += '<div class="space-y-2">';
        for (const [service, status] of Object.entries(data.services)) {
            const icon = status ? 'fa-check-circle' : 'fa-times-circle';
            const color = status ? 'text-green-500' : 'text-red-500';
            html += `<div class="flex items-center gap-2">`;
            html += `<i class="fas ${icon} ${color}"></i>`;
            html += `<span class="text-sm text-slate-600">${service}</span>`;
            html += `</div>`;
        }
        html += '</div></div></div>';
        
        resultEl.innerHTML = html;
        resultEl.classList.remove('flex', 'items-center', 'gap-2', 'text-slate-500');
    } catch (error) {
        showError(resultEl, error);
    }
}

// Dashboard Functions
async function getCurrentStatus() {
    const resultEl = document.getElementById('currentStatus');
    showLoading(resultEl);

    try {
        const response = await fetch(`${API_BASE_URL}/api/pollution/current-status`);
        const data = await response.json();
        
        const levelColors = {
            'good': 'bg-green-100 text-green-800 border-green-200',
            'moderate': 'bg-yellow-100 text-yellow-800 border-yellow-200',
            'unhealthy_for_sensitive': 'bg-orange-100 text-orange-800 border-orange-200',
            'unhealthy': 'bg-red-100 text-red-800 border-red-200',
            'very_unhealthy': 'bg-purple-100 text-purple-800 border-purple-200',
            'hazardous': 'bg-red-900 text-white border-red-900'
        };
        
        const color = levelColors[data.pollution_level] || 'bg-slate-100 text-slate-800 border-slate-200';
        
        let html = `<div class="p-4 rounded-lg border ${color}">`;
        html += `<h4 class="font-semibold mb-2">${data.pollution_level.replace(/_/g, ' ').toUpperCase()}</h4>`;
        html += `<p class="text-sm mb-3">${data.description}</p>`;
        html += `<div class="space-y-1 text-sm">`;
        html += `<p><strong>Latest:</strong> ${data.latest_reading.gas_value} ppm</p>`;
        html += `<p><strong>Avg (7d):</strong> ${data.stats.average.toFixed(2)} ppm</p>`;
        html += `<p><strong>Trend:</strong> ${data.stats.trend}</p>`;
        html += `</div></div>`;
        
        resultEl.innerHTML = html;
    } catch (error) {
        showError(resultEl, error);
    }
}

async function getAlerts() {
    const resultEl = document.getElementById('alerts');
    showLoading(resultEl);

    try {
        const response = await fetch(`${API_BASE_URL}/api/pollution/alerts`);
        const data = await response.json();
        
        let html = '';
        
        if (data.alerts && data.alerts.length > 0) {
            html += '<div class="space-y-3">';
            data.alerts.forEach(alert => {
                const severityColors = {
                    'warning': 'bg-yellow-50 border-yellow-200 text-yellow-800',
                    'danger': 'bg-red-50 border-red-200 text-red-800',
                    'info': 'bg-blue-50 border-blue-200 text-blue-800'
                };
                const color = severityColors[alert.severity] || 'bg-slate-50 border-slate-200 text-slate-800';
                html += `<div class="p-4 rounded-lg border ${color}">`;
                html += `<h4 class="font-semibold mb-1">${alert.title}</h4>`;
                html += `<p class="text-sm mb-2">${alert.message}</p>`;
                html += `<span class="text-xs">Priority: ${alert.priority}</span>`;
                html += `</div>`;
            });
            html += '</div>';
        } else {
            html = '<p class="text-sm text-slate-500">No active alerts</p>';
        }
        
        resultEl.innerHTML = html;
    } catch (error) {
        showError(resultEl, error);
    }
}

// Pollution Analysis
async function analyzePollution() {
    const resultEl = document.getElementById('pollutionAnalysis');
    const days = document.getElementById('analysisDays').value;
    showLoading(resultEl);

    try {
        const response = await fetch(`${API_BASE_URL}/api/pollution/analyze?days=${days}`);
        const data = await response.json();
        
        let html = '<div class="mt-4 p-4 bg-slate-50 rounded-lg">';
        html += '<h4 class="font-semibold text-slate-900 mb-3">Statistics</h4>';
        html += '<div class="grid grid-cols-2 gap-4">';
        html += `<div><span class="text-sm text-slate-600">Average</span><p class="text-lg font-semibold">${data.stats.average.toFixed(2)} ppm</p></div>`;
        html += `<div><span class="text-sm text-slate-600">Maximum</span><p class="text-lg font-semibold">${data.stats.max.toFixed(2)} ppm</p></div>`;
        html += `<div><span class="text-sm text-slate-600">Minimum</span><p class="text-lg font-semibold">${data.stats.min.toFixed(2)} ppm</p></div>`;
        html += `<div><span class="text-sm text-slate-600">Trend</span><p class="text-lg font-semibold">${data.stats.trend}</p></div>`;
        html += '</div>';
        
        html += '<h4 class="font-semibold text-slate-900 mt-4 mb-2">Level Distribution</h4>';
        html += '<div class="space-y-1">';
        for (const [level, count] of Object.entries(data.level_distribution)) {
            html += `<div class="flex items-center justify-between text-sm">`;
            html += `<span class="text-slate-600">${level}</span>`;
            html += `<span class="font-medium">${count} readings</span>`;
            html += `</div>`;
        }
        html += '</div></div>';
        
        resultEl.innerHTML = html;
    } catch (error) {
        showError(resultEl, error);
    }
}

// Recommendations
async function getGeneralRecommendations() {
    const resultEl = document.getElementById('generalRecs');
    const userType = document.getElementById('userType').value;
    showLoading(resultEl);

    try {
        const response = await fetch(`${API_BASE_URL}/api/pollution/recommendations`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_type: userType })
        });
        const data = await response.json();
        
        let html = '<div class="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">';
        
        if (data.recommendations && data.recommendations.length > 0) {
            html += '<h4 class="font-semibold text-slate-900 mb-2">Recommendations</h4>';
            html += '<ul class="space-y-1 text-sm text-slate-700">';
            data.recommendations.forEach(rec => {
                html += `<li class="flex items-start gap-2"><i class="fas fa-check-circle text-blue-600 mt-0.5"></i><span>${rec}</span></li>`;
            });
            html += '</ul>';
        }
        
        if (data.health_advice && data.health_advice.length > 0) {
            html += '<h4 class="font-semibold text-slate-900 mt-3 mb-2">Health Advice</h4>';
            html += '<ul class="space-y-1 text-sm text-slate-700">';
            data.health_advice.forEach(advice => {
                html += `<li class="flex items-start gap-2"><i class="fas fa-heart text-red-500 mt-0.5"></i><span>${advice}</span></li>`;
            });
            html += '</ul>';
        }
        
        html += '</div>';
        resultEl.innerHTML = html;
    } catch (error) {
        showError(resultEl, error);
    }
}

async function getIndustrialRecommendations() {
    const resultEl = document.getElementById('industrialRecs');
    const industryType = document.getElementById('industryType').value;
    showLoading(resultEl);

    try {
        const response = await fetch(`${API_BASE_URL}/api/pollution/recommendations`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                user_type: 'industrial',
                industry_type: industryType 
            })
        });
        const data = await response.json();
        
        let html = '<div class="mt-4 space-y-3">';
        
        if (data.industrial_alerts && data.industrial_alerts.length > 0) {
            data.industrial_alerts.forEach(alert => {
                html += `<div class="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">`;
                html += `<p class="text-sm text-yellow-900"><strong>${alert.alert_type}:</strong> ${alert.message}</p>`;
                html += `</div>`;
            });
        }
        
        if (data.recommendations && data.recommendations.length > 0) {
            html += '<div class="p-4 bg-blue-50 border border-blue-200 rounded-lg">';
            html += '<h4 class="font-semibold text-slate-900 mb-2">Actions Required</h4>';
            html += '<ul class="space-y-1 text-sm text-slate-700">';
            data.recommendations.forEach(rec => {
                html += `<li class="flex items-start gap-2"><i class="fas fa-wrench text-blue-600 mt-0.5"></i><span>${rec}</span></li>`;
            });
            html += '</ul></div>';
        }
        
        html += '</div>';
        resultEl.innerHTML = html;
    } catch (error) {
        showError(resultEl, error);
    }
}

async function getSmartRecommendations() {
    const resultEl = document.getElementById('smartRecs');
    const query = document.getElementById('aiQuery').value;
    showLoading(resultEl);

    try {
        const response = await fetch(`${API_BASE_URL}/api/pollution/smart-recommendations`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                query: query,
                user_type: 'general'
            })
        });
        const data = await response.json();
        
        let html = '<div class="mt-4 p-6 bg-gradient-to-br from-purple-50 to-blue-50 border border-purple-200 rounded-lg">';
        html += '<h4 class="font-semibold text-slate-900 mb-3 flex items-center gap-2">';
        html += '<i class="fas fa-robot text-purple-600"></i>AI Response</h4>';
        html += `<p class="text-slate-700 leading-relaxed">${data.ai_response || data.recommendation}</p>`;
        
        if (data.relevant_data && data.relevant_data.length > 0) {
            html += `<p class="text-sm text-slate-600 mt-3">Based on ${data.relevant_data.length} recent readings</p>`;
        }
        
        html += '</div>';
        resultEl.innerHTML = html;
    } catch (error) {
        showError(resultEl, error);
    }
}

// Google Sheets Functions
async function getSheetsInfo() {
    const resultEl = document.getElementById('sheetsInfo');
    showLoading(resultEl);

    try {
        const response = await fetch(`${API_BASE_URL}/api/data/sheets/info`);
        const data = await response.json();
        
        let html = '<div class="mt-4 p-4 bg-slate-50 rounded-lg">';
        html += '<pre class="text-xs overflow-x-auto">' + JSON.stringify(data, null, 2) + '</pre>';
        html += '</div>';
        resultEl.innerHTML = html;
    } catch (error) {
        showError(resultEl, error);
    }
}

async function getSheetsData() {
    const resultEl = document.getElementById('sheetsData');
    const limit = document.getElementById('dataLimit').value;
    showLoading(resultEl);

    try {
        let url = `${API_BASE_URL}/api/data/sheets/data`;
        if (limit) url += `?limit=${limit}`;
        
        const response = await fetch(url);
        const data = await response.json();
        
        let html = `<div class="mt-4">`;
        html += `<p class="text-sm text-slate-600 mb-3">Retrieved: <strong>${data.count}</strong> records</p>`;
        
        if (data.data && data.data.length > 0) {
            html += '<div class="overflow-x-auto"><table class="w-full text-sm"><thead class="bg-slate-100"><tr>';
            const headers = Object.keys(data.data[0]).slice(0, 6);
            headers.forEach(h => {
                html += `<th class="px-3 py-2 text-left font-semibold text-slate-700">${h}</th>`;
            });
            html += '</tr></thead><tbody>';
            
            data.data.slice(0, 10).forEach((row, i) => {
                html += `<tr class="${i % 2 === 0 ? 'bg-white' : 'bg-slate-50'}">`;
                headers.forEach(h => {
                    html += `<td class="px-3 py-2 text-slate-600">${row[h] || '-'}</td>`;
                });
                html += '</tr>';
            });
            html += '</tbody></table></div>';
            
            if (data.data.length > 10) {
                html += `<p class="text-xs text-slate-500 mt-2">Showing first 10 of ${data.data.length} records</p>`;
            }
        }
        
        html += '</div>';
        resultEl.innerHTML = html;
    } catch (error) {
        showError(resultEl, error);
    }
}

async function querySheetsData() {
    const resultEl = document.getElementById('queryResult');
    const filterText = document.getElementById('dataFilter').value;
    showLoading(resultEl);

    try {
        const filter = JSON.parse(filterText);
        
        const response = await fetch(`${API_BASE_URL}/api/data/sheets/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(filter)
        });
        const data = await response.json();
        
        let html = '<div class="mt-4 p-4 bg-slate-50 rounded-lg">';
        html += '<pre class="text-xs overflow-x-auto">' + JSON.stringify(data, null, 2) + '</pre>';
        html += '</div>';
        resultEl.innerHTML = html;
    } catch (error) {
        showError(resultEl, error);
    }
}

// AI & RAG Functions
async function getRAGStats() {
    const resultEl = document.getElementById('ragStats');
    showLoading(resultEl);

    try {
        const response = await fetch(`${API_BASE_URL}/api/ai/rag/stats`);
        const data = await response.json();
        
        let html = '<div class="mt-4 p-4 bg-slate-50 rounded-lg space-y-3">';
        html += '<div class="flex items-center justify-between">';
        html += '<span class="text-sm font-medium text-slate-700">Status</span>';
        html += `<span class="px-3 py-1 rounded-full text-xs font-medium ${data.initialized ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">${data.initialized ? 'Initialized' : 'Not Initialized'}</span>`;
        html += '</div>';
        html += '<div class="flex items-center justify-between">';
        html += '<span class="text-sm font-medium text-slate-700">Documents</span>';
        html += `<span class="text-sm text-slate-600">${data.document_count}</span>`;
        html += '</div>';
        html += '<div class="flex items-center justify-between">';
        html += '<span class="text-sm font-medium text-slate-700">Last Updated</span>';
        html += `<span class="text-sm text-slate-600">${data.last_updated || 'Never'}</span>`;
        html += '</div></div>';
        
        resultEl.innerHTML = html;
    } catch (error) {
        showError(resultEl, error);
    }
}

async function queryRAG() {
    const resultEl = document.getElementById('ragResult');
    const query = document.getElementById('ragQuery').value;
    const k = document.getElementById('ragK').value;
    showLoading(resultEl);

    try {
        const response = await fetch(`${API_BASE_URL}/api/ai/rag/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query, k: parseInt(k) })
        });
        const data = await response.json();
        
        let html = '<div class="mt-4 space-y-4">';
        html += `<div class="p-4 bg-blue-50 border border-blue-200 rounded-lg">`;
        html += `<p class="text-slate-700">${data.answer}</p>`;
        html += `</div>`;
        
        if (data.sources && data.sources.length > 0) {
            html += '<div><h4 class="font-semibold text-slate-900 mb-2">Relevant Sources</h4>';
            data.sources.forEach((source, i) => {
                html += `<div class="p-3 bg-slate-50 rounded-lg mb-2">`;
                html += `<p class="text-xs font-semibold text-slate-700 mb-1">Source ${i + 1}</p>`;
                html += `<pre class="text-xs text-slate-600 whitespace-pre-wrap">${source}</pre>`;
                html += `</div>`;
            });
            html += '</div>';
        }
        
        html += '</div>';
        resultEl.innerHTML = html;
    } catch (error) {
        showError(resultEl, error);
    }
}

async function reindexRAG() {
    const resultEl = document.getElementById('reindexResult');
    showLoading(resultEl);

    try {
        const response = await fetch(`${API_BASE_URL}/api/ai/rag/reindex`, {
            method: 'POST'
        });
        const data = await response.json();
        
        let html = '<div class="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">';
        html += `<p class="text-sm text-green-900"><strong>Status:</strong> ${data.status}</p>`;
        html += `<p class="text-sm text-green-900"><strong>Documents:</strong> ${data.document_count}</p>`;
        html += `<p class="text-sm text-green-900 mt-2">${data.message}</p>`;
        html += '</div>';
        
        resultEl.innerHTML = html;
    } catch (error) {
        showError(resultEl, error);
    }
}

// Utility Functions
function showLoading(element) {
    element.innerHTML = `
        <div class="flex items-center gap-2 text-slate-500">
            <div class="w-4 h-4 border-2 border-slate-300 border-t-blue-600 rounded-full animate-spin"></div>
            <span class="text-sm">Loading...</span>
        </div>
    `;
}

function showError(element, error) {
    element.innerHTML = `
        <div class="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <h4 class="font-semibold text-red-900 mb-1">Error</h4>
            <p class="text-sm text-red-700">${error.message || 'Failed to fetch data'}</p>
            <p class="text-xs text-red-600 mt-2">Make sure the API is running on ${API_BASE_URL}</p>
        </div>
    `;
}
