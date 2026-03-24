from flask import Flask, render_template, request, jsonify
import database as db
import ai_engine as ai

app = Flask(__name__)


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
    history = db.get_calculations()
    return jsonify(history)


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
    ok = db.delete_calculation(calc_id)
    return jsonify({"ok": ok})


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


# ─── History ──────────────────────────────────────────────────────────

@app.route('/api/history/<item_type>', methods=['GET'])
def get_history(item_type):
    items = db.get_generated_items(item_type)
    return jsonify(items)


@app.route('/api/history/<int:item_id>', methods=['DELETE'])
def delete_history(item_id):
    ok = db.delete_generated_item(item_id)
    return jsonify({"ok": ok})


# ─── AI Status ────────────────────────────────────────────────────────

@app.route('/api/ai/status', methods=['GET'])
def ai_status():
    return jsonify(ai.check_ai_status())


if __name__ == '__main__':
    db.init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
