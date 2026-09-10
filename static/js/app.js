/**
 * PYDAH SkillPath - Frontend Application Controller
 * Features: Checkpoints, Interview Flashcards, Leaderboard, Placement Filters & ATS Resume
 */

// Department Course Specializations Mapping
const DEPARTMENT_COURSES = {
    "Computer Science & Engineering": [
        { id: 1, code: "FSD", title: "Full Stack Web & Cloud Architect", recommended: true, role: "Full Stack Cloud Engineer" },
        { id: 2, code: "AIML", title: "Artificial Intelligence & Generative AI", recommended: true, role: "AI / ML Engineer" },
        { id: 3, code: "DEVOPS", title: "Cloud Native, DevOps & Site Reliability", recommended: true, role: "Cloud DevOps Architect" },
        { id: 4, code: "CYBER", title: "Cybersecurity & Ethical Penetration Testing", recommended: false, role: "Cybersecurity Analyst" },
        { id: 5, code: "APP", title: "Mobile App Development (Flutter & React Native)", recommended: false, role: "Mobile Application Engineer" }
    ],
    "Artificial Intelligence & Data Science": [
        { id: 2, code: "AIML", title: "Artificial Intelligence & Generative AI", recommended: true, role: "AI Research & RAG Specialist" },
        { id: 1, code: "FSD", title: "Full Stack Web & Cloud Architect", recommended: false, role: "Full Stack AI Developer" },
        { id: 3, code: "DEVOPS", title: "Cloud Native, DevOps & MLOps", recommended: false, role: "MLOps Engineer" },
        { id: 5, code: "APP", title: "Mobile App Development", recommended: false, role: "AI Mobile App Engineer" }
    ],
    "Electronics & Communication": [
        { id: 11, code: "EMBEDDED", title: "Embedded Systems, IoT & Robotics", recommended: true, role: "Embedded Firmware & IoT Engineer" },
        { id: 12, code: "VLSI", title: "VLSI Design & Digital Verification", recommended: true, role: "VLSI Verification Engineer" },
        { id: 4, code: "CYBER", title: "Cybersecurity & Hardware Security", recommended: false, role: "Hardware Security Specialist" },
        { id: 2, code: "AIML", title: "Artificial Intelligence & Edge AI", recommended: false, role: "Edge AI / Embedded ML Engineer" },
        { id: 1, code: "FSD", title: "Full Stack Web & Cloud Architect", recommended: false, role: "Full Stack Software Engineer" }
    ],
    "Electrical & Electronics": [
        { id: 13, code: "EV_SMARTGRID", title: "Electric Vehicles (EV) & Smart Automation", recommended: true, role: "EV Powertrain & BMS Engineer" },
        { id: 11, code: "EMBEDDED", title: "Embedded Systems, IoT & Robotics", recommended: true, role: "IoT & Industrial Automation Engineer" },
        { id: 3, code: "DEVOPS", title: "Cloud Native, DevOps & Industrial Infra", recommended: false, role: "Industrial Systems Engineer" },
        { id: 1, code: "FSD", title: "Full Stack Web & Cloud Architect", recommended: false, role: "Software Engineer" }
    ],
    "Information Technology": [
        { id: 1, code: "FSD", title: "Full Stack Web & Cloud Architect", recommended: true, role: "Full Stack Web Architect" },
        { id: 3, code: "DEVOPS", title: "Cloud Native, DevOps & Site Reliability", recommended: true, role: "DevOps / SRE Engineer" },
        { id: 4, code: "CYBER", title: "Cybersecurity & Ethical Penetration Testing", recommended: true, role: "Security Operations Analyst" },
        { id: 5, code: "APP", title: "Mobile App Development (Flutter & React Native)", recommended: false, role: "Mobile Application Developer" },
        { id: 2, code: "AIML", title: "Artificial Intelligence & Generative AI", recommended: false, role: "Data Science Engineer" }
    ],
    "Mechanical Engineering": [
        { id: 11, code: "EMBEDDED", title: "Embedded Systems, IoT & Robotics", recommended: true, role: "Robotics & Automation Engineer" },
        { id: 13, code: "EV_SMARTGRID", title: "Electric Vehicles (EV) & Smart Automation", recommended: true, role: "EV Powertrain Design Engineer" }
    ]
};

// Application State
const state = {
    user: null,
    activeTab: 'dashboard',
    tracks: [],
    selectedTrackId: 1,
    selectedQuizTrackId: 1,
    selectedFlashcardTrack: 'FSD',
    deptOnlyRoadmaps: true,
    placementFilter: {
        category: 'All',
        location: 'All',
        searchQuery: ''
    },
    quizState: {
        questions: [],
        answers: {},
        submitted: false,
        result: null
    }
};

// Initialize Application on DOM Ready
document.addEventListener('DOMContentLoaded', async () => {
    lucide.createIcons();
    onDepartmentChanged();
    await checkAuthStatus();
});

// -----------------------------------------------------------------------------
// TOAST NOTIFICATIONS
// -----------------------------------------------------------------------------
function notify(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let iconName = 'info';
    if (type === 'success') iconName = 'check-circle-2';
    if (type === 'error') iconName = 'alert-triangle';

    toast.innerHTML = `
        <i data-lucide="${iconName}"></i>
        <span>${message}</span>
    `;
    container.appendChild(toast);
    lucide.createIcons({ targets: [toast] });

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(40px)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// -----------------------------------------------------------------------------
// AUTHENTICATION & DIRECT PASSWORD RESET
// -----------------------------------------------------------------------------
async function checkAuthStatus() {
    try {
        const res = await fetch('/api/me');
        if (res.ok) {
            const data = await res.json();
            if (data.authenticated && data.user) {
                state.user = data.user;
                renderAppShell();
                return;
            }
        }
    } catch (err) {
        console.error('Session check failed:', err);
    }
    showAuthGateway();
}

function showAuthGateway() {
    document.getElementById('auth-section').classList.remove('hidden');
    document.getElementById('app-section').classList.add('hidden');
    lucide.createIcons();
}

function switchAuthTab(tab) {
    const btnLogin = document.getElementById('tab-btn-login');
    const btnReg = document.getElementById('tab-btn-register');
    const btnReset = document.getElementById('tab-btn-reset');
    
    const formLogin = document.getElementById('login-form');
    const formReg = document.getElementById('register-form');
    const formReset = document.getElementById('reset-form');
    const quickDemoBox = document.getElementById('quick-demo-wrapper');

    [btnLogin, btnReg, btnReset].forEach(b => b && b.classList.remove('active'));
    [formLogin, formReg, formReset].forEach(f => f && f.classList.add('hidden'));

    if (tab === 'login') {
        btnLogin.classList.add('active');
        formLogin.classList.remove('hidden');
        if (quickDemoBox) quickDemoBox.classList.remove('hidden');
    } else if (tab === 'register') {
        btnReg.classList.add('active');
        formReg.classList.remove('hidden');
        if (quickDemoBox) quickDemoBox.classList.add('hidden');
        onDepartmentChanged();
    } else if (tab === 'reset') {
        btnReset.classList.add('active');
        formReset.classList.remove('hidden');
        if (quickDemoBox) quickDemoBox.classList.add('hidden');
    }
    lucide.createIcons();
}

function onDepartmentChanged() {
    const deptSelect = document.getElementById('reg-dept');
    const courseSelect = document.getElementById('reg-course');
    const badgeEl = document.getElementById('reg-dept-badge');
    const hintEl = document.getElementById('reg-course-hint');
    if (!deptSelect || !courseSelect) return;

    const dept = deptSelect.value;
    const courses = DEPARTMENT_COURSES[dept] || DEPARTMENT_COURSES["Computer Science & Engineering"];
    
    let html = '';
    courses.forEach((c, idx) => {
        const star = c.recommended ? '⭐ ' : '';
        const recLabel = c.recommended ? ' [Recommended]' : '';
        html += `<option value="${c.id}" data-role="${c.role}" ${idx === 0 ? 'selected' : ''}>${star}${c.title}${recLabel}</option>`;
    });
    courseSelect.innerHTML = html;

    // Short department code for the badge
    let deptCode = 'Your Dept';
    if (dept.includes('Computer Science')) deptCode = 'CSE';
    else if (dept.includes('Artificial')) deptCode = 'AI & DS';
    else if (dept.includes('Communication')) deptCode = 'ECE';
    else if (dept.includes('Electrical')) deptCode = 'EEE';
    else if (dept.includes('Information')) deptCode = 'IT';
    else if (dept.includes('Mechanical')) deptCode = 'MECH';

    if (badgeEl) badgeEl.textContent = `⭐ ${deptCode} Specializations`;
    if (hintEl) hintEl.textContent = `⚡ Showing ${courses.length} courses tailored for ${deptCode} curriculum & core recruiters`;

    onCourseChanged();
}

function onCourseChanged() {
    const courseSelect = document.getElementById('reg-course');
    const targetInput = document.getElementById('reg-target');
    if (!courseSelect || !targetInput) return;

    const selectedOption = courseSelect.options[courseSelect.selectedIndex];
    if (selectedOption && selectedOption.dataset.role) {
        targetInput.value = selectedOption.dataset.role;
    }
}

function quickFillDemo(role) {
    switchAuthTab('login');
    const emailInput = document.getElementById('login-email');
    const passInput = document.getElementById('login-password');

    if (role === 'student') {
        emailInput.value = 'student@pydah.edu.in';
        passInput.value = 'pydah123';
        notify('Loaded Demo Student: Venkata Sai Teja', 'info');
    } else if (role === 'admin') {
        emailInput.value = 'admin@pydah.edu.in';
        passInput.value = 'pydah123';
        notify('Loaded Demo Administrator: Dean Office', 'info');
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;
    const btnSubmit = document.getElementById('btn-login-submit');

    btnSubmit.disabled = true;
    btnSubmit.innerHTML = `<span>Signing In...</span>`;

    try {
        const res = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await res.json();

        if (res.ok && data.success) {
            state.user = data.user;
            notify(data.message || 'Login successful!', 'success');
            renderAppShell();
        } else {
            notify(data.message || 'Invalid email or password.', 'error');
        }
    } catch (err) {
        notify('Connection error. Please try again.', 'error');
    } finally {
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = `<span>Access SkillPath Portal</span><i data-lucide="arrow-right"></i>`;
        lucide.createIcons();
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const name = document.getElementById('reg-name').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const password = document.getElementById('reg-password').value;
    const department = document.getElementById('reg-dept').value;
    const year_or_designation = document.getElementById('reg-year').value;
    const target_role = document.getElementById('reg-target').value.trim();
    const regCourse = document.getElementById('reg-course');
    const preferred_track_id = regCourse ? parseInt(regCourse.value) : null;
    const btnSubmit = document.getElementById('btn-reg-submit');

    btnSubmit.disabled = true;
    btnSubmit.innerHTML = `<span>Creating Profile...</span>`;

    try {
        const res = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password, department, year_or_designation, target_role, preferred_track_id })
        });
        const data = await res.json();

        if (res.ok && data.success) {
            state.user = data.user;
            notify('Student account registered successfully!', 'success');
            renderAppShell();
        } else {
            notify(data.message || 'Registration failed.', 'error');
        }
    } catch (err) {
        notify('Network error during registration.', 'error');
    } finally {
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = `<span>Create Student Profile</span><i data-lucide="check-circle"></i>`;
        lucide.createIcons();
    }
}

async function handlePasswordReset(e) {
    e.preventDefault();
    const email = document.getElementById('reset-email').value.trim();
    const newPassword = document.getElementById('reset-new-password').value;
    const confirmPassword = document.getElementById('reset-confirm-password').value;
    const btnReset = document.getElementById('btn-reset-submit');

    if (newPassword !== confirmPassword) {
        notify('Passwords do not match. Please re-enter carefully.', 'error');
        return;
    }

    if (newPassword.length < 6) {
        notify('Password must be at least 6 characters long.', 'error');
        return;
    }

    btnReset.disabled = true;
    btnReset.innerHTML = `<span>Updating Password in Database...</span>`;

    try {
        const res = await fetch('/api/forgot-password/reset', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, new_password: newPassword })
        });
        const data = await res.json();

        if (res.ok && data.success) {
            notify(data.message || 'Password reset successfully!', 'success');
            document.getElementById('login-email').value = email;
            document.getElementById('login-password').value = newPassword;
            document.getElementById('reset-form').reset();
            switchAuthTab('login');
        } else {
            notify(data.message || 'Password reset failed.', 'error');
        }
    } catch (err) {
        notify('Network error resetting password.', 'error');
    } finally {
        btnReset.disabled = false;
        btnReset.innerHTML = `<span>Update & Reset Password</span><i data-lucide="refresh-cw"></i>`;
        lucide.createIcons();
    }
}

async function handleLogout() {
    try {
        await fetch('/api/logout', { method: 'POST' });
        state.user = null;
        notify('Logged out successfully.', 'info');
        showAuthGateway();
    } catch (err) {
        console.error('Logout error:', err);
    }
}

// -----------------------------------------------------------------------------
// APP SHELL & TAB SWITCHING
// -----------------------------------------------------------------------------
async function renderAppShell() {
    document.getElementById('auth-section').classList.add('hidden');
    document.getElementById('app-section').classList.remove('hidden');

    const initials = state.user.name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
    document.getElementById('nav-avatar').textContent = initials;
    document.getElementById('nav-user-name').textContent = state.user.name;
    document.getElementById('nav-user-role').textContent = `${state.user.role.toUpperCase()} • ${state.user.department}`;

    // Set initial track selection based on user's department preference
    if (state.user && state.user.preferred_track_id) {
        state.selectedTrackId = state.user.preferred_track_id;
        state.selectedQuizTrackId = state.user.preferred_track_id;
    }

    await switchAppTab('dashboard');
    lucide.createIcons();
}

async function switchAppTab(tabName) {
    state.activeTab = tabName;

    document.querySelectorAll('.nav-link-btn').forEach(btn => {
        if (btn.dataset.tab === tabName) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    document.querySelectorAll('.tab-content').forEach(tc => {
        tc.classList.remove('active');
    });

    const activeContent = document.getElementById(`tab-${tabName}`);
    if (activeContent) activeContent.classList.add('active');

    if (tabName === 'dashboard') {
        await loadDashboard();
    } else if (tabName === 'roadmaps') {
        await loadRoadmaps();
    } else if (tabName === 'interview') {
        await loadInterviewPrep();
    } else if (tabName === 'quizzes') {
        await loadQuizArena();
    } else if (tabName === 'projects') {
        await loadProjects();
    } else if (tabName === 'placements') {
        await loadPlacements();
    } else if (tabName === 'leaderboard') {
        await loadLeaderboard();
    } else if (tabName === 'passport') {
        await loadSkillPassport();
    } else if (tabName === 'portfolio') {
        await loadPortfolioEditor();
    }

    lucide.createIcons();
}

// -----------------------------------------------------------------------------
// TAB 1: DASHBOARD
// -----------------------------------------------------------------------------
async function loadDashboard() {
    try {
        const [statsRes, tracksRes, placementsRes] = await Promise.all([
            fetch('/api/stats/dashboard'),
            fetch('/api/tracks'),
            fetch('/api/placements')
        ]);

        if (statsRes.ok) {
            const data = await statsRes.json();
            const s = data.stats;

            document.getElementById('dash-user-name').textContent = state.user.name;
            document.getElementById('dash-completed-modules').textContent = s.completed_modules;
            document.getElementById('dash-quizzes-passed').textContent = s.quizzes_passed;
            document.getElementById('dash-projects-count').textContent = s.projects_count;
            document.getElementById('dash-karma-points').textContent = s.karma_points;
            document.getElementById('nav-streak-count').textContent = `${s.streak_days} Days`;

            const readinessPct = s.career_readiness;
            document.getElementById('dash-readiness-val').textContent = `${readinessPct}%`;
            
            const circle = document.getElementById('dash-readiness-circle');
            const circumference = 54 * 2 * Math.PI;
            const offset = circumference - (readinessPct / 100) * circumference;
            circle.style.strokeDashoffset = offset;

            if (s.active_track) {
                document.getElementById('dash-track-title').textContent = s.active_track.title;
            }
        }

        if (tracksRes.ok) {
            const tData = await tracksRes.json();
            state.tracks = tData.tracks;
            renderDashboardTrackPreview(tData.tracks);
        }

        if (placementsRes.ok) {
            const pData = await placementsRes.json();
            renderDashboardPlacementsSpotlight(pData.placements);
        }

    } catch (err) {
        console.error('Dashboard load error:', err);
    }
}

function renderDashboardTrackPreview(tracks) {
    const box = document.getElementById('dash-track-preview-box');
    if (!tracks || tracks.length === 0) return;

    const t = tracks[0];
    box.innerHTML = `
        <div class="track-preview-card">
            <div class="track-preview-top">
                <div class="track-preview-info">
                    <h4>${t.title}</h4>
                    <p>${t.tagline}</p>
                </div>
                <span class="badge-tag">${t.category}</span>
            </div>

            <div class="prog-text-row" style="margin-top: 14px;">
                <span style="font-size: 0.85rem; color: var(--text-muted);">Curriculum Completion</span>
                <strong style="color: var(--pydah-orange-bright);">${t.progress_percent}%</strong>
            </div>
            <div class="progress-bar-bg">
                <div class="progress-bar-fill" style="width: ${t.progress_percent}%"></div>
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 14px;">
                <span style="font-size: 0.8rem; color: var(--text-dim);">${t.completed_modules} of ${t.total_modules} Modules Mastered</span>
                <button class="btn-primary" style="padding: 6px 14px; font-size: 0.8rem;" onclick="openTrackRoadmap(${t.id})">
                    <span>Explore Roadmap</span>
                    <i data-lucide="arrow-right"></i>
                </button>
            </div>
        </div>
    `;
    lucide.createIcons();
}

function renderDashboardPlacementsSpotlight(placements) {
    const list = document.getElementById('dash-placements-spotlight');
    if (!placements || placements.length === 0) return;

    list.innerHTML = placements.slice(0, 3).map(p => `
        <div class="placement-spotlight-item">
            <div class="spot-company-info">
                <strong>${p.company}</strong>
                <span>${p.role} • ${p.location}</span>
                <div class="spot-match-tag">🎯 ${p.match_percent}% Skills Match</div>
            </div>
            <div style="text-align: right;">
                <div class="spot-package">${p.package_or_stipend}</div>
                <button class="btn-ghost-sm" style="margin-top: 4px;" onclick="switchAppTab('placements')">Details & Apply</button>
            </div>
        </div>
    `).join('');
    lucide.createIcons();
}

// -----------------------------------------------------------------------------
// TAB 2: TECH ROADMAPS WITH GRANULAR CHECKPOINTS
// -----------------------------------------------------------------------------
async function loadRoadmaps() {
    try {
        if (!state.tracks || state.tracks.length === 0) {
            const res = await fetch('/api/tracks');
            const data = await res.json();
            state.tracks = data.tracks;
        }

        // Update department indicator in UI
        if (state.user) {
            const deptTextEl = document.getElementById('roadmap-dept-text');
            if (deptTextEl) {
                deptTextEl.textContent = `Department: ${state.user.department}`;
            }

            // If user has a preferred track and none selected, activate it
            if (!state._roadmapManuallySelected && state.user.preferred_track_id) {
                state.selectedTrackId = state.user.preferred_track_id;
            }
        }

        // Filter tracks based on deptOnlyRoadmaps toggle
        let visibleTracks = state.tracks;
        if (state.deptOnlyRoadmaps && state.user && state.user.department) {
            const recTracks = state.tracks.filter(t => t.is_recommended);
            if (recTracks.length > 0) {
                visibleTracks = recTracks;
            }
        }

        // Update toggle buttons active state
        const btnDeptOnly = document.getElementById('btn-filter-dept-only');
        const btnAllTracks = document.getElementById('btn-filter-all-tracks');
        if (btnDeptOnly) btnDeptOnly.classList.toggle('active', state.deptOnlyRoadmaps);
        if (btnAllTracks) btnAllTracks.classList.toggle('active', !state.deptOnlyRoadmaps);

        // Ensure current selectedTrackId is valid in visibleTracks
        if (!visibleTracks.some(t => t.id === state.selectedTrackId) && visibleTracks.length > 0) {
            state.selectedTrackId = visibleTracks[0].id;
        }

        const chipsContainer = document.getElementById('track-filter-chips');
        chipsContainer.innerHTML = visibleTracks.map(t => `
            <button class="track-chip-btn ${t.id === state.selectedTrackId ? 'active' : ''}" onclick="selectRoadmapTrack(${t.id})">
                <i data-lucide="${t.icon || 'code-2'}"></i>
                <span>${t.code} Roadmap</span>
                ${t.is_recommended ? '<span class="chip-star" title="Recommended for your department">★</span>' : ''}
            </button>
        `).join('');

        await fetchAndRenderTrackDetail(state.selectedTrackId);
        lucide.createIcons();
    } catch (err) {
        console.error('Roadmaps error:', err);
    }
}

function toggleDeptRoadmaps(deptOnly) {
    state.deptOnlyRoadmaps = deptOnly;
    loadRoadmaps();
}

function selectRoadmapTrack(trackId) {
    state._roadmapManuallySelected = true;
    state.selectedTrackId = trackId;
    loadRoadmaps();
}

function openTrackRoadmap(trackId) {
    state._roadmapManuallySelected = true;
    state.selectedTrackId = trackId;
    switchAppTab('roadmaps');
}

async function fetchAndRenderTrackDetail(trackId) {
    try {
        const res = await fetch(`/api/tracks/${trackId}`);
        const data = await res.json();
        if (!data.success) return;

        const t = data.track;
        const modules = data.modules;

        document.getElementById('track-hero-category').textContent = t.category;
        document.getElementById('track-hero-title').textContent = t.title;
        document.getElementById('track-hero-tagline').textContent = t.tagline;
        document.getElementById('track-hero-pct').textContent = `${data.progress_percent}%`;
        document.getElementById('track-hero-prog-fill').style.width = `${data.progress_percent}%`;
        document.getElementById('track-hero-modules-sub').textContent = `${data.completed_modules} of ${data.total_modules} Modules Completed`;

        const nodesWrapper = document.getElementById('roadmap-nodes-wrapper');
        nodesWrapper.innerHTML = modules.map(m => {
            const skills = m.key_skills.split(',').map(s => s.trim());
            const tierClean = m.tier.replace(/[^a-zA-Z0-9]/g, '-');
            const checkpoints = m.checkpoints || [];
            const completedCp = m.completed_checkpoints || [];

            let statusLabel = 'Not Started';
            if (m.status === 'completed') statusLabel = 'Completed';
            else if (m.status === 'in_progress') statusLabel = 'In Progress';

            return `
                <div class="roadmap-node-card status-${m.status}">
                    <div class="node-step-badge">
                        <span class="step-label">Step</span>
                        <span class="step-num">${m.step_number}</span>
                    </div>

                    <div class="node-main-info">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span class="node-tier-pill tier-${tierClean}">${m.tier}</span>
                        </div>
                        <h4 class="node-title">${m.title}</h4>
                        <p class="node-desc">${m.description}</p>
                        
                        <!-- Granular Checkpoints List -->
                        ${checkpoints.length > 0 ? `
                            <div class="checkpoints-container">
                                <div class="checkpoints-title">
                                    <i data-lucide="check-square"></i>
                                    <span>Milestone Checkpoints (${completedCp.length}/${checkpoints.length})</span>
                                </div>
                                <div class="checkpoint-list">
                                    ${checkpoints.map(cp => {
                                        const isChecked = completedCp.includes(cp);
                                        return `
                                            <label class="checkpoint-item ${isChecked ? 'completed' : ''}">
                                                <input type="checkbox" ${isChecked ? 'checked' : ''} onchange="handleToggleCheckpoint(${m.id}, '${cp.replace(/'/g, "\\'")}')">
                                                <span>${cp}</span>
                                            </label>
                                        `;
                                    }).join('')}
                                </div>
                            </div>
                        ` : ''}

                        <div class="node-skills-tags">
                            ${skills.map(s => `<span class="skill-tag">${s}</span>`).join('')}
                        </div>

                        ${m.project_prompt ? `
                            <div style="background: rgba(15, 23, 42, 0.6); padding: 8px 12px; border-radius: 6px; border-left: 3px solid var(--pydah-orange); font-size: 0.8rem; color: #94a3b8; margin-top: 4px;">
                                <strong style="color: #fb923c;">Hands-on Milestone:</strong> ${m.project_prompt}
                            </div>
                        ` : ''}

                        ${m.resources ? `
                            <a href="${m.resources.split(',')[0].trim()}" target="_blank" rel="noopener" class="node-resources-link">
                                <i data-lucide="external-link"></i> Official Documentation & Curated Resources
                            </a>
                        ` : ''}
                    </div>

                    <div class="node-actions">
                        <button class="status-dropdown-btn ${m.status}" onclick="cycleModuleStatus(${m.id}, '${m.status}')" title="Cycle status: Not Started ➜ In Progress ➜ Completed">
                            <i data-lucide="${m.status === 'completed' ? 'check-circle-2' : m.status === 'in_progress' ? 'clock' : 'circle'}"></i>
                            <span>${statusLabel}</span>
                        </button>
                    </div>
                </div>
            `;
        }).join('');

        lucide.createIcons();
    } catch (err) {
        console.error('Fetch track detail error:', err);
    }
}

async function handleToggleCheckpoint(moduleId, checkpointName) {
    try {
        const res = await fetch('/api/progress/checkpoints', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ module_id: moduleId, checkpoint_name: checkpointName })
        });
        const data = await res.json();

        if (res.ok && data.success) {
            notify(`Checkpoint updated! (${data.completed_checkpoints.length}/${data.total_checkpoints})`, 'info');
            await fetchAndRenderTrackDetail(state.selectedTrackId);
        } else {
            notify(data.message || 'Error updating checkpoint.', 'error');
        }
    } catch (err) {
        notify('Network error updating checkpoint.', 'error');
    }
}

async function cycleModuleStatus(moduleId, currentStatus) {
    let newStatus = 'in_progress';
    if (currentStatus === 'in_progress') newStatus = 'completed';
    else if (currentStatus === 'completed') newStatus = 'not_started';

    try {
        const res = await fetch('/api/progress/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ module_id: moduleId, status: newStatus })
        });
        const data = await res.json();

        if (res.ok && data.success) {
            notify(`Status updated to: ${newStatus.replace('_', ' ').toUpperCase()}`, 'success');
            await fetchAndRenderTrackDetail(state.selectedTrackId);
        } else {
            notify(data.message || 'Could not update status.', 'error');
        }
    } catch (err) {
        notify('Network error updating progress.', 'error');
    }
}

// -----------------------------------------------------------------------------
// TAB 3: TECHNICAL INTERVIEW PREPARATION FLASHCARDS
// -----------------------------------------------------------------------------
async function loadInterviewPrep() {
    try {
        if (!state.tracks || state.tracks.length === 0) {
            const res = await fetch('/api/tracks');
            const data = await res.json();
            state.tracks = data.tracks;
        }

        // Default to user's preferred track if not manually changed
        if (state.user && state.user.preferred_track_id && !state._flashcardTrackManuallySelected) {
            const prefTrack = state.tracks.find(t => t.id === state.user.preferred_track_id);
            if (prefTrack) state.selectedFlashcardTrack = prefTrack.code;
        }

        const tabsContainer = document.getElementById('flashcard-track-tabs');
        tabsContainer.innerHTML = state.tracks.map(t => `
            <button class="track-chip-btn ${t.code === state.selectedFlashcardTrack ? 'active' : ''}" onclick="selectFlashcardTrack('${t.code}')">
                <i data-lucide="${t.icon || 'code-2'}"></i>
                <span>${t.code} Q&A</span>
                ${t.is_recommended ? '<span class="chip-star" title="Department Recommendation">★</span>' : ''}
            </button>
        `).join('');

        const res = await fetch(`/api/flashcards/${state.selectedFlashcardTrack}`);
        const data = await res.json();
        const container = document.getElementById('flashcards-deck-container');

        if (!data.success || data.flashcards.length === 0) {
            container.innerHTML = `<p style="color: var(--text-muted);">No flashcards found for this track.</p>`;
            return;
        }

        container.innerHTML = data.flashcards.map(f => `
            <div class="flashcard-card" id="flashcard-${f.id}">
                <div>
                    <div class="flashcard-top">
                        <span class="flashcard-badge diff-${f.difficulty}">${f.difficulty} Level</span>
                        <span class="flashcard-concept"><i data-lucide="tag" style="width: 12px; height: 12px; display: inline;"></i> ${f.key_concept}</span>
                    </div>

                    <h4 class="flashcard-question">Q: ${f.question}</h4>
                </div>

                <div id="flashcard-answer-${f.id}" class="flashcard-answer-box hidden">
                    <strong>Model Answer & Talking Points:</strong>
                    <p style="margin-top: 6px;">${f.answer}</p>
                </div>

                <div style="margin-top: 16px;">
                    <button class="flashcard-reveal-btn" onclick="toggleFlashcardAnswer(${f.id})">
                        <i data-lucide="eye"></i>
                        <span id="btn-text-${f.id}">Reveal Verified Answer</span>
                    </button>
                </div>
            </div>
        `).join('');

        lucide.createIcons();
    } catch (err) {
        console.error('Flashcards error:', err);
    }
}

function selectFlashcardTrack(trackCode) {
    state._flashcardTrackManuallySelected = true;
    state.selectedFlashcardTrack = trackCode;
    loadInterviewPrep();
}

function toggleFlashcardAnswer(id) {
    const el = document.getElementById(`flashcard-answer-${id}`);
    const btnText = document.getElementById(`btn-text-${id}`);
    if (!el) return;

    if (el.classList.contains('hidden')) {
        el.classList.remove('hidden');
        if (btnText) btnText.textContent = 'Hide Answer';
    } else {
        el.classList.add('hidden');
        if (btnText) btnText.textContent = 'Reveal Verified Answer';
    }
    lucide.createIcons();
}

// -----------------------------------------------------------------------------
// TAB 4: QUIZ ARENA
// -----------------------------------------------------------------------------
async function loadQuizArena() {
    try {
        if (!state.tracks || state.tracks.length === 0) {
            const res = await fetch('/api/tracks');
            const data = await res.json();
            state.tracks = data.tracks;
        }

        if (state.user && state.user.preferred_track_id && !state._quizTrackManuallySelected) {
            state.selectedQuizTrackId = state.user.preferred_track_id;
        }

        const tabsContainer = document.getElementById('quiz-track-tabs');
        tabsContainer.innerHTML = state.tracks.map(t => `
            <button class="track-chip-btn ${t.id === state.selectedQuizTrackId ? 'active' : ''}" onclick="selectQuizTrack(${t.id})">
                <i data-lucide="${t.icon || 'code-2'}"></i>
                <span>${t.code} Assessment</span>
                ${t.is_recommended ? '<span class="chip-star" title="Department Recommendation">★</span>' : ''}
            </button>
        `).join('');

        await fetchAndRenderQuiz(state.selectedQuizTrackId);
    } catch (err) {
        console.error('Quiz arena error:', err);
    }
}

function selectQuizTrack(trackId) {
    state._quizTrackManuallySelected = true;
    state.selectedQuizTrackId = trackId;
    loadQuizArena();
}

async function fetchAndRenderQuiz(trackId) {
    const container = document.getElementById('quiz-active-container');
    container.innerHTML = `<p style="color: var(--text-muted);">Loading quiz assessment...</p>`;

    try {
        const res = await fetch(`/api/quizzes/${trackId}`);
        const data = await res.json();

        if (!data.success || !data.quizzes || data.quizzes.length === 0) {
            container.innerHTML = `
                <div class="quiz-intro-card">
                    <div>
                        <h3>Curriculum Quizzes Coming Soon</h3>
                        <p style="color: var(--text-muted); margin-top: 6px;">Questions for this specialization are being compiled by Pydah Innovation Cell.</p>
                    </div>
                </div>
            `;
            return;
        }

        state.quizState = {
            questions: data.quizzes,
            answers: {},
            submitted: false,
            result: null
        };

        renderQuizQuestions();
    } catch (err) {
        console.error('Fetch quiz error:', err);
    }
}

function renderQuizQuestions() {
    const container = document.getElementById('quiz-active-container');
    const { questions, answers, submitted, result } = state.quizState;

    let html = `
        <div class="quiz-intro-card">
            <div>
                <h3>Pydah Specialization Competency Exam</h3>
                <p style="color: var(--text-muted); margin-top: 4px;">Score 70% or higher to earn the <strong>Pydah Certified Specialist Badge</strong> and placement endorsement.</p>
            </div>
            ${submitted && result ? `
                <div class="badge-tag" style="font-size: 0.9rem; padding: 8px 16px;">
                    ${result.passed ? '🎉 Assessment Passed!' : '⚠️ Attempt Completed'}
                </div>
            ` : ''}
        </div>
    `;

    if (submitted && result) {
        html += `
            <div class="quiz-result-banner">
                <div>
                    <h3 style="color: ${result.passed ? '#34d399' : '#fbbf24'};">${result.passed ? 'Skill Certification Unlocked!' : 'Keep Learning & Retake'}</h3>
                    <p style="color: var(--text-muted); margin-top: 4px;">You scored <strong>${result.score}</strong> / ${result.max_score} points (${result.correct_count} of ${result.total_questions} correct).</p>
                </div>
                <button class="btn-secondary" onclick="fetchAndRenderQuiz(state.selectedQuizTrackId)">
                    <i data-lucide="rotate-ccw"></i>
                    <span>Retake Quiz</span>
                </button>
            </div>
        `;
    }

    questions.forEach((q, idx) => {
        const userChoice = answers[q.id];
        let detail = null;
        if (submitted && result && result.details) {
            detail = result.details.find(d => d.quiz_id === q.id);
        }

        html += `
            <div class="quiz-question-box">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="q-badge">Question ${idx + 1} of ${questions.length}</span>
                    <span style="font-size: 0.8rem; color: var(--pydah-gold); font-weight: 600;">+${q.points} Points</span>
                </div>
                <h4 class="q-title">${q.question}</h4>

                <div class="q-options-grid">
                    ${q.options.map((opt, optIdx) => {
                        let optClass = '';
                        if (userChoice === optIdx) optClass = 'selected';

                        if (submitted && detail) {
                            if (detail.correct_index === optIdx) optClass = 'correct';
                            else if (detail.user_choice === optIdx && !detail.is_correct) optClass = 'wrong';
                        }

                        const bullet = String.fromCharCode(65 + optIdx);
                        return `
                            <div class="q-opt-label ${optClass}" onclick="handleSelectQuizOption(${q.id}, ${optIdx})">
                                <span class="q-opt-bullet">${bullet}</span>
                                <span>${opt}</span>
                            </div>
                        `;
                    }).join('')}
                </div>

                ${submitted && detail && detail.explanation ? `
                    <div class="quiz-explanation-box">
                        <strong>Explanation:</strong> ${detail.explanation}
                    </div>
                ` : ''}
            </div>
        `;
    });

    if (!submitted) {
        html += `
            <div style="display: flex; justify-content: flex-end; margin-top: 10px;">
                <button class="btn-primary" onclick="handleSubmitQuiz()">
                    <i data-lucide="send"></i>
                    <span>Submit Assessment for Grading</span>
                </button>
            </div>
        `;
    }

    container.innerHTML = html;
    lucide.createIcons();
}

function handleSelectQuizOption(quizId, optionIndex) {
    if (state.quizState.submitted) return;
    state.quizState.answers[quizId] = optionIndex;
    renderQuizQuestions();
}

async function handleSubmitQuiz() {
    const { questions, answers } = state.quizState;
    const answeredCount = Object.keys(answers).length;

    if (answeredCount < questions.length) {
        if (!confirm(`You have answered ${answeredCount} of ${questions.length} questions. Submit anyway?`)) {
            return;
        }
    }

    try {
        const res = await fetch('/api/quizzes/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                track_id: state.selectedQuizTrackId,
                answers: answers
            })
        });
        const data = await res.json();

        if (res.ok && data.success) {
            state.quizState.submitted = true;
            state.quizState.result = data;
            notify(`Quiz graded! Score: ${data.score} / ${data.max_score}`, data.passed ? 'success' : 'info');
            renderQuizQuestions();
        } else {
            notify(data.message || 'Error submitting assessment.', 'error');
        }
    } catch (err) {
        notify('Network error submitting quiz.', 'error');
    }
}

// -----------------------------------------------------------------------------
// TAB 5: PROJECTS PORTFOLIO
// -----------------------------------------------------------------------------
async function loadProjects() {
    try {
        const res = await fetch('/api/projects');
        const data = await res.json();
        if (!data.success) return;

        const grid = document.getElementById('projects-grid');
        if (data.projects.length === 0) {
            grid.innerHTML = `
                <div style="grid-column: 1 / -1; padding: 40px; text-align: center; color: var(--text-muted);">
                    <i data-lucide="folder" style="width: 48px; height: 48px; margin-bottom: 12px; color: var(--text-dim);"></i>
                    <h3>No Student Projects Submitted Yet</h3>
                    <p>Click 'Add Project to Portfolio' to showcase your system architecture.</p>
                </div>
            `;
            lucide.createIcons();
            return;
        }

        grid.innerHTML = data.projects.map(p => {
            const isVerified = p.status === 'Verified & Approved';
            const techList = p.tech_stack.split(',').map(t => t.trim());

            return `
                <div class="project-card">
                    <div>
                        <div class="proj-top">
                            <span class="proj-track-chip">${p.track_title || 'Engineering'}</span>
                            <span class="proj-status-badge ${isVerified ? 'verified' : 'review'}">
                                ${isVerified ? '✓ Verified Portfolio' : '⏳ Under Review'}
                            </span>
                        </div>

                        <h4 class="proj-title">${p.title}</h4>
                        <p class="proj-summary">${p.summary}</p>

                        <div class="proj-tech-tags">
                            ${techList.map(t => `<span class="tech-pill">${t}</span>`).join('')}
                        </div>

                        ${p.endorsement_remarks ? `
                            <div class="proj-mentor-remarks">
                                <strong>Pydah Cell Review:</strong> ${p.endorsement_remarks}
                            </div>
                        ` : ''}
                    </div>

                    <div class="proj-footer-links">
                        ${p.github_url ? `
                            <a href="${p.github_url}" target="_blank" rel="noopener" class="proj-link">
                                <svg style="width:14px;height:14px;fill:currentColor;vertical-align:-2px;margin-right:4px;" viewBox="0 0 24 24"><path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/></svg>Source Code
                            </a>
                        ` : ''}
                        ${p.live_demo_url ? `
                            <a href="${p.live_demo_url}" target="_blank" rel="noopener" class="proj-link">
                                <i data-lucide="external-link"></i> Live Demo
                            </a>
                        ` : ''}
                        <span style="font-size: 0.75rem; color: var(--text-dim); margin-left: auto;">By ${p.student_name || 'Student'}</span>
                    </div>
                </div>
            `;
        }).join('');

        lucide.createIcons();
    } catch (err) {
        console.error('Projects load error:', err);
    }
}

async function handleProjectSubmit(e) {
    e.preventDefault();
    const title = document.getElementById('proj-title').value.trim();
    const track_id = document.getElementById('proj-track').value;
    const tech_stack = document.getElementById('proj-tech').value.trim();
    const summary = document.getElementById('proj-summary').value.trim();
    const github_url = document.getElementById('proj-github').value.trim();
    const live_demo_url = document.getElementById('proj-demo').value.trim();

    try {
        const res = await fetch('/api/projects', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, track_id, tech_stack, summary, github_url, live_demo_url })
        });
        const data = await res.json();

        if (res.ok && data.success) {
            notify('Project added to your portfolio! (+200 XP)', 'success');
            closeModal('modal-add-project');
            document.getElementById('project-submit-form').reset();
            await loadProjects();
        } else {
            notify(data.message || 'Error submitting project.', 'error');
        }
    } catch (err) {
        notify('Network error submitting project.', 'error');
    }
}

// -----------------------------------------------------------------------------
// TAB 6: PLACEMENT RADAR WITH SEARCH & FILTERS
// -----------------------------------------------------------------------------
async function loadPlacements() {
    try {
        const { category, location } = state.placementFilter;
        let url = `/api/placements?category=${encodeURIComponent(category)}&location=${encodeURIComponent(location)}`;

        const res = await fetch(url);
        const data = await res.json();
        if (!data.success) return;

        renderFilteredPlacements(data.placements);
    } catch (err) {
        console.error('Placements load error:', err);
    }
}

function setPlacementPackageFilter(category) {
    state.placementFilter.category = category;
    document.querySelectorAll('#package-filter-chips .filter-chip').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.val === category);
    });
    loadPlacements();
}

function handlePlacementFilter() {
    const loc = document.getElementById('placement-location-select').value;
    const query = document.getElementById('placement-search-input').value.trim().toLowerCase();
    
    state.placementFilter.location = loc;
    state.placementFilter.searchQuery = query;
    loadPlacements();
}

function renderFilteredPlacements(placements) {
    const grid = document.getElementById('placements-grid');
    const query = state.placementFilter.searchQuery;

    let filtered = placements;
    if (query) {
        filtered = placements.filter(p => 
            p.company.toLowerCase().includes(query) ||
            p.role.toLowerCase().includes(query) ||
            p.required_skills.toLowerCase().includes(query)
        );
    }

    if (filtered.length === 0) {
        grid.innerHTML = `
            <div style="grid-column: 1 / -1; padding: 36px; text-align: center; color: var(--text-muted);">
                <i data-lucide="filter" style="width: 42px; height: 42px; margin-bottom: 10px; color: var(--text-dim);"></i>
                <h4>No Placement Drives Match Your Filter</h4>
                <p>Try clearing your search query or switching package tiers.</p>
            </div>
        `;
        lucide.createIcons();
        return;
    }

    grid.innerHTML = filtered.map(p => {
        const skills = p.required_skills.split(',').map(s => s.trim());

        return `
            <div class="placement-card">
                <div>
                    <div class="p-header">
                        <div>
                            <h4 class="p-company">${p.company}</h4>
                            <span class="p-role">${p.role}</span>
                        </div>
                        <div class="p-match-gauge">
                            <span class="match-pct-text">${p.match_percent}%</span>
                            <span class="match-pct-label">Skill Match</span>
                        </div>
                    </div>

                    <div class="p-package-row">
                        <span class="p-package">${p.package_or_stipend}</span>
                        <span class="p-location"><i data-lucide="map-pin" style="width: 14px; height: 14px; display: inline;"></i> ${p.location}</span>
                    </div>

                    <div class="p-skills-box">
                        <span class="p-skills-label">Required Competencies:</span>
                        <div style="display: flex; flex-wrap: wrap; gap: 6px;">
                            ${skills.map(s => `<span class="skill-tag">${s}</span>`).join('')}
                        </div>
                    </div>

                    <div style="font-size: 0.78rem; color: var(--text-muted); margin-bottom: 14px;">
                        <strong>Eligibility:</strong> ${p.eligibility}
                    </div>
                </div>

                <div class="p-footer">
                    <span class="p-deadline">Apply by: <strong>${p.deadline}</strong></span>
                    <button class="btn-primary" style="padding: 7px 16px; font-size: 0.82rem;" onclick="applyForPlacement('${p.company}', '${p.role}', '${p.apply_link}')">
                        <span>Direct Apply</span>
                        <i data-lucide="send"></i>
                    </button>
                </div>
            </div>
        `;
    }).join('');

    lucide.createIcons();
}

function applyForPlacement(company, role, link) {
    notify(`Forwarding verified candidate profile for ${company} (${role})...`, 'success');
    setTimeout(() => {
        if (link && link !== '#') {
            window.open(link, '_blank');
        } else {
            notify(`Application dossier registered with Pydah Placement Directorate!`, 'success');
        }
    }, 1000);
}

// -----------------------------------------------------------------------------
// TAB 7: CAMPUS LEADERBOARD
// -----------------------------------------------------------------------------
async function loadLeaderboard() {
    try {
        const res = await fetch('/api/leaderboard');
        const data = await res.json();
        if (!data.success) return;

        const tbody = document.getElementById('leaderboard-tbody');
        tbody.innerHTML = data.leaderboard.map((u, idx) => {
            const rankNum = idx + 1;
            let rankBadge = rankNum;
            if (rankNum === 1) rankBadge = '🥇';
            else if (rankNum === 2) rankBadge = '🥈';
            else if (rankNum === 3) rankBadge = '🥉';

            const initials = u.name.split(' ').map(n => n[0]).join('').substring(0, 2);

            return `
                <tr>
                    <td><span class="rank-medal ${rankNum === 1 ? 'gold' : rankNum === 2 ? 'silver' : rankNum === 3 ? 'bronze' : ''}">${rankBadge}</span></td>
                    <td>
                        <div class="student-col-info">
                            <div class="student-lead-avatar">${initials}</div>
                            <div>
                                <strong style="color: #ffffff; display: block;">${u.name}</strong>
                                <span style="font-size: 0.76rem; color: var(--text-dim);">${u.badges_count} Certifications</span>
                            </div>
                        </div>
                    </td>
                    <td>${u.department} • ${u.year_or_designation}</td>
                    <td><span class="badge-tag">${u.target_role}</span></td>
                    <td><strong style="color: #34d399;">${u.completed_modules} Modules</strong></td>
                    <td><span class="karma-xp-badge">⚡ ${u.karma_xp} XP</span></td>
                </tr>
            `;
        }).join('');

        lucide.createIcons();
    } catch (err) {
        console.error('Leaderboard error:', err);
    }
}

// -----------------------------------------------------------------------------
// TAB 8: SKILL PASSPORT & OFFICIAL ACADEMIC CERTIFICATE
// -----------------------------------------------------------------------------
state.certificateTheme = 'parchment';

function setCertificateTheme(theme) {
    state.certificateTheme = theme;
    const doc = document.getElementById('passport-document');
    const btnParchment = document.getElementById('btn-theme-parchment');
    const btnMidnight = document.getElementById('btn-theme-midnight');

    if (doc) {
        doc.className = `academic-certificate-sheet theme-${theme}`;
    }

    if (btnParchment && btnMidnight) {
        btnParchment.classList.toggle('active', theme === 'parchment');
        btnMidnight.classList.toggle('active', theme === 'midnight');
    }
    notify(`Certificate theme changed to ${theme === 'parchment' ? 'Royal Parchment Gold' : 'Executive Midnight Obsidian'}`, 'info');
}

function printCertificate() {
    notify('Preparing print engine for high-resolution Certificate of Distinction...', 'info');
    setTimeout(() => {
        window.print();
    }, 400);
}

async function loadSkillPassport() {
    try {
        const res = await fetch('/api/passport');
        const data = await res.json();
        if (!data.success) return;

        const doc = document.getElementById('passport-document');
        const u = data.user;
        const compCount = data.completed_modules.length;
        const projCount = data.projects.length;
        const verificationId = data.verification_id || `PYDAH-SP-${u.id.toString().padStart(4, '0')}-2026`;

        // Extract key technical skills
        const skillsSet = new Set();
        data.completed_modules.forEach(m => {
            m.key_skills.split(',').forEach(s => {
                if (s.trim()) skillsSet.add(s.trim());
            });
        });
        const skillsList = Array.from(skillsSet).slice(0, 10);

        doc.className = `academic-certificate-sheet theme-${state.certificateTheme}`;
        doc.innerHTML = `
            <div class="cert-inner-frame">
                <!-- Ornate Corner Filigree Brackets -->
                <div class="cert-corner corner-tl"></div>
                <div class="cert-corner corner-tr"></div>
                <div class="cert-corner corner-bl"></div>
                <div class="cert-corner corner-br"></div>

                <!-- 1. Institutional Header Block -->
                <div class="cert-header-block">
                    <div class="cert-logo-container">
                        <img src="/static/images/pydah_logo.png" alt="PYDAH GROUP Logo" class="cert-pydah-logo">
                    </div>
                    <div class="inst-main-name">PYDAH EDUCATIONAL ACADEMY</div>
                    <div class="inst-accreditation">
                        Autonomous Engineering Institution • Approved by AICTE, Affiliated to JNTUK • Accredited with 'A+' Grade by NAAC
                    </div>
                    <div>
                        <span class="cert-main-heading">Certificate of Career Mastery</span>
                    </div>
                    <div style="font-size: 0.76rem; color: #b45309; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;">
                        CONFERRED UNDER THE AUTHORITY OF THE ACADEMIC & TECHNICAL COUNCIL
                    </div>
                </div>

                <!-- 2. Recipient Presentation Block -->
                <div class="cert-center-body">
                    <div class="cert-recipient-intro">This is to officially and proudly certify that</div>
                    <div class="cert-student-name">${u.name}</div>
                    <div class="cert-student-sub">
                        Registration ID: <strong>${verificationId}</strong> &nbsp;•&nbsp; Department of <strong>${u.department}</strong> (${u.year_or_designation})
                    </div>

                    <div class="cert-statement">
                        has demonstrated distinguished engineering competencies, completed the rigorous curriculum roadmap, verified hands-on production capstones, and exceeded institutional placement benchmarks in
                        <span class="cert-track-highlight">${u.target_role}</span>
                    </div>
                </div>

                <!-- 3. Metrics & Verified Competencies Matrix -->
                <div class="cert-stats-row">
                    <div class="cert-stat-item">
                        <span class="cert-stat-label">Roadmap Modules</span>
                        <span class="cert-stat-val">${compCount} Verified</span>
                    </div>
                    <div class="cert-stat-item">
                        <span class="cert-stat-label">Endorsed Capstones</span>
                        <span class="cert-stat-val">${projCount} Repositories</span>
                    </div>
                    <div class="cert-stat-item">
                        <span class="cert-stat-label">Skill Karma XP</span>
                        <span class="cert-stat-val">⚡ ${u.karma_xp || 880} XP</span>
                    </div>
                    <div class="cert-stat-item">
                        <span class="cert-stat-label">Placement Readiness</span>
                        <span class="cert-stat-val" style="color: #10b981;">78% Exceeded</span>
                    </div>
                </div>

                <!-- Mastered Competency Pills -->
                ${skillsList.length > 0 ? `
                    <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 6px; margin: 10px 0 16px;">
                        ${skillsList.map(s => `
                            <span style="font-size: 0.72rem; font-family: 'JetBrains Mono', monospace; background: rgba(234, 88, 12, 0.08); border: 1px solid rgba(234, 88, 12, 0.25); padding: 2px 8px; border-radius: 4px; font-weight: 600;">
                                ${s}
                            </span>
                        `).join('')}
                    </div>
                ` : ''}

                <!-- 4. Signatures & Official Gold Wax Seal Row -->
                <div class="cert-footer-row">
                    <!-- Left: Dean Signature -->
                    <div class="cert-sign-col">
                        <div class="cert-signature-art">Dr. K. S. Rao, Ph.D.</div>
                        <div class="cert-sign-rule"></div>
                        <div class="cert-sign-title">Dean of Academic Affairs</div>
                        <div class="cert-sign-sub">Pydah Academic Council</div>
                    </div>

                    <!-- Center: Metallic Gold Embossed Seal -->
                    <div class="cert-seal-col">
                        <div class="gold-wax-seal">
                            <span>PYDAH</span>
                            <span>OFFICIAL</span>
                            <span>SEAL</span>
                        </div>
                        <div class="cert-verification-tag">
                            ${verificationId}
                        </div>
                    </div>

                    <!-- Right: Placement Director Signature -->
                    <div class="cert-sign-col">
                        <div class="cert-signature-art">Prof. P. Ramachandra</div>
                        <div class="cert-sign-rule"></div>
                        <div class="cert-sign-title">Director of Placements</div>
                        <div class="cert-sign-sub">Corporate Relations Directorate</div>
                    </div>
                </div>
            </div>
        `;

        lucide.createIcons();
    } catch (err) {
        console.error('Skill passport error:', err);
    }
}

async function openAtsResumeModal() {
    try {
        const res = await fetch('/api/passport');
        const data = await res.json();
        if (data.success && data.ats_resume_snippet) {
            document.getElementById('ats-resume-text').textContent = data.ats_resume_snippet;
            openModal('modal-ats-resume');
        }
    } catch (err) {
        notify('Error generating ATS snippet.', 'error');
    }
}

function copyAtsResumeToClipboard() {
    const text = document.getElementById('ats-resume-text').textContent;
    navigator.clipboard.writeText(text).then(() => {
        notify('ATS Resume Snippet copied to clipboard! Ready to paste into resume.', 'success');
        closeModal('modal-ats-resume');
    }).catch(() => {
        notify('Could not copy to clipboard.', 'error');
    });
}

// -----------------------------------------------------------------------------
// MODAL CONTROLLERS
// -----------------------------------------------------------------------------
function openModal(modalId) {
    const m = document.getElementById(modalId);
    if (m) {
        m.classList.remove('hidden');
        lucide.createIcons();
    }
}

function closeModal(modalId) {
    const m = document.getElementById(modalId);
    if (m) m.classList.add('hidden');
}

window.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-overlay')) {
        e.target.classList.add('hidden');
    }
});

// -----------------------------------------------------------------------------
// TAB 9: STUDENT RECRUITER PORTFOLIO CONTROLLER
// -----------------------------------------------------------------------------
async function loadPortfolioEditor() {
    if (!state.user) return;

    const liveUrl = `${window.location.origin}/portfolio/${state.user.id}`;
    const urlDisplay = document.getElementById('portfolio-live-url');
    const openBtn = document.getElementById('btn-open-portfolio-tab');
    
    if (urlDisplay) urlDisplay.textContent = liveUrl;
    if (openBtn) openBtn.href = `/portfolio/${state.user.id}`;

    try {
        const res = await fetch(`/api/portfolio/${state.user.id}`);
        if (res.ok) {
            const data = await res.json();
            const u = data.portfolio.user;

            const elTagline = document.getElementById('port-tagline');
            const elBio = document.getElementById('port-bio');
            const elGithub = document.getElementById('port-github');
            const elLinkedin = document.getElementById('port-linkedin');
            const elLocation = document.getElementById('port-location');
            const elPhone = document.getElementById('port-phone');
            const elSkills = document.getElementById('port-skills');
            const elAvatar = document.getElementById('port-avatar-url');

            if (elTagline) elTagline.value = u.tagline || 'Computer Science Student, Python Developer & Robotics Enthusiast';
            if (elBio) elBio.value = u.bio || '';
            if (elGithub) elGithub.value = u.github_url || 'https://github.com/ismrs-tech';
            if (elLinkedin) elLinkedin.value = u.linkedin_url || 'https://linkedin.com/in/pydah-student';
            if (elLocation) elLocation.value = u.location || 'Kakinada, Andhra Pradesh, India';
            if (elPhone) elPhone.value = u.phone || '+91 98765 43210';
            if (elSkills) elSkills.value = u.custom_skills || 'Python, Flask, JavaScript, React, REST APIs, SQLite, Machine Learning, Robotics & IoT, Embedded C';
            if (elAvatar) elAvatar.value = u.profile_image_url || '/static/images/student_avatar.jpg';
            const preview = document.getElementById('port-avatar-preview');
            if (preview && u.profile_image_url) {
                preview.src = u.profile_image_url;
            }
        }
    } catch (err) {
        console.error('Error loading portfolio data:', err);
    }
}

async function handleAvatarFileSelect(e) {
    const file = e.target.files[0];
    if (!file) return;

    // Instant local preview
    const reader = new FileReader();
    reader.onload = (event) => {
        const preview = document.getElementById('port-avatar-preview');
        if (preview) preview.src = event.target.result;
    };
    reader.readAsDataURL(file);

    const statusEl = document.getElementById('photo-upload-status');
    if (statusEl) {
        statusEl.innerHTML = `<span style="color: var(--cyan-accent); font-weight: 600;">Uploading...</span>`;
    }

    const formData = new FormData();
    formData.append('avatar_file', file);

    try {
        const res = await fetch('/api/portfolio/upload-avatar', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        if (res.ok && data.success) {
            notify(data.message || 'Photo updated successfully!', 'success');
            document.getElementById('port-avatar-url').value = data.avatar_url;
            if (statusEl) {
                statusEl.innerHTML = `<span style="color: #34d399; font-weight: 600;">✓ Saved to Profile</span>`;
            }
            if (state.user) {
                state.user.profile_image_url = data.avatar_url;
            }
        } else {
            notify(data.message || 'Upload failed.', 'error');
            if (statusEl) statusEl.textContent = 'Upload failed';
        }
    } catch (err) {
        notify('Network error uploading image.', 'error');
        if (statusEl) statusEl.textContent = 'Network error';
    }
}

async function handleSavePortfolioSettings(e) {
    e.preventDefault();
    if (!state.user) return;

    const btn = document.getElementById('btn-save-portfolio');
    btn.disabled = true;
    btn.innerHTML = `<span>Saving Changes...</span>`;

    const payload = {
        tagline: document.getElementById('port-tagline').value.trim(),
        bio: document.getElementById('port-bio').value.trim(),
        github_url: document.getElementById('port-github').value.trim(),
        linkedin_url: document.getElementById('port-linkedin').value.trim(),
        location: document.getElementById('port-location').value.trim(),
        phone: document.getElementById('port-phone').value.trim(),
        custom_skills: document.getElementById('port-skills').value.trim(),
        profile_image_url: document.getElementById('port-avatar-url').value.trim() || '/static/images/student_avatar.jpg'
    };

    try {
        const res = await fetch('/api/portfolio/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (res.ok && data.success) {
            notify(data.message || 'Portfolio profile updated successfully!', 'success');
            // Update local user state
            Object.assign(state.user, payload);
        } else {
            notify(data.message || 'Failed to update portfolio.', 'error');
        }
    } catch (err) {
        notify('Network error updating portfolio settings.', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<i data-lucide="save"></i><span>Save Portfolio Changes</span>`;
        lucide.createIcons();
    }
}

function copyPortfolioLink() {
    if (!state.user) return;
    const liveUrl = `${window.location.origin}/portfolio/${state.user.id}`;
    navigator.clipboard.writeText(liveUrl).then(() => {
        notify('Recruiter Portfolio Link copied to clipboard! Share it anywhere.', 'success');
    }).catch(() => {
        notify('Could not copy link to clipboard.', 'error');
    });
}

function openLivePortfolioTab() {
    if (!state.user) return;
    window.open(`/portfolio/${state.user.id}`, '_blank');
}

