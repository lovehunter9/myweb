// ─── Scientific Calculator ───────────────────────────────────────────
const Calculator = (() => {
    let expression = '';
    let angleMode = 'deg';
    let lastResult = null;

    const exprEl = () => document.getElementById('calcExpression');
    const resultEl = () => document.getElementById('calcResult');

    function updateDisplay() {
        exprEl().textContent = expression || '';
        if (expression === '') {
            resultEl().textContent = lastResult !== null ? lastResult : '0';
        }
    }

    function input(val) {
        if (lastResult !== null && !isNaN(val) && expression === '') {
            expression = '';
            lastResult = null;
        }
        expression += val;
        updateDisplay();
        liveEvaluate();
    }

    function liveEvaluate() {
        try {
            const result = compute(expression);
            if (result !== undefined && !isNaN(result) && isFinite(result)) {
                resultEl().textContent = formatNumber(result);
            }
        } catch (_) {}
    }

    function backspace() {
        expression = expression.slice(0, -1);
        updateDisplay();
        if (expression) liveEvaluate();
        else resultEl().textContent = lastResult !== null ? lastResult : '0';
    }

    function clear() {
        expression = '';
        lastResult = null;
        exprEl().textContent = '';
        resultEl().textContent = '0';
    }

    function evaluate() {
        if (!expression) return;
        try {
            const result = compute(expression);
            const formatted = formatNumber(result);
            exprEl().textContent = expression + ' =';
            resultEl().textContent = formatted;

            saveToHistory(expression, formatted);
            lastResult = formatted;
            expression = '';
        } catch (err) {
            resultEl().textContent = '错误';
            setTimeout(() => { resultEl().textContent = '0'; }, 1500);
            expression = '';
        }
    }

    function compute(expr) {
        let processed = expr
            .replace(/ln\(/g, 'log(')
            .replace(/log\(/g, 'log10(');

        if (angleMode === 'deg') {
            processed = processed
                .replace(/sin\(/g, 'sin(pi/180*')
                .replace(/cos\(/g, 'cos(pi/180*')
                .replace(/tan\(/g, 'tan(pi/180*')
                .replace(/asin\(/g, '(180/pi)*asin(')
                .replace(/acos\(/g, '(180/pi)*acos(')
                .replace(/atan\(/g, '(180/pi)*atan(');
        }

        return math.evaluate(processed);
    }

    function formatNumber(num) {
        if (typeof num === 'object') return math.format(num, { precision: 10 });
        if (Number.isInteger(num)) return num.toString();
        const str = num.toPrecision(12);
        return parseFloat(str).toString();
    }

    function setAngleMode(mode) {
        angleMode = mode;
        document.getElementById('degBtn').classList.toggle('active', mode === 'deg');
        document.getElementById('radBtn').classList.toggle('active', mode === 'rad');
    }

    // ─── History ─────────────────────────────────────────────────────
    function saveToHistory(expr, result) {
        fetch('/api/calculator/history', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ expression: expr, result: result }),
        }).then(() => loadHistory());
    }

    function loadHistory() {
        fetch('/api/calculator/history')
            .then(r => r.json())
            .then(items => {
                const list = document.getElementById('calcHistoryList');
                if (!items.length) {
                    list.innerHTML = '<p class="empty-hint">暂无历史记录</p>';
                    return;
                }
                list.innerHTML = items.map(item => `
                    <div class="history-item" onclick="Calculator.useHistory('${item.expression.replace(/'/g, "\\'")}')">
                        <div class="history-expr">${escapeHtml(item.expression)}</div>
                        <div class="history-val">${escapeHtml(item.result)}</div>
                    </div>
                `).join('');
            });
    }

    function useHistory(expr) {
        expression = expr;
        updateDisplay();
        liveEvaluate();
    }

    function clearHistory() {
        fetch('/api/calculator/history', { method: 'DELETE' })
            .then(() => {
                document.getElementById('calcHistoryList').innerHTML =
                    '<p class="empty-hint">暂无历史记录</p>';
                showToast('历史记录已清空');
            });
    }

    // Keyboard support
    document.addEventListener('keydown', (e) => {
        const calcPage = document.getElementById('page-calculator');
        if (!calcPage.classList.contains('active')) return;

        const key = e.key;
        if (/[0-9.+\-*/%^()]/.test(key)) {
            e.preventDefault();
            input(key);
        } else if (key === 'Enter' || key === '=') {
            e.preventDefault();
            evaluate();
        } else if (key === 'Backspace') {
            e.preventDefault();
            backspace();
        } else if (key === 'Escape' || key === 'Delete') {
            e.preventDefault();
            clear();
        }
    });

    // Load history on page load
    document.addEventListener('DOMContentLoaded', loadHistory);

    return {
        input, backspace, clear, evaluate,
        setAngleMode, clearHistory, useHistory, loadHistory,
    };
})();

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
