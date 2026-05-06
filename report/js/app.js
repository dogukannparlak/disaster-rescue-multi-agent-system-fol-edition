/**
 * Disaster Rescue Multi-Agent System — Dashboard Application
 * ===========================================================
 * 
 * This module handles:
 * - Loading simulation data from JSON
 * - Rendering dashboard components
 * - Navigation state management
 */

// ── Configuration ─────────────────────────────────────────────────────────────
const CONFIG = {
  dataPath: null, // resolved at runtime (supports ?json=results/...)
  refreshInterval: null, // Set to milliseconds for auto-refresh, or null to disable
};

function resolveDefaultDataPath() {
  // report/index.html -> ../results/latest.json
  // report/pages/*.html -> ../../results/latest.json
  const inPagesDir = window.location.pathname.includes('/pages/');
  return inPagesDir ? '../../results/latest.json' : '../results/latest.json';
}

function resolveDataPathFromQuery() {
  const params = new URLSearchParams(window.location.search);
  const jsonParam = params.get('json');
  if (!jsonParam) return null;

  // Allow: ?json=results/run_xxx.json
  // Convert to correct relative path from current page.
  if (jsonParam.startsWith('results/')) {
    const inPagesDir = window.location.pathname.includes('/pages/');
    return (inPagesDir ? '../../' : '../') + jsonParam;
  }
  return jsonParam; // advanced users can pass a fully relative path themselves
}

// ── Global State ──────────────────────────────────────────────────────────────
let simulationData = null;

// ── Data Loading ──────────────────────────────────────────────────────────────

/**
 * Fetch simulation data from JSON file.
 * @returns {Promise<Object>} The simulation data
 */
async function loadSimulationData() {
  try {
    if (!CONFIG.dataPath) {
      CONFIG.dataPath = resolveDataPathFromQuery() || resolveDefaultDataPath();
    }
    const response = await fetch(CONFIG.dataPath);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    simulationData = await response.json();
    return simulationData;
  } catch (error) {
    console.error('Failed to load simulation data:', error);
    showError(error.message);
    throw error;
  }
}

/**
 * Display error message in the UI.
 * @param {string} message - Error message to display
 */
function showError(message) {
  const errorCard = document.getElementById('error-card');
  if (errorCard) {
    errorCard.style.display = 'block';
    const errorText = errorCard.querySelector('p');
    if (errorText) {
      errorText.innerHTML = `
        ${message}<br><br>
        Run the simulation first: <code>python main.py</code><br>
        Dashboard expects: <code>results/latest.json</code> (auto-generated)
      `;
    }
  }
}

// ── Utility Functions ─────────────────────────────────────────────────────────

/**
 * Create a priority tag HTML element.
 * @param {string} level - Priority level (high, medium, low)
 * @returns {string} HTML string for the tag
 */
function createPriorityTag(level) {
  const classMap = {
    high: 'tag-high',
    medium: 'tag-medium',
    low: 'tag-low',
  };
  return `<span class="tag ${classMap[level] || 'tag-low'}">${level}</span>`;
}

/**
 * Format a percentage value for display.
 * @param {number} value - Value between 0 and 1
 * @returns {string} Formatted percentage string
 */
function formatPercent(value) {
  return (Math.round((value || 0) * 1000) / 10).toFixed(1) + '%';
}

/**
 * Safely set text content of an element.
 * @param {string} id - Element ID
 * @param {string} text - Text content
 */
function setText(id, text) {
  const element = document.getElementById(id);
  if (element) {
    element.textContent = text;
  }
}

/**
 * Safely set inner HTML of an element.
 * @param {string} id - Element ID
 * @param {string} html - HTML content
 */
function setHTML(id, html) {
  const element = document.getElementById(id);
  if (element) {
    element.innerHTML = html;
  }
}

// ── Dashboard Rendering ───────────────────────────────────────────────────────

/**
 * Render the status bar with simulation info.
 * @param {Object} data - Simulation data
 */
function renderStatusBar(data) {
  setText('mode-value', data.mode || '—');
  setText('backend-value', data.backend || '—');
  setText('task-count', data.tasks?.length || 0);
  setText('robot-count', data.robots?.length || 0);

  // Config values
  const config = data.config || {};
  setText('seed-value', config.seed ?? '—');
  setText('grid-value', config.grid_size ? `${config.grid_size}×${config.grid_size}` : '—');

  // Priority summary
  const counts = { high: 0, medium: 0, low: 0 };
  for (const task of data.tasks || []) {
    counts[task.priority] = (counts[task.priority] || 0) + 1;
  }
  setText('priority-summary', `High: ${counts.high} | Med: ${counts.medium} | Low: ${counts.low}`);
}

/**
 * Render the tasks table.
 * @param {Object} data - Simulation data
 */
function renderTasksTable(data) {
  const tbody = document.querySelector('#tasks-table tbody');
  if (!tbody) return;

  tbody.innerHTML = '';
  for (const task of data.tasks || []) {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${task.id}</strong></td>
      <td>${task.type}</td>
      <td>${createPriorityTag(task.priority)}</td>
      <td>${task.capability}</td>
      <td><code>(${task.x}, ${task.y})</code></td>
    `;
    tbody.appendChild(tr);
  }
}

/**
 * Render the robots table.
 * @param {Object} data - Simulation data
 */
function renderRobotsTable(data) {
  const tbody = document.querySelector('#robots-table tbody');
  if (!tbody) return;

  tbody.innerHTML = '';
  for (const robot of data.robots || []) {
    const speedClass = {
      fast: 'text-accent',
      medium: 'text-warning',
      slow: 'text-danger',
    }[robot.speed] || '';

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${robot.id}</strong></td>
      <td>${robot.name}</td>
      <td>${robot.capability}</td>
      <td class="${speedClass}">${robot.speed}</td>
    `;
    tbody.appendChild(tr);
  }
}

/**
 * Render the assignments table.
 * @param {Object} data - Simulation data
 */
function renderAssignmentsTable(data) {
  const tbody = document.querySelector('#assignments-table tbody');
  if (!tbody) return;

  const taskMap = Object.fromEntries((data.tasks || []).map(t => [t.id, t]));
  const robotMap = Object.fromEntries((data.robots || []).map(r => [r.id, r]));

  tbody.innerHTML = '';
  for (const assignment of data.assignments || []) {
    const task = taskMap[assignment.task_id];
    const robot = robotMap[assignment.robot_id];
    if (!task) continue;

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${task.id}</strong></td>
      <td>${task.type}</td>
      <td>${createPriorityTag(task.priority)}</td>
      <td>${robot ? robot.name : '<span class="text-danger">UNASSIGNED</span>'}</td>
      <td><code>(${task.x}, ${task.y})</code></td>
    `;
    tbody.appendChild(tr);
  }
}

/**
 * Render a single metric with animation.
 * @param {string} key - Metric key (cap, prio, balance, comp)
 * @param {number} value - Metric value (0-1)
 */
function renderMetric(key, value) {
  const percent = formatPercent(value);
  setText(`m-${key}`, percent);

  // Animate the progress bar
  requestAnimationFrame(() => {
    const bar = document.getElementById(`bar-${key}`);
    if (bar) {
      const width = Math.min(100, (value || 0) * 100);
      bar.style.width = `${width}%`;
    }
  });
}

/**
 * Render all metrics.
 * @param {Object} data - Simulation data
 */
function renderMetrics(data) {
  const metrics = data.metrics || {};
  renderMetric('cap', metrics.capability_match_rate);
  renderMetric('prio', metrics.priority_order_score);
  renderMetric('balance', metrics.task_distribution_balance);
  renderMetric('comp', metrics.completion_rate);
  setText('m-unassigned', metrics.unassigned_count ?? 0);
  renderCostMetrics(data);
}

/**
 * Format PDF cost ratio: Efficiency = Actual Cost / Optimal Cost (1.0 = optimal).
 * @param {number|null|undefined} eff
 * @returns {string}
 */
function formatCostEfficiencyRatio(eff) {
  if (eff === null || eff === undefined || !Number.isFinite(eff)) return 'n/a';
  return eff.toFixed(4) + ' (1.0 = optimal)';
}

/**
 * Bar width: 100% at optimal (1.0); lower fill when ratio > 1 (worse cost).
 * @param {number|null|undefined} eff
 * @returns {number}
 */
function costEfficiencyBarPercent(eff) {
  if (eff === null || eff === undefined || !Number.isFinite(eff) || eff <= 0) return 0;
  return Math.min(100, (1 / eff) * 100);
}

/**
 * Render cost metrics (HW2; CSE419 PDF Actual/Optimal ratio).
 * @param {Object} data - Simulation data
 */
function renderCostMetrics(data) {
  const metrics = data.metrics || {};
  if (metrics.actual_cost === undefined) return;

  const actualCostEl   = document.getElementById('m-actual-cost');
  const optimalCostEl  = document.getElementById('m-optimal-cost');
  const costEffEl      = document.getElementById('m-cost-eff');
  const costEffBarEl   = document.getElementById('bar-cost-eff');

  if (actualCostEl)  actualCostEl.textContent  = (metrics.actual_cost  || 0).toFixed(2);
  if (optimalCostEl) optimalCostEl.textContent = (metrics.optimal_cost || 0).toFixed(2);
  if (costEffEl) {
    const eff = metrics.cost_efficiency;
    costEffEl.textContent = formatCostEfficiencyRatio(eff);
    requestAnimationFrame(() => {
      if (costEffBarEl) costEffBarEl.style.width = costEfficiencyBarPercent(eff) + '%';
    });
  }
}

/**
 * Render per-robot statistics.
 * @param {Object} data - Simulation data
 */
function renderRobotStats(data) {
  const container = document.getElementById('robot-stats');
  if (!container) return;

  const robotMap = Object.fromEntries((data.robots || []).map(r => [r.id, r]));
  const taskCounts = {};

  // Count tasks per robot
  for (const assignment of data.assignments || []) {
    const robotId = assignment.robot_id;
    taskCounts[robotId] = (taskCounts[robotId] || 0) + 1;
  }

  let html = '';
  for (const robot of data.robots || []) {
    const count = taskCounts[robot.id] || 0;
    html += `
      <div class="info-card">
        <h3>${robot.name}</h3>
        <p>
          <strong>ID:</strong> ${robot.id}<br>
          <strong>Capability:</strong> ${robot.capability}<br>
          <strong>Speed:</strong> ${robot.speed}<br>
          <strong>Assigned Tasks:</strong> ${count}
        </p>
      </div>
    `;
  }
  container.innerHTML = html;
}

// ── Main Dashboard Render ─────────────────────────────────────────────────────

/**
 * Render the complete dashboard.
 * @param {Object} data - Simulation data
 */
function renderDashboard(data) {
  renderStatusBar(data);
  renderTasksTable(data);
  renderRobotsTable(data);
  renderAssignmentsTable(data);
  renderMetrics(data);
  renderRobotStats(data);
}

// ── Page-Specific Renderers ───────────────────────────────────────────────────

/**
 * Render the architecture page content.
 */
function renderArchitecturePage() {
  // Architecture page is mostly static HTML
  // This function can add dynamic elements if needed
}

/**
 * Render the guide page content.
 */
function renderGuidePage() {
  // Guide page is static HTML
}

// ── Navigation ────────────────────────────────────────────────────────────────

/**
 * Set active navigation link based on current page.
 */
function setActiveNavLink() {
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  const navLinks = document.querySelectorAll('.nav-link');

  navLinks.forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPage || (currentPage === '' && href === 'index.html')) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });
}

// ── Initialization ────────────────────────────────────────────────────────────

/**
 * Initialize the dashboard application.
 */
async function initDashboard() {
  setActiveNavLink();

  try {
    const data = await loadSimulationData();
    renderDashboard(data);
  } catch (error) {
    // Error already handled in loadSimulationData
  }
}

/**
 * Initialize a page that only needs basic data.
 */
async function initPage() {
  setActiveNavLink();

  try {
    await loadSimulationData();
    renderStatusBar(simulationData);
  } catch (error) {
    // Error already handled in loadSimulationData
  }
}

// ── Export for use in HTML ────────────────────────────────────────────────────
window.Dashboard = {
  init: initDashboard,
  initPage: initPage,
  loadData: loadSimulationData,
  getData: () => simulationData,
  render: renderDashboard,
  renderStatusBar,
  renderTasksTable,
  renderRobotsTable,
  renderAssignmentsTable,
  renderMetrics,
  renderCostMetrics,
  renderRobotStats,
};
