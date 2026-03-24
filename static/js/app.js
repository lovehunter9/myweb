// ─── Navigation ──────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initTheme();
    checkAIStatus();
    initRangeSliders();
});

function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const page = item.dataset.page;
            navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');

            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            const target = document.getElementById('page-' + page);
            if (target) target.classList.add('active');

            if (window.innerWidth <= 768) {
                document.getElementById('sidebar').classList.remove('open');
            }
        });
    });

    const menuBtn = document.getElementById('mobileMenuBtn');
    if (menuBtn) {
        menuBtn.addEventListener('click', () => {
            document.getElementById('sidebar').classList.toggle('open');
        });
    }
}

// ─── Theme ───────────────────────────────────────────────────────────
function initTheme() {
    const saved = localStorage.getItem('theme') || 'dark';
    applyTheme(saved);

    document.getElementById('themeToggle').addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'light' ? 'dark' : 'light';
        applyTheme(next);
        localStorage.setItem('theme', next);
    });
}

function applyTheme(theme) {
    if (theme === 'light') {
        document.documentElement.setAttribute('data-theme', 'light');
        document.getElementById('themeIcon').textContent = '☀';
    } else {
        document.documentElement.removeAttribute('data-theme');
        document.getElementById('themeIcon').textContent = '☽';
    }
}

// ─── AI Status ───────────────────────────────────────────────────────
function checkAIStatus() {
    fetch('/api/ai/status')
        .then(r => r.json())
        .then(data => {
            const el = document.getElementById('aiStatus');
            const dot = el.querySelector('.status-dot');
            const label = el.querySelector('.nav-label');
            if (data.available) {
                dot.classList.remove('offline');
                dot.classList.add('online');
                label.textContent = 'AI 在线';
            } else {
                dot.classList.remove('online');
                dot.classList.add('offline');
                label.textContent = 'AI 离线';
            }
        })
        .catch(() => {});
}

// ─── Range Sliders ───────────────────────────────────────────────────
function initRangeSliders() {
    const pairs = [
        ['charNameCount', 'charNameCountVal'],
        ['novelNameCount', 'novelNameCountVal'],
    ];
    pairs.forEach(([sliderId, valId]) => {
        const slider = document.getElementById(sliderId);
        const val = document.getElementById(valId);
        if (slider && val) {
            slider.addEventListener('input', () => { val.textContent = slider.value; });
        }
    });
}

// ─── Toast ───────────────────────────────────────────────────────────
function showToast(msg) {
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2500);
}

// ─── Copy to clipboard ──────────────────────────────────────────────
function copyText(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('已复制: ' + text);
    }).catch(() => {
        showToast('复制失败');
    });
}
