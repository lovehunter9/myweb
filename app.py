import os
import tempfile
from flask import Flask, render_template, request, jsonify
import database as db
import ai_engine as ai

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}


def _allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.before_request
def ensure_db():
    db.init_db()


# ─── Pages ────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


# ─── Calculator API ──────────────────────────────────────────────────

@app.route('/api/calculator/history', methods=['GET'])
def get_calc_history():
    return jsonify(db.get_calculations())


@app.route('/api/calculator/history', methods=['POST'])
def save_calc_history():
    data = request.get_json()
    row_id = db.save_calculation(data['expression'], data['result'])
    return jsonify({"id": row_id, "ok": True})


@app.route('/api/calculator/history', methods=['DELETE'])
def clear_calc_history():
    count = db.clear_calculations()
    return jsonify({"deleted": count, "ok": True})


@app.route('/api/calculator/history/<int:calc_id>', methods=['DELETE'])
def delete_calc_entry(calc_id):
    return jsonify({"ok": db.delete_calculation(calc_id)})


# ─── Character Name Generator ────────────────────────────────────────

@app.route('/api/generate/character-name', methods=['POST'])
def gen_character_name():
    data = request.get_json()
    result = ai.generate_character_name(
        genre=data.get('genre', '仙侠'),
        gender=data.get('gender', 'male'),
        count=min(data.get('count', 5), 20),
        use_ai=data.get('use_ai', False),
    )
    db.save_generated_item('character_name', data, result)
    return jsonify(result)


# ─── Character Setting Generator ─────────────────────────────────────

@app.route('/api/generate/character-setting', methods=['POST'])
def gen_character_setting():
    data = request.get_json()
    result = ai.generate_character_setting(
        genre=data.get('genre', '仙侠'),
        gender=data.get('gender', 'male'),
        use_ai=data.get('use_ai', False),
    )
    db.save_generated_item('character_setting', data, result)
    return jsonify(result)


# ─── Background Setting Generator ────────────────────────────────────

@app.route('/api/generate/background', methods=['POST'])
def gen_background():
    data = request.get_json()
    result = ai.generate_background_setting(
        genre=data.get('genre', '仙侠'),
        use_ai=data.get('use_ai', False),
    )
    db.save_generated_item('background', data, result)
    return jsonify(result)


# ─── Novel Name Generator ────────────────────────────────────────────

@app.route('/api/generate/novel-name', methods=['POST'])
def gen_novel_name():
    data = request.get_json()
    result = ai.generate_novel_name(
        genre=data.get('genre', '仙侠'),
        count=min(data.get('count', 5), 20),
        use_ai=data.get('use_ai', False),
    )
    db.save_generated_item('novel_name', data, result)
    return jsonify(result)


# ─── Cover Generator ─────────────────────────────────────────────────

@app.route('/api/generate/cover', methods=['POST'])
def gen_cover():
    data = request.get_json()
    result = ai.generate_cover_data(
        title=data.get('title', '未命名'),
        author=data.get('author', ''),
        genre=data.get('genre', '仙侠'),
    )
    db.save_generated_item('cover', data, result)
    return jsonify(result)


# ─── Novel Upload / Analysis / Imitation ─────────────────────────────

@app.route('/api/novels', methods=['GET'])
def list_novels():
    return jsonify(db.get_novels())


@app.route('/api/novels/upload', methods=['POST'])
def upload_novel():
    if 'file' not in request.files:
        return jsonify({"error": "没有上传文件"}), 400
    f = request.files['file']
    if not f.filename or not _allowed_file(f.filename):
        return jsonify({"error": "不支持的文件格式，请上传 PDF、DOCX 或 TXT 文件"}), 400

    title = request.form.get('title', '').strip()
    if not title:
        title = os.path.splitext(f.filename)[0]

    ext = f.filename.rsplit('.', 1)[1].lower()

    try:
        if ext == 'txt':
            raw = f.read()
            for enc in ('utf-8', 'gbk', 'gb2312', 'big5', 'latin-1'):
                try:
                    content = raw.decode(enc)
                    break
                except (UnicodeDecodeError, LookupError):
                    continue
            else:
                content = raw.decode('utf-8', errors='replace')
        else:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.' + ext)
            f.save(tmp.name)
            tmp.close()
            try:
                if ext == 'pdf':
                    content = ai.parse_pdf(tmp.name)
                else:
                    content = ai.parse_docx(tmp.name)
            finally:
                os.unlink(tmp.name)

        content = content.strip()
        if not content:
            return jsonify({"error": "文件内容为空"}), 400

        word_count = len(content)
        novel_id = db.save_novel(title, f.filename, content, word_count)
        return jsonify({"id": novel_id, "title": title, "word_count": word_count, "ok": True})

    except Exception as e:
        return jsonify({"error": f"文件解析失败：{str(e)}"}), 500


@app.route('/api/novels/<int:novel_id>', methods=['GET'])
def get_novel(novel_id):
    novel = db.get_novel(novel_id)
    if not novel:
        return jsonify({"error": "小说不存在"}), 404
    return jsonify(novel)


@app.route('/api/novels/<int:novel_id>', methods=['DELETE'])
def delete_novel(novel_id):
    return jsonify({"ok": db.delete_novel(novel_id)})


@app.route('/api/novels/<int:novel_id>/analyze', methods=['POST'])
def analyze_novel(novel_id):
    novel = db.get_novel(novel_id)
    if not novel:
        return jsonify({"error": "小说不存在"}), 404

    analysis = ai.analyze_novel(novel['content'])
    db.update_novel_analysis(novel_id, analysis)
    return jsonify(analysis)


@app.route('/api/novels/<int:novel_id>/imitate', methods=['POST'])
def imitate_novel(novel_id):
    novel = db.get_novel(novel_id)
    if not novel:
        return jsonify({"error": "小说不存在"}), 404

    if not novel.get('analysis'):
        analysis = ai.analyze_novel(novel['content'])
        db.update_novel_analysis(novel_id, analysis)
    else:
        analysis = novel['analysis']

    data = request.get_json() or {}
    result = ai.imitate_novel(
        text=novel['content'],
        analysis=analysis,
        target_length=min(data.get('target_length', 1000), 10000),
        chapters=min(data.get('chapters', 1), 20),
        scope=data.get('scope', 'full'),
        use_ai=data.get('use_ai', False),
    )
    return jsonify(result)


# ─── History & AI Status ─────────────────────────────────────────────

@app.route('/api/history/<item_type>', methods=['GET'])
def get_history(item_type):
    return jsonify(db.get_generated_items(item_type))


@app.route('/api/history/<int:item_id>', methods=['DELETE'])
def delete_history(item_id):
    return jsonify({"ok": db.delete_generated_item(item_id)})


@app.route('/api/ai/status', methods=['GET'])
def ai_status():
    return jsonify(ai.check_ai_status())


if __name__ == '__main__':
    db.init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
