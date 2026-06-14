# Study

这是一个从 Python 基础到中级全栈工程师能力建设的学习仓库。

当前重点项目是个人记账 Web 应用：先用 Python、FastAPI、Flask、SQLite 和原生前端完成完整功能，再逐步升级到 React、PostgreSQL、Docker、监控和工程化部署。

## 目录结构

```text
Study/
├── 初级全栈开发者/    # Python、Web 基础和记账应用旧版实现
├── 中级工程师/        # React 重写、工程化和进阶学习计划
├── 当前状态.md        # 当前学习状态和项目备忘
└── README.md          # 仓库说明
```

## 当前主项目

个人记账 Web 应用，支持：

- 注册和登录
- 新增收入、支出记录
- 按收入或支出筛选
- 删除记录
- 本月收入、支出、结余统计
- 收入和支出分类条形图
- 多用户数据隔离

## 技术栈

初级版本：

- Python
- FastAPI
- Flask
- SQLite
- HTML / CSS / JavaScript
- pytest

进阶版本：

- React
- Vite
- Axios
- 后续计划：PostgreSQL、Docker、GitHub Actions、Sentry

## 本地运行

启动后端：

```powershell
cd F:\Desktop\Study\初级全栈开发者
python -m uvicorn api_ledger:app --reload --port 8000 --no-use-colors
```

启动 React 前端：

```powershell
cd F:\Desktop\Study\中级工程师\ledger-react
npm run dev
```

访问：

```text
http://127.0.0.1:5175/
```

## 测试

```powershell
cd F:\Desktop\Study\初级全栈开发者
$env:LEDGER_DB='test_ledger.db'
pytest test_api_ledger.py -v
```

## 学习目标

从“能独立完成功能”逐步升级到：

- 能拆分前后端项目结构
- 能写可维护的组件化前端
- 能设计更稳定的数据库结构
- 能使用 Git 管理开发流程
- 能用 Docker 和 CI 改善交付
- 能定位线上错误和性能问题
