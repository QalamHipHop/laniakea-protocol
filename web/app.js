/**
 * Laniakea Protocol - Frontend Application
 * رابط کاربری پروتوکل لانیاکیا
 */

// ========== CONFIGURATION ==========
const API_BASE_URL = 'http://localhost:8000';
const REFRESH_INTERVAL = 5000; // 5 seconds

// ========== STATE MANAGEMENT ==========
let appState = {
    currentSection: 'dashboard',
    nodeInfo: null,
    systemStats: null,
    tasks: [],
    solutions: [],
    blockchain: null
};

// ========== INITIALIZATION ==========
document.addEventListener('DOMContentLoaded', () => {
    console.log('🌌 Laniakea Protocol Frontend Initialized');
    
    // Setup navigation
    setupNavigation();
    
    // Initial data fetch
    refreshAllData();
    
    // Setup auto-refresh
    setInterval(refreshAllData, REFRESH_INTERVAL);
    
    // Setup form handlers
    setupFormHandlers();
    
    // Setup modal handlers
    setupModalHandlers();
});

// ========== NAVIGATION ==========
function setupNavigation() {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const sectionId = link.getAttribute('href').substring(1);
            switchSection(sectionId);
        });
    });
}

function switchSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Show selected section
    document.getElementById(sectionId).classList.add('active');
    
    // Update nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === '#' + sectionId) {
            link.classList.add('active');
        }
    });
    
    appState.currentSection = sectionId;
}

// ========== API CALLS ==========
async function fetchNodeInfo() {
    try {
        const response = await axios.get(`${API_BASE_URL}/`);
        appState.nodeInfo = response.data;
        updateNodeInfoDisplay();
    } catch (error) {
        console.error('Error fetching node info:', error);
        showAlert('خطا در دریافت اطلاعات نود', 'error');
    }
}

async function fetchSystemStats() {
    try {
        const response = await axios.get(`${API_BASE_URL}/stats`);
        appState.systemStats = response.data;
        updateSystemStatsDisplay();
    } catch (error) {
        console.error('Error fetching stats:', error);
    }
}

async function fetchTasks() {
    try {
        const response = await axios.get(`${API_BASE_URL}/tasks`);
        appState.tasks = response.data.tasks || [];
        updateTasksDisplay();
    } catch (error) {
        console.error('Error fetching tasks:', error);
    }
}

async function fetchSolutions() {
    try {
        const response = await axios.get(`${API_BASE_URL}/solutions`);
        appState.solutions = response.data.solutions || [];
        updateSolutionsDisplay();
    } catch (error) {
        console.error('Error fetching solutions:', error);
    }
}

async function fetchBlockchain() {
    try {
        const response = await axios.get(`${API_BASE_URL}/blockchain`);
        appState.blockchain = response.data;
        updateBlockchainDisplay();
    } catch (error) {
        console.error('Error fetching blockchain:', error);
    }
}

// ========== DISPLAY UPDATES ==========
function updateNodeInfoDisplay() {
    if (!appState.nodeInfo) return;
    
    const html = `
        <div class="stat-item">
            <span class="stat-label">شناسه نود:</span>
            <span class="stat-value">${appState.nodeInfo.node_id?.substring(0, 12)}...</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">هاست:</span>
            <span class="stat-value">${appState.nodeInfo.host}:${appState.nodeInfo.api_port}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">اعتبار:</span>
            <span class="stat-value">${(appState.nodeInfo.reputation || 0).toFixed(2)}</span>
        </div>
    `;
    
    const nodeInfoEl = document.getElementById('node-info');
    if (nodeInfoEl) nodeInfoEl.innerHTML = html;
}

function updateSystemStatsDisplay() {
    if (!appState.systemStats) return;
    
    const stats = appState.systemStats;
    
    document.getElementById('task-count').textContent = stats.task_pool_size || 0;
    document.getElementById('solution-count').textContent = stats.solution_pool_size || 0;
    document.getElementById('blockchain-length').textContent = stats.blockchain?.length || 0;
    
    const totalValue = stats.blockchain?.total_value_created?.total_value || 0;
    document.getElementById('total-value').textContent = totalValue.toFixed(2);
    
    // Update modernity index
    const modernity = stats.hash_modernity?.modernity_index || 0;
    const modernityPercent = Math.min(100, (modernity / 10) * 100);
    document.getElementById('modernity-progress').style.width = modernityPercent + '%';
    document.getElementById('modernity-text').textContent = modernity.toFixed(2);
    
    // Update consciousness level
    const consciousness = stats.cognitive_core?.consciousness_level || 0;
    const consciousnessPercent = Math.min(100, consciousness * 100);
    document.getElementById('consciousness-progress').style.width = consciousnessPercent + '%';
    document.getElementById('consciousness-text').textContent = consciousness.toFixed(2);
    
    // Update value vector chart
    updateValueVectorChart(stats.blockchain?.total_value_created);
}

function updateValueVectorChart(valueVector) {
    if (!valueVector) return;
    
    const ctx = document.getElementById('valueVectorChart');
    if (!ctx) return;
    
    const data = {
        labels: ['دانش', 'محاسبات', 'خلاقیت', 'آگاهی', 'محیطی', 'سلامتی', 'گسترش', 'اخلاقی'],
        datasets: [{
            label: 'بردار ارزش',
            data: [
                valueVector.knowledge || 0,
                valueVector.computation || 0,
                valueVector.originality || 0,
                valueVector.consciousness || 0,
                valueVector.environmental || 0,
                valueVector.health || 0,
                valueVector.scalability || 0,
                valueVector.ethical_alignment || 0
            ],
            borderColor: '#667eea',
            backgroundColor: 'rgba(102, 126, 234, 0.1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4
        }]
    };
    
    // Destroy existing chart if it exists
    if (window.valueVectorChart) {
        window.valueVectorChart.destroy();
    }
    
    window.valueVectorChart = new Chart(ctx, {
        type: 'radar',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    labels: { color: '#fff' }
                }
            },
            scales: {
                r: {
                    ticks: { color: 'rgba(255, 255, 255, 0.7)' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                }
            }
        }
    });
}

function updateTasksDisplay() {
    const container = document.getElementById('tasks-list');
    if (!container) return;
    
    if (appState.tasks.length === 0) {
        container.innerHTML = '<p class="loading">هیچ تسکی یافت نشد</p>';
        return;
    }
    
    const html = appState.tasks.map(task => `
        <div class="card">
            <h4>${task.title}</h4>
            <p>${task.description}</p>
            <div class="stat-item">
                <span class="stat-label">دسته‌بندی:</span>
                <span class="stat-value">${task.category}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">سطح دشواری:</span>
                <span class="stat-value">${task.difficulty.toFixed(1)}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">شناسه:</span>
                <span class="stat-value">${task.id.substring(0, 12)}...</span>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

function updateSolutionsDisplay() {
    const container = document.getElementById('solutions-list');
    if (!container) return;
    
    if (appState.solutions.length === 0) {
        container.innerHTML = '<p class="loading">هیچ راه‌حلی یافت نشد</p>';
        return;
    }
    
    const html = appState.solutions.map(solution => `
        <div class="card">
            <h4>راه‌حل برای تسک: ${solution.task_id.substring(0, 12)}...</h4>
            <p>${solution.content}</p>
            <div class="stat-item">
                <span class="stat-label">ارزش کل:</span>
                <span class="stat-value">${solution.value_vector?.total_value?.toFixed(2) || 0}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">شناسه:</span>
                <span class="stat-value">${solution.id.substring(0, 12)}...</span>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

function updateBlockchainDisplay() {
    const container = document.getElementById('blockchain-info');
    if (!container) return;
    
    if (!appState.blockchain) {
        container.innerHTML = '<p class="loading">اطلاعات بلاک‌چین در دسترس نیست</p>';
        return;
    }
    
    const html = `
        <div class="card">
            <h3>📊 اطلاعات بلاک‌چین</h3>
            <div class="stat-item">
                <span class="stat-label">طول زنجیره:</span>
                <span class="stat-value">${appState.blockchain.length}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">آخرین بلاک:</span>
                <span class="stat-value">${appState.blockchain.last_block_index}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">تعداد تراکنش‌ها:</span>
                <span class="stat-value">${appState.blockchain.stats?.total_transactions || 0}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">تعداد راه‌حل‌ها:</span>
                <span class="stat-value">${appState.blockchain.stats?.total_solutions || 0}</span>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

// ========== FORM HANDLERS ==========
function setupFormHandlers() {
    // Create Task Form
    const createTaskForm = document.getElementById('createTaskForm');
    if (createTaskForm) {
        createTaskForm.addEventListener('submit', submitTask);
    }
    
    // Submit Solution Form
    const submitSolutionForm = document.getElementById('submitSolutionForm');
    if (submitSolutionForm) {
        submitSolutionForm.addEventListener('submit', submitSolution);
    }
}

async function submitTask(event) {
    event.preventDefault();
    
    const taskData = {
        title: document.getElementById('taskTitle').value,
        description: document.getElementById('taskDescription').value,
        category: document.getElementById('taskCategory').value,
        difficulty: parseFloat(document.getElementById('taskDifficulty').value)
    };
    
    try {
        const response = await axios.post(`${API_BASE_URL}/tasks/create`, taskData);
        showAlert('تسک با موفقیت ایجاد شد', 'success');
        event.target.reset();
        refreshTasks();
    } catch (error) {
        console.error('Error creating task:', error);
        showAlert('خطا در ایجاد تسک', 'error');
    }
}

async function submitSolution(event) {
    event.preventDefault();
    
    const solutionData = {
        task_id: document.getElementById('solutionTaskId').value,
        content: document.getElementById('solutionContent').value,
        value_vector: {
            knowledge: parseFloat(document.getElementById('solutionKnowledge').value),
            computation: parseFloat(document.getElementById('solutionComputation').value),
            originality: parseFloat(document.getElementById('solutionOriginality').value)
        }
    };
    
    try {
        const response = await axios.post(`${API_BASE_URL}/solutions/submit`, solutionData);
        showAlert('راه‌حل با موفقیت ارسال شد', 'success');
        event.target.reset();
        refreshSolutions();
    } catch (error) {
        console.error('Error submitting solution:', error);
        showAlert('خطا در ارسال راه‌حل', 'error');
    }
}

// ========== MODAL HANDLERS ==========
function setupModalHandlers() {
    // Close modals when clicking outside
    window.addEventListener('click', (event) => {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            if (event.target === modal) {
                modal.classList.remove('show');
            }
        });
    });
}

function openCreateTaskModal() {
    document.getElementById('createTaskModal').classList.add('show');
}

function closeCreateTaskModal() {
    document.getElementById('createTaskModal').classList.remove('show');
}

function openSubmitSolutionModal() {
    document.getElementById('submitSolutionModal').classList.add('show');
    
    // Populate task dropdown
    const taskSelect = document.getElementById('solutionTaskId');
    taskSelect.innerHTML = '<option value="">تسک را انتخاب کنید</option>';
    appState.tasks.forEach(task => {
        const option = document.createElement('option');
        option.value = task.id;
        option.textContent = task.title;
        taskSelect.appendChild(option);
    });
}

function closeSubmitSolutionModal() {
    document.getElementById('submitSolutionModal').classList.remove('show');
}

// ========== UTILITY FUNCTIONS ==========
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    document.body.insertBefore(alertDiv, document.body.firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function refreshTasks() {
    fetchTasks();
}

function refreshSolutions() {
    fetchSolutions();
}

function refreshBlockchain() {
    fetchBlockchain();
}

function refreshAllData() {
    fetchNodeInfo();
    fetchSystemStats();
    fetchTasks();
    fetchSolutions();
    fetchBlockchain();
}

// ========== EXPORT FOR GLOBAL USE ==========
window.openCreateTaskModal = openCreateTaskModal;
window.closeCreateTaskModal = closeCreateTaskModal;
window.openSubmitSolutionModal = openSubmitSolutionModal;
window.closeSubmitSolutionModal = closeSubmitSolutionModal;
window.submitTask = submitTask;
window.submitSolution = submitSolution;
window.refreshTasks = refreshTasks;
window.refreshSolutions = refreshSolutions;
window.refreshBlockchain = refreshBlockchain;
