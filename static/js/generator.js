// ─── AI Generators ───────────────────────────────────────────────────
const Generator = (() => {

    async function apiPost(url, data) {
        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        return res.json();
    }

    function showLoading(el) {
        el.innerHTML = '<div class="loading"><div class="spinner"></div>生成中...</div>';
    }

    function sourceBadge(source) {
        const cls = source === 'ai' ? 'ai' : 'template';
        const label = source === 'ai' ? 'AI 生成' : '模板生成';
        return `<span class="source-badge ${cls}">${label}</span>`;
    }

    // ─── Character Name ──────────────────────────────────────────────
    async function generateCharacterName() {
        const genre = document.getElementById('charNameGenre').value;
        const gender = document.querySelector('input[name="charNameGender"]:checked').value;
        const count = parseInt(document.getElementById('charNameCount').value);
        const useAI = document.getElementById('charNameAI').checked;
        const results = document.getElementById('charNameResults');

        showLoading(results);

        try {
            const data = await apiPost('/api/generate/character-name', {
                genre, gender, count, use_ai: useAI,
            });

            let html = sourceBadge(data.source);
            html += '<div class="name-tag-list">';
            data.names.forEach(name => {
                html += `<div class="name-tag" onclick="copyText('${name}')">
                    ${name}
                    <span class="copy-hint">点击复制</span>
                </div>`;
            });
            html += '</div>';
            results.innerHTML = html;
        } catch (err) {
            results.innerHTML = '<p class="empty-hint">生成失败，请重试</p>';
        }
    }

    // ─── Character Setting ───────────────────────────────────────────
    async function generateCharacterSetting() {
        const genre = document.getElementById('charSettingGenre').value;
        const gender = document.querySelector('input[name="charSettingGender"]:checked').value;
        const useAI = document.getElementById('charSettingAI').checked;
        const results = document.getElementById('charSettingResults');

        showLoading(results);

        try {
            const data = await apiPost('/api/generate/character-setting', {
                genre, gender, use_ai: useAI,
            });

            let html = sourceBadge(data.source);

            if (typeof data.setting === 'string') {
                html += `<div class="char-card"><div class="char-card-body">
                    <div class="char-field"><div class="char-field-value">${data.setting.replace(/\n/g, '<br>')}</div></div>
                </div></div>`;
            } else {
                const s = data.setting;
                const initial = s.name ? s.name.charAt(s.name.length - 1) : '?';
                html += `
                <div class="char-card">
                    <div class="char-card-header">
                        <div class="char-avatar">${initial}</div>
                        <div>
                            <div class="char-name">${s.name}</div>
                            <div class="char-gender">${s.gender} · ${genre}</div>
                        </div>
                    </div>
                    <div class="char-card-body">
                        <div class="char-field">
                            <div class="char-field-label">性格特征</div>
                            <div class="char-field-value">${s.personality}</div>
                        </div>
                        <div class="char-field">
                            <div class="char-field-label">身世背景</div>
                            <div class="char-field-value">${s.background}</div>
                        </div>
                        <div class="char-field">
                            <div class="char-field-label">能力特长</div>
                            <div class="char-field-value">${s.abilities}</div>
                        </div>
                        <div class="char-field">
                            <div class="char-field-label">外貌描述</div>
                            <div class="char-field-value">${s.appearance}</div>
                        </div>
                    </div>
                </div>`;
            }
            results.innerHTML = html;
        } catch (err) {
            results.innerHTML = '<p class="empty-hint">生成失败，请重试</p>';
        }
    }

    // ─── Background Setting ──────────────────────────────────────────
    async function generateBackground() {
        const genre = document.getElementById('bgGenre').value;
        const useAI = document.getElementById('bgAI').checked;
        const results = document.getElementById('bgResults');

        showLoading(results);

        try {
            const data = await apiPost('/api/generate/background', {
                genre, use_ai: useAI,
            });

            let html = sourceBadge(data.source);

            if (typeof data.setting === 'string') {
                html += `<div class="world-section full-width">
                    <div class="world-section-text">${data.setting.replace(/\n/g, '<br>')}</div>
                </div>`;
            } else {
                const s = data.setting;
                html += `
                <div class="world-card">
                    <div class="world-section">
                        <div class="world-section-title">世界描述</div>
                        <div class="world-section-text">${s.world_description}</div>
                    </div>
                    <div class="world-section">
                        <div class="world-section-title">力量体系</div>
                        <div class="world-section-text">${s.power_system}</div>
                    </div>
                    <div class="world-section">
                        <div class="world-section-title">势力格局</div>
                        <div class="world-section-text">${s.factions}</div>
                    </div>
                    <div class="world-section">
                        <div class="world-section-title">地理环境</div>
                        <div class="world-section-text">${s.geography}</div>
                    </div>
                </div>`;
            }
            results.innerHTML = html;
        } catch (err) {
            results.innerHTML = '<p class="empty-hint">生成失败，请重试</p>';
        }
    }

    // ─── Novel Name ──────────────────────────────────────────────────
    async function generateNovelName() {
        const genre = document.getElementById('novelNameGenre').value;
        const count = parseInt(document.getElementById('novelNameCount').value);
        const useAI = document.getElementById('novelNameAI').checked;
        const results = document.getElementById('novelNameResults');

        showLoading(results);

        try {
            const data = await apiPost('/api/generate/novel-name', {
                genre, count, use_ai: useAI,
            });

            let html = sourceBadge(data.source);
            html += '<div class="name-tag-list">';
            data.names.forEach(name => {
                html += `<div class="name-tag" onclick="copyText('${name}')">
                    《${name}》
                    <span class="copy-hint">点击复制</span>
                </div>`;
            });
            html += '</div>';
            results.innerHTML = html;
        } catch (err) {
            results.innerHTML = '<p class="empty-hint">生成失败，请重试</p>';
        }
    }

    // ─── Cover ───────────────────────────────────────────────────────
    async function generateCover() {
        const title = document.getElementById('coverTitle').value.trim();
        const author = document.getElementById('coverAuthor').value.trim();
        const genre = document.getElementById('coverGenre').value;
        const results = document.getElementById('coverResults');

        if (!title) {
            showToast('请输入书名');
            return;
        }

        showLoading(results);

        try {
            const data = await apiPost('/api/generate/cover', {
                title, author, genre,
            });

            const canvas = document.getElementById('coverCanvas');
            results.innerHTML = '';
            results.appendChild(canvas);
            canvas.style.display = 'block';

            drawCover(canvas, data.cover);

            document.getElementById('downloadCoverBtn').style.display = 'block';
        } catch (err) {
            results.innerHTML = '<p class="empty-hint">生成失败，请重试</p>';
        }
    }

    function drawCover(canvas, cover) {
        const ctx = canvas.getContext('2d');
        const w = canvas.width;
        const h = canvas.height;

        const gradient = ctx.createLinearGradient(0, 0, w, h);
        gradient.addColorStop(0, cover.bg_color);
        gradient.addColorStop(1, shiftColor(cover.bg_color, 30));
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, w, h);

        drawDecorations(ctx, w, h, cover);

        ctx.fillStyle = cover.accent_color;
        ctx.globalAlpha = 0.1;
        ctx.fillRect(0, h * 0.3, w, h * 0.4);
        ctx.globalAlpha = 1;

        ctx.fillStyle = cover.accent_color;
        ctx.fillRect(w * 0.1, h * 0.32, w * 0.8, 2);
        ctx.fillRect(w * 0.1, h * 0.68, w * 0.8, 2);

        ctx.fillStyle = '#ffffff';
        ctx.textAlign = 'center';

        const titleSize = cover.title.length <= 4 ? 72 : cover.title.length <= 8 ? 56 : 42;
        ctx.font = `bold ${titleSize}px "PingFang SC", "Microsoft YaHei", serif`;

        if (cover.title.length > 8) {
            const mid = Math.ceil(cover.title.length / 2);
            const line1 = cover.title.slice(0, mid);
            const line2 = cover.title.slice(mid);
            ctx.fillText(line1, w / 2, h * 0.47);
            ctx.fillText(line2, w / 2, h * 0.47 + titleSize + 10);
        } else {
            ctx.fillText(cover.title, w / 2, h * 0.52);
        }

        ctx.font = '20px "PingFang SC", "Microsoft YaHei", sans-serif';
        ctx.fillStyle = cover.accent_color;
        ctx.fillText(cover.author, w / 2, h * 0.76);

        ctx.font = '16px "PingFang SC", "Microsoft YaHei", sans-serif';
        ctx.fillStyle = 'rgba(255,255,255,0.4)';
        ctx.fillText(cover.genre + ' · 小说', w / 2, h * 0.92);
    }

    function drawDecorations(ctx, w, h, cover) {
        ctx.save();
        ctx.globalAlpha = 0.08;
        ctx.strokeStyle = cover.accent_color;
        ctx.lineWidth = 1;

        const element = cover.element;

        if (element === 'cloud' || element === 'flower') {
            for (let i = 0; i < 6; i++) {
                const x = Math.random() * w;
                const y = Math.random() * h * 0.25;
                drawCloud(ctx, x, y, 40 + Math.random() * 60);
            }
            for (let i = 0; i < 4; i++) {
                const x = Math.random() * w;
                const y = h * 0.75 + Math.random() * h * 0.2;
                drawCloud(ctx, x, y, 30 + Math.random() * 50);
            }
        }

        if (element === 'star' || element === 'circuit') {
            ctx.globalAlpha = 0.05;
            ctx.fillStyle = cover.accent_color;
            for (let i = 0; i < 80; i++) {
                const x = Math.random() * w;
                const y = Math.random() * h;
                const r = Math.random() * 2;
                ctx.beginPath();
                ctx.arc(x, y, r, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        if (element === 'mountain' || element === 'bamboo') {
            ctx.globalAlpha = 0.06;
            ctx.fillStyle = cover.accent_color;
            drawMountains(ctx, w, h);
        }

        if (element === 'sword' || element === 'lightning') {
            ctx.globalAlpha = 0.06;
            ctx.strokeStyle = cover.accent_color;
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(w * 0.5, h * 0.05);
            ctx.lineTo(w * 0.5, h * 0.28);
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo(w * 0.42, h * 0.2);
            ctx.lineTo(w * 0.58, h * 0.2);
            ctx.stroke();
        }

        if (element === 'grid' || element === 'ring') {
            ctx.globalAlpha = 0.04;
            ctx.strokeStyle = cover.accent_color;
            for (let i = 0; i < 10; i++) {
                ctx.beginPath();
                ctx.arc(w / 2, h / 2, 50 + i * 40, 0, Math.PI * 2);
                ctx.stroke();
            }
        }

        if (element === 'moon' || element === 'fan') {
            ctx.globalAlpha = 0.06;
            ctx.fillStyle = cover.accent_color;
            ctx.beginPath();
            ctx.arc(w * 0.75, h * 0.15, 50, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = cover.bg_color;
            ctx.beginPath();
            ctx.arc(w * 0.78, h * 0.13, 45, 0, Math.PI * 2);
            ctx.fill();
        }

        ctx.restore();
    }

    function drawCloud(ctx, x, y, size) {
        ctx.beginPath();
        ctx.arc(x, y, size * 0.5, 0, Math.PI * 2);
        ctx.arc(x + size * 0.35, y - size * 0.1, size * 0.35, 0, Math.PI * 2);
        ctx.arc(x + size * 0.6, y, size * 0.3, 0, Math.PI * 2);
        ctx.stroke();
    }

    function drawMountains(ctx, w, h) {
        ctx.beginPath();
        ctx.moveTo(0, h * 0.85);
        const peaks = [0.15, 0.3, 0.5, 0.7, 0.85];
        peaks.forEach(p => {
            ctx.lineTo(w * p, h * (0.7 + Math.random() * 0.1));
            ctx.lineTo(w * (p + 0.07), h * 0.85);
        });
        ctx.lineTo(w, h * 0.85);
        ctx.lineTo(w, h);
        ctx.lineTo(0, h);
        ctx.closePath();
        ctx.fill();
    }

    function shiftColor(hex, amount) {
        let r = parseInt(hex.slice(1, 3), 16);
        let g = parseInt(hex.slice(3, 5), 16);
        let b = parseInt(hex.slice(5, 7), 16);
        r = Math.min(255, r + amount);
        g = Math.min(255, g + amount);
        b = Math.min(255, b + amount);
        return `rgb(${r},${g},${b})`;
    }

    function downloadCover() {
        const canvas = document.getElementById('coverCanvas');
        const link = document.createElement('a');
        link.download = '小说封面.png';
        link.href = canvas.toDataURL('image/png');
        link.click();
        showToast('封面已下载');
    }

    return {
        generateCharacterName,
        generateCharacterSetting,
        generateBackground,
        generateNovelName,
        generateCover,
        downloadCover,
    };
})();
