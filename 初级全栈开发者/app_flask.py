import sqlite3, hashlib, secrets, os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__, static_folder=".")
CORS(app)

DB_PATH = os.environ.get("LEDGER_DB", "ledger.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=5000")
    return conn

def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            token TEXT
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            type TEXT NOT NULL,
            tag TEXT DEFAULT '',
            item TEXT NOT NULL,
            amount REAL NOT NULL,
            user_id INTEGER NOT NULL
        )
    """)
    try:
        db.execute("SELECT user_id FROM records LIMIT 1")
    except:
        db.execute("ALTER TABLE records ADD COLUMN user_id INTEGER DEFAULT 1")
    db.commit()
    db.close()

init_db()

def hash_password(password):
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
    return salt + ":" + h.hex()

def verify_password(password, stored):
    salt, h = stored.split(":")
    computed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
    return computed.hex() == h

def get_current_user():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth[7:]
    db = get_db()
    row = db.execute("SELECT id, username FROM users WHERE token = ?", (token,)).fetchone()
    db.close()
    return {"id": row["id"], "username": row["username"]} if row else None

# 首页
@app.route("/")
def index():
    return send_file("web_ledger.html")

# 注册
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "")
    if len(username) < 2 or len(password) < 4:
        return jsonify({"ok": False, "error": "用户名至少2位，密码至少4位"})
    db = get_db()
    if db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone():
        db.close()
        return jsonify({"ok": False, "error": "用户名已存在"})
    h = hash_password(password)
    token = secrets.token_hex(32)
    db.execute("INSERT INTO users (username, password_hash, token) VALUES (?, ?, ?)", (username, h, token))
    db.commit()
    db.close()
    return jsonify({"ok": True, "token": token, "username": username})

# 登录
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    db = get_db()
    row = db.execute("SELECT id, password_hash FROM users WHERE username = ?", (data.get("username", ""),)).fetchone()
    if not row or not verify_password(data.get("password", ""), row["password_hash"]):
        db.close()
        return jsonify({"ok": False, "error": "用户名或密码错误"})
    token = secrets.token_hex(32)
    db.execute("UPDATE users SET token = ? WHERE id = ?", (token, row["id"]))
    db.commit()
    db.close()
    return jsonify({"ok": True, "token": token, "username": data["username"]})

# 验证登录
@app.route("/me")
def me():
    user = get_current_user()
    if not user:
        return jsonify({"username": None}), 401
    return jsonify({"username": user["username"]})

# 新增记录
@app.route("/records", methods=["POST"])
def add_record():
    user = get_current_user()
    if not user:
        return jsonify({"error": "请先登录"}), 401
    data = request.get_json()
    db = get_db()
    db.execute(
        "INSERT INTO records (date, type, tag, item, amount, user_id) VALUES (?, ?, ?, ?, ?, ?)",
        (data["date"], data["type"], data.get("tag", ""), data.get("item", ""), data["amount"], user["id"]),
    )
    db.commit()
    rid = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    db.close()
    return jsonify({"id": rid})

# 查询记录
@app.route("/records")
def get_records():
    user = get_current_user()
    if not user:
        return jsonify([]), 401
    filter_type = request.args.get("type")
    db = get_db()
    if filter_type in ("收入", "支出"):
        rows = db.execute(
            "SELECT id, date, type, tag, item, amount FROM records WHERE type = ? AND user_id = ? ORDER BY date DESC, id DESC",
            (filter_type, user["id"]),
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT id, date, type, tag, item, amount FROM records WHERE user_id = ? ORDER BY date DESC, id DESC",
            (user["id"],),
        ).fetchall()
    result = [{"id": r[0], "date": r[1], "type": r[2], "tag": r[3], "item": r[4], "amount": r[5]} for r in rows]
    db.close()
    return jsonify(result)

# 删除记录
@app.route("/records/<int:record_id>", methods=["DELETE"])
def delete_record(record_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "请先登录"}), 401
    db = get_db()
    db.execute("DELETE FROM records WHERE id = ? AND user_id = ?", (record_id, user["id"]))
    db.commit()
    db.close()
    return jsonify({"deleted": record_id})

# 统计
@app.route("/records/stats")
def stats():
    user = get_current_user()
    if not user:
        return jsonify({
            "monthly": {"收入": 0, "支出": 0},
            "income_by_tag": [],
            "expense_by_tag": [],
        }), 401
    db = get_db()
    rows = db.execute("""
        SELECT type, SUM(amount) FROM records
        WHERE date >= date('now', 'start of month') AND user_id = ?
        GROUP BY type
    """, (user["id"],)).fetchall()
    monthly = {"收入": 0, "支出": 0}
    for r in rows:
        monthly[r[0]] = round(r[1], 2)
    rows = db.execute("""
        SELECT tag, SUM(amount) FROM records
        WHERE type = '收入' AND date >= date('now', 'start of month') AND user_id = ?
        GROUP BY tag ORDER BY SUM(amount) DESC
    """, (user["id"],)).fetchall()
    income_tags = [{"tag": r[0] if r[0] else "其他", "amount": round(r[1], 2)} for r in rows]
    rows = db.execute("""
        SELECT tag, SUM(amount) FROM records
        WHERE type = '支出' AND date >= date('now', 'start of month') AND user_id = ?
        GROUP BY tag ORDER BY SUM(amount) DESC
    """, (user["id"],)).fetchall()
    expense_tags = [{"tag": r[0] if r[0] else "其他", "amount": round(r[1], 2)} for r in rows]
    db.close()
    return jsonify({
        "monthly": monthly,
        "income_by_tag": income_tags,
        "expense_by_tag": expense_tags,
    })

if __name__ == "__main__":
    app.run()
