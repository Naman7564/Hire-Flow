/* ============================================
   HR HIRING PLATFORM — Main JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', function () {
    initSidebar();
    initAlerts();
    initFormValidation();
    initAnimations();
    initSearchBar();
});

/* ============================================
   Sidebar Toggle (Mobile)
   ============================================ */
function initSidebar() {
    const hamburger = document.getElementById('hamburgerBtn');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');

    if (hamburger && sidebar) {
        hamburger.addEventListener('click', () => {
            sidebar.classList.toggle('active');
            if (overlay) overlay.classList.toggle('active');
        });
    }

    if (overlay) {
        overlay.addEventListener('click', () => {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
        });
    }
}

/* ============================================
   Auto-dismiss Alerts
   ============================================ */
function initAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach((alert, index) => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-8px)';
            setTimeout(() => alert.remove(), 300);
        }, 4000 + index * 500);
    });
}

/* ============================================
   Form Validation
   ============================================ */
function initFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');

    forms.forEach(form => {
        const inputs = form.querySelectorAll('.form-control[required]');

        inputs.forEach(input => {
            input.addEventListener('blur', () => validateField(input));
            input.addEventListener('input', () => {
                if (input.classList.contains('is-invalid')) {
                    validateField(input);
                }
            });
        });

        form.addEventListener('submit', function (e) {
            let isValid = true;
            inputs.forEach(input => {
                if (!validateField(input)) {
                    isValid = false;
                }
            });

            // Password match validation
            const password1 = form.querySelector('#id_password1');
            const password2 = form.querySelector('#id_password2');
            if (password1 && password2 && password1.value !== password2.value) {
                showFieldError(password2, 'Passwords do not match');
                isValid = false;
            }

            // Email validation
            const emailField = form.querySelector('input[type="email"]');
            if (emailField && emailField.value && !isValidEmail(emailField.value)) {
                showFieldError(emailField, 'Please enter a valid email address');
                isValid = false;
            }

            if (!isValid) {
                e.preventDefault();
                const firstError = form.querySelector('.is-invalid');
                if (firstError) {
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    firstError.focus();
                }
            }
        });
    });
}

function validateField(input) {
    const value = input.value.trim();
    clearFieldError(input);

    if (input.hasAttribute('required') && !value) {
        showFieldError(input, 'This field is required');
        return false;
    }

    if (input.type === 'email' && value && !isValidEmail(value)) {
        showFieldError(input, 'Please enter a valid email');
        return false;
    }

    if (input.minLength > 0 && value.length < input.minLength) {
        showFieldError(input, `Minimum ${input.minLength} characters required`);
        return false;
    }

    return true;
}

function showFieldError(input, message) {
    input.classList.add('is-invalid');
    input.style.borderColor = '#ef4444';
    input.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.15)';

    let errorEl = input.parentElement.querySelector('.form-error');
    if (!errorEl) {
        errorEl = document.createElement('div');
        errorEl.className = 'form-error';
        input.parentElement.appendChild(errorEl);
    }
    errorEl.textContent = message;
}

function clearFieldError(input) {
    input.classList.remove('is-invalid');
    input.style.borderColor = '';
    input.style.boxShadow = '';

    const errorEl = input.parentElement.querySelector('.form-error');
    if (errorEl) errorEl.remove();
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

/* ============================================
   Intersection Observer Animations
   ============================================ */
function initAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -30px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.stat-card, .job-card, .card').forEach(el => {
        observer.observe(el);
    });
}

/* ============================================
   Live Search Bar
   ============================================ */
function initSearchBar() {
    const topbarSearch = document.getElementById('topbarSearch');
    if (topbarSearch) {
        let debounceTimer;
        topbarSearch.addEventListener('input', function () {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const query = this.value.trim();
                if (query.length >= 2) {
                    // Navigate to search
                    const currentPath = window.location.pathname;
                    if (currentPath.includes('/jobs/')) {
                        window.location.href = `/jobs/?q=${encodeURIComponent(query)}`;
                    } else if (currentPath.includes('/applications/')) {
                        window.location.href = `/applications/all/?q=${encodeURIComponent(query)}`;
                    }
                }
            }, 600);
        });
    }
}

/* ============================================
   Confirm Delete
   ============================================ */
function confirmDelete(itemName) {
    return confirm(`Are you sure you want to delete "${itemName}"? This action cannot be undone.`);
}

/* ============================================
   Pipeline Chart (Simple Canvas)
   ============================================ */
function drawPipelineChart(canvasId, labels, data, colors) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.parentElement.offsetWidth - 24;
    const height = 260;
    canvas.width = width;
    canvas.height = height;

    const maxVal = Math.max(...data, 1);
    const barWidth = Math.min(40, (width - 80) / data.length - 16);
    const chartLeft = 50;
    const chartBottom = height - 40;
    const chartHeight = chartBottom - 20;

    // Clear
    ctx.clearRect(0, 0, width, height);

    // Grid lines
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
        const y = chartBottom - (chartHeight / 4) * i;
        ctx.beginPath();
        ctx.moveTo(chartLeft, y);
        ctx.lineTo(width - 10, y);
        ctx.stroke();

        // Labels
        ctx.fillStyle = '#64748b';
        ctx.font = '11px Inter';
        ctx.textAlign = 'right';
        ctx.fillText(Math.round((maxVal / 4) * i), chartLeft - 8, y + 4);
    }

    // Bars
    const totalWidth = data.length * (barWidth + 16);
    const startX = chartLeft + (width - chartLeft - totalWidth) / 2;

    data.forEach((value, i) => {
        const x = startX + i * (barWidth + 16);
        const barHeight = (value / maxVal) * chartHeight;
        const y = chartBottom - barHeight;

        // Bar gradient
        const gradient = ctx.createLinearGradient(x, y, x, chartBottom);
        gradient.addColorStop(0, colors[i] || '#6366f1');
        gradient.addColorStop(1, (colors[i] || '#6366f1') + '66');

        // Rounded bar
        const radius = Math.min(4, barWidth / 2);
        ctx.beginPath();
        ctx.moveTo(x + radius, y);
        ctx.lineTo(x + barWidth - radius, y);
        ctx.quadraticCurveTo(x + barWidth, y, x + barWidth, y + radius);
        ctx.lineTo(x + barWidth, chartBottom);
        ctx.lineTo(x, chartBottom);
        ctx.lineTo(x, y + radius);
        ctx.quadraticCurveTo(x, y, x + radius, y);
        ctx.fillStyle = gradient;
        ctx.fill();

        // Value
        ctx.fillStyle = '#f1f5f9';
        ctx.font = '600 12px Inter';
        ctx.textAlign = 'center';
        ctx.fillText(value, x + barWidth / 2, y - 8);

        // Label
        ctx.fillStyle = '#94a3b8';
        ctx.font = '10px Inter';
        ctx.fillText(labels[i], x + barWidth / 2, chartBottom + 18);
    });
}

/* ============================================
   Skills Tag Input Enhancement
   ============================================ */
function initSkillsInput(inputId) {
    const input = document.getElementById(inputId);
    if (!input) return;

    // Show tags below input
    const tagContainer = document.createElement('div');
    tagContainer.className = 'job-skills';
    tagContainer.style.marginTop = '8px';
    input.parentElement.appendChild(tagContainer);

    function renderTags() {
        const skills = input.value.split(',').filter(s => s.trim());
        tagContainer.innerHTML = skills.map(skill =>
            `<span class="skill-tag">${skill.trim()}</span>`
        ).join('');
    }

    input.addEventListener('input', renderTags);
    renderTags();
}
