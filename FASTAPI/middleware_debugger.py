from fastapi import FastAPI
from middleware_debugger import DebugAuthMiddleware

app = FastAPI()

app.add_middleware(DebugAuthMiddleware)
