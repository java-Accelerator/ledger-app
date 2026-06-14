# PythonAnywhere WSGI 入口：把 FastAPI (ASGI) 转为 WSGI
from a2wsgi import ASGIMiddleware
from api_ledger import app

application = ASGIMiddleware(app)
