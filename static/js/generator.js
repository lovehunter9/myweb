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
        const label = source === 'ai' ? '🤖 AI 生成' : '🎲 模板生成';
        return `<span class="source-badge ${cls}">${label}</span>`;
    }

    async function generateCharacterName() {
        const genre = document.getElementById('charNameGenre').value;
        const gender = document.querySelector('input[name="charNameGender"]:checked').value;
        const count = parseInt(document.getElementById('charNameCount').value);
        const useAI = document.getElementById('charNameAI').checked;
        const results = document.getElementById('charNameResults');
        showLoading(results);
        try {
            const data = await apiPost('/api/generate/character-name', { genre, gender, count, use_ai: useAI });
            let html = sourceBadge(data.source) + '<div class="name-tag-list">';
            data.names.forEach(name => {
                html += `<div class="name-tag" onclick="copyText('${name}')">${name}<span class="copy-hint">点击复制</span></div>`;
            });
            results.innerHTML = html + '</div>';
        } catch { results.innerHTML = '<p class="empty-hint">生成失败，请重试</p>'; }
    }

    async function generateCharacterSetting() {
        const genre = document.getElementById('charSettingGenre').value;
        const gender = document.querySelector('input[name="charSettingGender"]:checked').value;
        const useAI = document.getElementById('charSettingAI').checked;
        const results = document.getElementById('charSettingResults');
        showLoading(results);
        try {
            const data = await apiPost('/api/generate/character-setting', { genre, gender, use_ai: useAI });
            let html = sourceBadge(data.source);
            if (typeof data.setting === 'string') {
                html += `<div class="char-card"><div class="char-card-body"><div class="char-field"><div class="char-field-value">${data.setting.replace(/\n/g, '<br>')}</div></div></div></div>`;
            } else {
                const s = data.setting;
                const initial = s.name ? s.name.charAt(s.name.length - 1) : '?';
                html += `
                <div class="char-card">
                    <div class="char-card-header">
                        <div class="char-avatar">${initial}</div>
                        <div><div class="char-name">${s.name}</div><div class="char-gender">${s.gender} · ${genre}</div></div>
                    </div>
                    <div class="char-card-body">
                        <div class="char-field"><div class="char-field-label">性格特征</div><div class="char-field-value">${s.personality}</div></div>
                        <div class="char-field"><div class="char-field-label">身世背景</div><div class="char-field-value">${s.background}</div></div>
                        <div class="char-field"><div class="char-field-label">能力特长</div><div class="char-field-value">${s.abilities}</div></div>
                        <div class="char-field"><div class="char-field-label">外貌描述</div><div class="char-field-value">${s.appearance}</div></div>
                    </div>
                </div>`;
            }
            results.innerHTML = html;
        } catch { results.innerHTML = '<p class="empty-hint">生成失败，请重试</p>'; }
    }

    async function generateBackground() {
        const genre = document.getElementById('bgGenre').value;
        const useAI = document.getElementById('bgAI').checked;
        const results = document.getElementById('bgResults');
        showLoading(results);
        try {
            const data = await apiPost('/api/generate/background', { genre, use_ai: useAI });
            let html = sourceBadge(data.source);
            if (typeof data.setting === 'string') {
                html += `<div class="world-section full-width"><div class="world-section-text">${data.setting.replace(/\n/g, '<br>')}</div></div>`;
            } else {
                const s = data.setting;
                html += `<div class="world-card">
                    <div class="world-section"><div class="world-section-title">世界描述</div><div class="world-section-text">${s.world_description}</div></div>
                    <div class="world-section"><div class="world-section-title">力量体系</div><div class="world-section-text">${s.power_system}</div></div>
                    <div class="world-section"><div class="world-section-title">势力格局</div><div class="world-section-text">${s.factions}</div></div>
                    <div class="world-section"><div class="world-section-title">地理环境</div><div class="world-section-text">${s.geography}</div></div>
                </div>`;
            }
            results.innerHTML = html;
        } catch { results.innerHTML = '<p class="empty-hint">生成失败，请重试</p>'; }
    }

    async function generateNovelName() {
        const genre = document.getElementById('novelNameGenre').value;
        const count = parseInt(document.getElementById('novelNameCount').value);
        const useAI = document.getElementById('novelNameAI').checked;
        const results = document.getElementById('novelNameResults');
        showLoading(results);
        try {
            const data = await apiPost('/api/generate/novel-name', { genre, count, use_ai: useAI });
            let html = sourceBadge(data.source) + '<div class="name-tag-list">';
            data.names.forEach(name => {
                html += `<div class="name-tag" onclick="copyText('${name}')">《${name}》<span class="copy-hint">点击复制</span></div>`;
            });
            results.innerHTML = html + '</div>';
        } catch { results.innerHTML = '<p class="empty-hint">生成失败，请重试</p>'; }
    }

    async function generateCover() {
        const title = document.getElementById('coverTitle').value.trim();
        const author = document.getElementById('coverAuthor').value.trim();
        const genre = document.getElementById('coverGenre').value;
        if (!title) { showToast('请输入书名'); return; }
        const results = document.getElementById('coverResults');
        showLoading(results);
        try {
            const data = await apiPost('/api/generate/cover', { title, author, genre });
            const canvas = document.getElementById('coverCanvas');
            results.innerHTML = '';
            results.appendChild(canvas);
            canvas.style.display = 'block';
            drawCover(canvas, data.cover);
            document.getElementById('downloadCoverBtn').style.display = 'block';
        } catch { results.innerHTML = '<p class="empty-hint">生成失败，请重试</p>'; }
    }

    function drawCover(canvas, cover) {
        const ctx = canvas.getContext('2d');
        const w = canvas.width, h = canvas.height;
        const gradient = ctx.createLinearGradient(0, 0, w, h);
        gradient.addColorStop(0, cover.bg_color);
        gradient.addColorStop(1, _shiftColor(cover.bg_color, 30));
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, w, h);
        _drawDecorations(ctx, w, h, cover);
        ctx.fillStyle = cover.accent_color; ctx.globalAlpha = 0.1;
        ctx.fillRect(0, h * 0.3, w, h * 0.4); ctx.globalAlpha = 1;
        ctx.fillStyle = cover.accent_color;
        ctx.fillRect(w * 0.1, h * 0.32, w * 0.8, 2);
        ctx.fillRect(w * 0.1, h * 0.68, w * 0.8, 2);
        ctx.fillStyle = '#ffffff'; ctx.textAlign = 'center';
        const ts = cover.title.length <= 4 ? 72 : cover.title.length <= 8 ? 56 : 42;
        ctx.font = `bold ${ts}px "PingFang SC","Microsoft YaHei",serif`;
        if (cover.title.length > 8) {
            const mid = Math.ceil(cover.title.length / 2);
            ctx.fillText(cover.title.slice(0, mid), w/2, h*0.47);
            ctx.fillText(cover.title.slice(mid), w/2, h*0.47 + ts + 10);
        } else { ctx.fillText(cover.title, w/2, h*0.52); }
        ctx.font = '20px "PingFang SC","Microsoft YaHei",sans-serif';
        ctx.fillStyle = cover.accent_color;
        ctx.fillText(cover.author, w/2, h*0.76);
        ctx.font = '16px "PingFang SC","Microsoft YaHei",sans-serif';
        ctx.fillStyle = 'rgba(255,255,255,0.4)';
        ctx.fillText(cover.genre + ' · 小说', w/2, h*0.92);
    }

    function _drawDecorations(ctx, w, h, cover) {
        ctx.save(); ctx.globalAlpha = 0.08; ctx.strokeStyle = cover.accent_color; ctx.lineWidth = 1;
        if (['cloud','flower'].includes(cover.element)) {
            for (let i = 0; i < 6; i++) { const x = Math.random()*w, y = Math.random()*h*0.25; _cloud(ctx,x,y,40+Math.random()*60); }
            for (let i = 0; i < 4; i++) { const x = Math.random()*w, y = h*0.75+Math.random()*h*0.2; _cloud(ctx,x,y,30+Math.random()*50); }
        }
        if (['star','circuit'].includes(cover.element)) {
            ctx.globalAlpha = 0.05; ctx.fillStyle = cover.accent_color;
            for (let i = 0; i < 80; i++) { ctx.beginPath(); ctx.arc(Math.random()*w, Math.random()*h, Math.random()*2, 0, Math.PI*2); ctx.fill(); }
        }
        if (['mountain','bamboo'].includes(cover.element)) { ctx.globalAlpha = 0.06; ctx.fillStyle = cover.accent_color; _mountains(ctx,w,h); }
        if (['sword','lightning'].includes(cover.element)) {
            ctx.globalAlpha = 0.06; ctx.strokeStyle = cover.accent_color; ctx.lineWidth = 2;
            ctx.beginPath(); ctx.moveTo(w*0.5,h*0.05); ctx.lineTo(w*0.5,h*0.28); ctx.stroke();
            ctx.beginPath(); ctx.moveTo(w*0.42,h*0.2); ctx.lineTo(w*0.58,h*0.2); ctx.stroke();
        }
        if (['grid','ring'].includes(cover.element)) { ctx.globalAlpha = 0.04; ctx.strokeStyle = cover.accent_color; for (let i=0;i<10;i++){ctx.beginPath();ctx.arc(w/2,h/2,50+i*40,0,Math.PI*2);ctx.stroke();} }
        if (['moon','fan'].includes(cover.element)) {
            ctx.globalAlpha = 0.06; ctx.fillStyle = cover.accent_color; ctx.beginPath(); ctx.arc(w*0.75,h*0.15,50,0,Math.PI*2); ctx.fill();
            ctx.fillStyle = cover.bg_color; ctx.beginPath(); ctx.arc(w*0.78,h*0.13,45,0,Math.PI*2); ctx.fill();
        }
        ctx.restore();
    }
    function _cloud(ctx,x,y,s){ctx.beginPath();ctx.arc(x,y,s*0.5,0,Math.PI*2);ctx.arc(x+s*0.35,y-s*0.1,s*0.35,0,Math.PI*2);ctx.arc(x+s*0.6,y,s*0.3,0,Math.PI*2);ctx.stroke();}
    function _mountains(ctx,w,h){ctx.beginPath();ctx.moveTo(0,h*0.85);[0.15,0.3,0.5,0.7,0.85].forEach(p=>{ctx.lineTo(w*p,h*(0.7+Math.random()*0.1));ctx.lineTo(w*(p+0.07),h*0.85);});ctx.lineTo(w,h*0.85);ctx.lineTo(w,h);ctx.lineTo(0,h);ctx.closePath();ctx.fill();}
    function _shiftColor(hex,amt){let r=parseInt(hex.slice(1,3),16),g=parseInt(hex.slice(3,5),16),b=parseInt(hex.slice(5,7),16);return `rgb(${Math.min(255,r+amt)},${Math.min(255,g+amt)},${Math.min(255,b+amt)})`;}

    function downloadCover() {
        const canvas = document.getElementById('coverCanvas');
        const link = document.createElement('a');
        link.download = '小说封面.png';
        link.href = canvas.toDataURL('image/png');
        link.click();
        showToast('封面已下载');
    }

    return { generateCharacterName, generateCharacterSetting, generateBackground, generateNovelName, generateCover, downloadCover };
})();


// ─── Novel Analysis & Imitation ──────────────────────────────────────
const NovelAnalysis = (() => {
    let selectedNovelId = null;

    function init() {
        const zone = document.getElementById('uploadZone');
        const input = document.getElementById('fileInput');

        zone.addEventListener('click', () => input.click());
        zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('drag-over'); });
        zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
        zone.addEventListener('drop', e => {
            e.preventDefault();
            zone.classList.remove('drag-over');
            if (e.dataTransfer.files.length) uploadFile(e.dataTransfer.files[0]);
        });
        input.addEventListener('change', () => { if (input.files.length) uploadFile(input.files[0]); input.value = ''; });

        loadNovels();
    }

    async function uploadFile(file) {
        const zone = document.getElementById('uploadZone');
        zone.innerHTML = '<div class="loading"><div class="spinner"></div>上传解析中...</div>';

        const fd = new FormData();
        fd.append('file', file);
        fd.append('title', file.name.replace(/\.[^.]+$/, ''));

        try {
            const res = await fetch('/api/novels/upload', { method: 'POST', body: fd });
            const data = await res.json();
            if (data.error) {
                showToast(data.error);
            } else {
                showToast(`上传成功：${data.title}（${data.word_count} 字）`);
                loadNovels();
                selectNovel(data.id);
            }
        } catch {
            showToast('上传失败');
        }

        zone.innerHTML = '<div class="upload-icon">📄</div><div class="upload-text">点击或拖拽上传小说文件</div><div class="upload-hint">支持 PDF、DOCX、TXT 格式</div>';
    }

    async function loadNovels() {
        try {
            const novels = await (await fetch('/api/novels')).json();
            const list = document.getElementById('novelList');
            if (!novels.length) {
                list.innerHTML = '<p class="empty-hint" style="padding:16px">尚未上传任何小说</p>';
                return;
            }
            list.innerHTML = novels.map(n => `
                <div class="novel-item ${n.id === selectedNovelId ? 'active' : ''}" onclick="NovelAnalysis.selectNovel(${n.id})">
                    <div class="novel-item-info">
                        <div class="novel-item-title">📖 ${_esc(n.title)}</div>
                        <div class="novel-item-meta">${n.word_count} 字 ${n.analysis ? '· ✅ 已分析' : ''}</div>
                    </div>
                    <button class="btn-danger" onclick="event.stopPropagation();NovelAnalysis.deleteNovel(${n.id})" title="删除">✕</button>
                </div>
            `).join('');
        } catch {}
    }

    async function selectNovel(id) {
        selectedNovelId = id;
        document.getElementById('imitateBtn').disabled = false;
        loadNovels();

        const results = document.getElementById('analysisResults');
        results.innerHTML = '<div class="loading"><div class="spinner"></div>分析中...</div>';

        try {
            const res = await fetch(`/api/novels/${id}/analyze`, { method: 'POST' });
            const analysis = await res.json();
            renderAnalysis(analysis);
        } catch {
            results.innerHTML = '<p class="empty-hint">分析失败，请重试</p>';
        }
    }

    function renderAnalysis(a) {
        const results = document.getElementById('analysisResults');
        let html = '<div style="margin-bottom:24px">';

        // Stats grid
        html += '<div class="stats-grid">';
        const stats = [
            [a.char_count, '总字数'], [a.word_count, '词汇量'],
            [a.sentence_count, '句子数'], [a.paragraph_count, '段落数'],
            [a.avg_sentence_len, '平均句长'], [a.unique_words, '独立词汇'],
            [(a.vocabulary_richness * 100).toFixed(1) + '%', '词汇丰富度'],
            [(a.dialogue_ratio * 100).toFixed(1) + '%', '对话占比'],
        ];
        stats.forEach(([v, l]) => {
            html += `<div class="stat-card"><div class="stat-value">${v}</div><div class="stat-label">${l}</div></div>`;
        });
        html += '</div>';

        // Style tags
        if (a.style_tags && a.style_tags.length) {
            html += '<div style="margin-bottom:16px"><div style="font-size:13px;font-weight:700;color:var(--text-secondary);margin-bottom:8px">写作风格标签</div>';
            html += '<div class="style-tags">';
            a.style_tags.forEach(t => { html += `<span class="style-tag">${t}</span>`; });
            html += '</div></div>';
        }

        // Top words
        if (a.top_words && a.top_words.length) {
            html += '<div><div style="font-size:13px;font-weight:700;color:var(--text-secondary);margin-bottom:8px">高频词汇 TOP 30</div>';
            html += '<div class="word-cloud">';
            a.top_words.forEach(([w, c]) => {
                html += `<span class="word-item">${w}<span class="word-count">×${c}</span></span>`;
            });
            html += '</div></div>';
        }

        html += '</div>';

        // Imitation output placeholder
        html += '<div id="imitationOutput"></div>';

        results.innerHTML = html;
    }

    async function imitate() {
        if (!selectedNovelId) { showToast('请先选择一本小说'); return; }

        const output = document.getElementById('imitationOutput') || document.getElementById('analysisResults');
        const prevContent = output.id === 'imitationOutput' ? '' : output.innerHTML;

        const targetEl = document.getElementById('imitationOutput');
        if (targetEl) {
            targetEl.innerHTML = '<div class="loading"><div class="spinner"></div>仿写生成中，请稍候...</div>';
        }

        try {
            const res = await fetch(`/api/novels/${selectedNovelId}/imitate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    target_length: parseInt(document.getElementById('imitateLength').value) || 1000,
                    chapters: parseInt(document.getElementById('imitateChapters').value) || 1,
                    scope: document.getElementById('imitateScope').value,
                    use_ai: document.getElementById('imitateAI').checked,
                }),
            });
            const data = await res.json();

            let html = '<div style="margin-top:20px;padding-top:20px;border-top:1.5px solid var(--border-light)">';
            html += '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">';
            html += '<div style="font-size:15px;font-weight:700">✍️ 仿写结果</div>';
            const badge = data.source === 'ai' ? '<span class="source-badge ai">🤖 AI 生成</span>' : '<span class="source-badge template">🎲 马尔可夫链生成</span>';
            html += badge + '</div>';
            html += `<div class="imitation-output">${_esc(data.text)}</div>`;
            html += `<button class="btn-secondary" onclick="copyText(document.querySelector('.imitation-output').textContent)">📋 复制全文</button>`;
            html += '</div>';

            if (targetEl) targetEl.innerHTML = html;
        } catch {
            if (targetEl) targetEl.innerHTML = '<p class="empty-hint">仿写失败，请重试</p>';
        }
    }

    async function deleteNovel(id) {
        try {
            await fetch(`/api/novels/${id}`, { method: 'DELETE' });
            if (selectedNovelId === id) {
                selectedNovelId = null;
                document.getElementById('imitateBtn').disabled = true;
                document.getElementById('analysisResults').innerHTML = '<p class="empty-hint">上传小说文件后，选择一本小说开始分析 📚</p>';
            }
            loadNovels();
            showToast('已删除');
        } catch {}
    }

    function _esc(s) {
        const d = document.createElement('div');
        d.textContent = s;
        return d.innerHTML;
    }

    document.addEventListener('DOMContentLoaded', init);

    return { selectNovel, imitate, deleteNovel };
})();
