import sqlite3, hashlib, secrets, os
from fastapi import FastAPI, Query, Header, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.environ.get("LEDGER_DB", "ledger.db")

def get_db():
    """每个请求独立连接，避免并发游标冲突"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout=5000")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
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
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            token TEXT
        )
    """)
    # 兼容旧数据
    try:
        conn.execute("SELECT user_id FROM records LIMIT 1")
    except:
        conn.execute("ALTER TABLE records ADD COLUMN user_id INTEGER DEFAULT 1")
    conn.commit()
    conn.close()

init_db()

# 提供前端页面
@app.get("/")
def serve_frontend():
    return FileResponse("web_ledger.html")

# ====== 密码工具 ======
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
    return salt + ":" + h.hex()

def verify_password(password: str, stored: str) -> bool:
    salt, h = stored.split(":")
    computed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
    return computed.hex() == h

# ====== 鉴权 ======
def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="请先登录")
    token = authorization[7:]
    db = get_db()
    try:
        row = db.execute("SELECT id, username FROM users WHERE token = ?", (token,)).fetchone()
        if not row:
            raise HTTPException(status_code=401, detail="登录已过期")
        return {"id": row[0], "username": row[1]}
    finally:
        db.close()

# ====== 数据模型 ======
class Record(BaseModel):
    date: str
    type: str
    tag: str = ""
    item: str
    amount: float

class AuthRequest(BaseModel):
    username: str
    password: str

# ====== 注册 ======
@app.post("/register")
def register(req: AuthRequest):
    if len(req.username) < 2 or len(req.password) < 4:
        return {"ok": False, "error": "用户名至少2位，密码至少4位"}
    db = get_db()
    try:
        exist = db.execute("SELECT id FROM users WHERE username = ?", (req.username,)).fetchone()
        if exist:
            return {"ok": False, "error": "用户名已存在"}
        h = hash_password(req.password)
        token = secrets.token_hex(32)
        db.execute(
            "INSERT INTO users (username, password_hash, token) VALUES (?, ?, ?)",
            (req.username, h, token),
        )
        db.commit()
        return {"ok": True, "token": token, "username": req.username}
    finally:
        db.close()

# ====== 登录 ======
@app.post("/login")
def login(req: AuthRequest):
    db = get_db()
    try:
        row = db.execute(
            "SELECT id, password_hash FROM users WHERE username = ?", (req.username,)
        ).fetchone()
        if not row or not verify_password(req.password, row[1]):
            return {"ok": False, "error": "用户名或密码错误"}
        token = secrets.token_hex(32)
        db.execute("UPDATE users SET token = ? WHERE id = ?", (token, row[0]))
        db.commit()
        return {"ok": True, "token": token, "username": req.username}
    finally:
        db.close()

# ====== 查询当前用户 ======
@app.get("/me")
def me(user: dict = Depends(get_current_user)):
    return {"username": user["username"]}

# ====== 新增 ======
@app.post("/records")
def add_record(r: Record, user: dict = Depends(get_current_user)):
    db = get_db()
    try:
        db.execute(
            "INSERT INTO records (date, type, tag, item, amount, user_id) VALUES (?, ?, ?, ?, ?, ?)",
            (r.date, r.type, r.tag, r.item, r.amount, user["id"]),
        )
        db.commit()
        return {"id": db.execute("SELECT last_insert_rowid()").fetchone()[0], **r.model_dump()}
    finally:
        db.close()

# ====== 查询 ======
@app.get("/records")
def get_records(
    type: str = Query(None),
    user: dict = Depends(get_current_user),
):
    db = get_db()
    try:
        if type and type in ("收入", "支出"):
            rows = db.execute(
                "SELECT id, date, type, tag, item, amount FROM records WHERE type = ? AND user_id = ? ORDER BY date DESC, id DESC",
                (type, user["id"]),
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT id, date, type, tag, item, amount FROM records WHERE user_id = ? ORDER BY date DESC, id DESC",
                (user["id"],),
            ).fetchall()

        result = []
        for r in rows:
            result.append({
                "id": r[0], "date": r[1], "type": r[2],
                "tag": r[3], "item": r[4], "amount": r[5],
            })
        return result
    finally:
        db.close()

# ====== 删除 ======
@app.delete("/records/{record_id}")
def delete_record(record_id: int, user: dict = Depends(get_current_user)):
    db = get_db()
    try:
        db.execute("DELETE FROM records WHERE id = ? AND user_id = ?", (record_id, user["id"]))
        db.commit()
        return {"deleted": record_id}
    finally:
        db.close()

# ====== 统计 ======
@app.get("/records/stats")
def get_stats(user: dict = Depends(get_current_user)):
    db = get_db()
    try:
        rows = db.execute("""
            SELECT type, SUM(amount) FROM records
            WHERE date >= date('now', 'start of month') AND user_id = ?
            GROUP BY type
        """, (user["id"],)).fetchall()
        monthly = {"收入": 0, "支出": 0}
        for t, s in rows:
            monthly[t] = round(s, 2)

        rows = db.execute("""
            SELECT tag, SUM(amount) FROM records
            WHERE type = '支出' AND date >= date('now', 'start of month') AND user_id = ?
            GROUP BY tag ORDER BY SUM(amount) DESC
        """, (user["id"],)).fetchall()
        tags = []
        for tag, s in rows:
            tags.append({"tag": tag if tag else "其他", "amount": round(s, 2)})

        return {"monthly": monthly, "expense_by_tag": tags}
    finally:
        db.close()

