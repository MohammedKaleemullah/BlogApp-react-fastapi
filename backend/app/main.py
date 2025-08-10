from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
import logging
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from app.routers import upload_router
from fastapi.staticfiles import StaticFiles

from app.routers import user_router, blog_router, auth_router
from app.middleware.logging_middleware import LoggingMiddleware

app = FastAPI(title="Blog App API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger("uvicorn.access")
logging.basicConfig(level=logging.INFO)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"Request: {request.method} {request.url}")
        response = await call_next(request)
        logger.info(f"Response Status: {response.status_code}")
        return response

app.add_middleware(LoggingMiddleware)

class TraceIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = str(uuid.uuid4())
        request.state.trace_id = trace_id
        response = await call_next(request)
        response.headers["X-Trace-Id"] = trace_id
        return response

app.add_middleware(TraceIdMiddleware)

app.include_router(user_router.router)
app.include_router(blog_router.router)
app.include_router(auth_router.router)
app.include_router(upload_router.router)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.add_middleware(LoggingMiddleware)

@app.get("/")
def root():
    return {"message": "Welcome to Blog App API"}



