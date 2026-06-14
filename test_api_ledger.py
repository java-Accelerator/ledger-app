import os, sys

# 必须在导入 api_ledger 之前设置，让它用测试数据库
os.environ["LEDGER_DB"] = "test_ledger.db"
if os.path.exists("test_ledger.db"):
    os.remove("test_ledger.db")

from fastapi.testclient import TestClient
from api_ledger import app
import pytest

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup() -> dict:
    """每个测试前：删库 → 重建 → 注册测试用户 → 返回 token"""
    # 删掉旧测试库
    if os.path.exists("test_ledger.db"):
        os.remove("test_ledger.db")

    # 重新建表
    from api_ledger import init_db
    init_db()

    # 注册测试用户
    res = client.post("/register", json={"username": "tester", "password": "123456"})
    data = res.json()
    assert data["ok"], f"注册失败: {data}"
    return {"token": data["token"]}

def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}

# ========== 注册登录测试（新） ==========

def test_register_ok(setup):
    """注册：用户名和密码合法"""
    res = client.post("/register", json={"username": "user1", "password": "abcd1234"})
    assert res.json()["ok"] is True
    assert "token" in res.json()

def test_register_duplicate(setup):
    """重复注册：用户名已存在"""
    res = client.post("/register", json={"username": "tester", "password": "123456"})
    assert res.json()["ok"] is False
    assert "已存在" in res.json()["error"]

def test_login_ok(setup):
    """登录：密码正确"""
    res = client.post("/login", json={"username": "tester", "password": "123456"})
    assert res.json()["ok"] is True

def test_login_wrong_password(setup):
    """登录：密码错误"""
    res = client.post("/login", json={"username": "tester", "password": "wrong"})
    assert res.json()["ok"] is False

# ========== 数据接口测试（修复版，带 token） ==========

def test_add_record(setup):
    token = setup["token"]
    res = client.post("/records",
        json={"date": "2026-06-14", "type": "支出", "tag": "餐饮", "item": "午餐", "amount": 35.5},
        headers=auth_headers(token),
    )
    assert res.status_code == 200
    data = res.json()
    assert data["amount"] == 35.5
    assert "id" in data

def test_get_all_records(setup):
    token = setup["token"]
    client.post("/records",
        json={"date": "2026-06-14", "type": "支出", "tag": "餐饮", "item": "午餐", "amount": 20},
        headers=auth_headers(token),
    )
    client.post("/records",
        json={"date": "2026-06-14", "type": "收入", "tag": "工资", "item": "6月", "amount": 5000},
        headers=auth_headers(token),
    )
    res = client.get("/records", headers=auth_headers(token))
    assert res.status_code == 200
    assert len(res.json()) == 2

def test_filter_by_type(setup):
    token = setup["token"]
    client.post("/records",
        json={"date": "2026-06-14", "type": "收入", "tag": "工资", "item": "6月", "amount": 5000},
        headers=auth_headers(token),
    )
    client.post("/records",
        json={"date": "2026-06-14", "type": "支出", "tag": "餐饮", "item": "午餐", "amount": 20},
        headers=auth_headers(token),
    )
    res = client.get("/records?type=收入", headers=auth_headers(token))
    data = res.json()
    assert len(data) == 1
    assert data[0]["type"] == "收入"

def test_delete_record(setup):
    token = setup["token"]
    res = client.post("/records",
        json={"date": "2026-06-14", "type": "支出", "tag": "餐饮", "item": "临时", "amount": 10},
        headers=auth_headers(token),
    )
    record_id = res.json()["id"]
    client.delete(f"/records/{record_id}", headers=auth_headers(token))
    res = client.get("/records", headers=auth_headers(token))
    assert len(res.json()) == 0

def test_stats(setup):
    token = setup["token"]
    client.post("/records",
        json={"date": "2026-06-14", "type": "收入", "tag": "工资", "item": "6月", "amount": 3000},
        headers=auth_headers(token),
    )
    client.post("/records",
        json={"date": "2026-06-15", "type": "支出", "tag": "餐饮", "item": "晚餐", "amount": 80},
        headers=auth_headers(token),
    )
    res = client.get("/records/stats", headers=auth_headers(token))
    stats = res.json()
    assert stats["monthly"]["收入"] == 3000
    assert stats["monthly"]["支出"] == 80

def test_empty_records(setup):
    res = client.get("/records", headers=auth_headers(setup["token"]))
    assert res.status_code == 200
    assert res.json() == []

def test_rejected_without_token():
    """未登录：直接访问受保护接口应返回 401"""
    res = client.get("/records")
    assert res.status_code == 401
