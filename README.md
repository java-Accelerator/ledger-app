# 个人记账 Web 应用

一个前后端分离的个人记账工具，Python + FastAPI 后端，纯 HTML/CSS/JS 前端，SQLite 数据库。

## 功能

- 新增收入 / 支出记录
- 按收入/支出筛选
- 删除记录
- 本月收支统计
- 支出分类条形图
- 数据持久化存储（SQLite）

## 技术栈

| 层 | 技术 |
|----|------|
| 后端 | Python · FastAPI · SQLite |
| 前端 | HTML · CSS · JavaScript |
| 测试 | pytest · httpx |

## 快速启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动后端
python -m uvicorn api_ledger:app --reload --port 8000

# 3. 浏览器打开 web_ledger.html
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /records | 新增记录 |
| GET | /records | 查询全部（支持 ?type=收入 筛选） |
| DELETE | /records/{id} | 删除记录 |
| GET | /records/stats | 本月统计 + 分类汇总 |

## 运行测试

```bash
pytest test_api_ledger.py -v
```

## 项目结构

```
├── api_ledger.py          # 后端 API
├── web_ledger.html        # 前端页面
├── test_api_ledger.py     # 接口测试
├── requirements.txt       # 依赖列表
├── ledger.db              # SQLite 数据库（运行后生成）
└── README.md
```
