import os
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from config import settings
from database import init_db
from logging_config import setup_logging
from routes import router

# ── Logging bootstrap ──────────────────────────────────────────────────────────

os.makedirs("logs", exist_ok=True)
setup_logging(debug=settings.DEBUG)


# ── Lifespan ───────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("ApexAI startup — initializing database …")
    init_db()
    logger.success("Database ready ✓")
    yield
    logger.info("ApexAI shutdown complete.")


# ── App ────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description=(
        "ApexAI is a multi-agent AI system that analyzes resumes, scores candidates, "
        "predicts hiring decisions, detects skill gaps, and generates talent intelligence reports."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ───────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Middleware: Request ID ─────────────────────────────────────────────────────

@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# ── Middleware: Logging + Performance ──────────────────────────────────────────

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start = time.perf_counter()
    logger.info(
        "[{}] {} {} — start",
        getattr(request.state, "request_id", "?"),
        request.method,
        request.url.path,
    )
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "[{}] {} {} — {} ({:.1f}ms)",
        getattr(request.state, "request_id", "?"),
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.1f}"
    return response


# ── Global Exception Handler ───────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception on {} {}: {}", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "data": None,
            "meta": {"detail": str(exc)},
        },
    )


# ── Health Check ───────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "debug": settings.DEBUG,
    }


# ── API Routes ─────────────────────────────────────────────────────────────────

app.include_router(router, prefix=settings.API_PREFIX, tags=["Talent Intelligence"])


# ── Entry Point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
