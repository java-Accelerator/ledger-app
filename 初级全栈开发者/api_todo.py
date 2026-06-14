import sqlite3
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

conn = sqlite3.connect("todo.db", check_same_thread=False)
cur = conn.cursor()

# 建表（只执行一次）
cur.execute("""
    CREATE TABLE IF NOT EXISTS todos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT NOT NULL,
        done INTEGER DEFAULT 0
    )
""")
conn.commit()

class TodoItem(BaseModel):
    task: str

# 1. 查询全部
@app.get("/todos")
def get_todos():
    rows = cur.execute("SELECT id, task, done FROM todos ORDER BY id").fetchall()
    result = []
    for r in rows:
        result.append({"id": r[0], "task": r[1], "done": bool(r[2])})
    return result

# 2. 新增
@app.post("/todos")
def add_todo(item: TodoItem):
    cur.execute("INSERT INTO todos (task) VALUES (?)", (item.task,))
    conn.commit()
    return {"id": cur.lastrowid, "task": item.task, "done": False}

# 3. 标记完成/取消
@app.put("/todos/{todo_id}")
def toggle_done(todo_id: int):
    cur.execute("SELECT done FROM todos WHERE id = ?", (todo_id,))
    row = cur.fetchone()
    if not row:
        return {"error": "记录不存在"}
    new_done = 1 if row[0] == 0 else 0
    cur.execute("UPDATE todos SET done = ? WHERE id = ?", (new_done, todo_id))
    conn.commit()
    return {"id": todo_id, "done": bool(new_done)}

# 4. 删除
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    cur.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    if cur.rowcount == 0:
        return {"error": "记录不存在"}
    return {"deleted": todo_id}
