from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.db import init_db
from app.routes import chat, document, tools, auth
from app.config import settings
from app.services.rate_limit_service import rate_limiter
import os

# Initialize DB tables
init_db()

app = FastAPI(
    title="BharatAI Backend API",
    description="Backend services for BharatAI - Chat, Search, PDF processing, Translation, and Grammar check.",
    version="1.0.0"
)

# Ensure storage directory exists
os.makedirs(settings.STORAGE_DIR, exist_ok=True)

# Mount static folder to serve generated files
app.mount("/storage", StaticFiles(directory=settings.STORAGE_DIR), name="storage")

# CORS configurations
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://192.168.1.18:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

cors_kwargs = {
    "allow_origins": origins,
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}
if settings.CORS_ORIGIN_REGEX:
    cors_kwargs["allow_origin_regex"] = settings.CORS_ORIGIN_REGEX

app.add_middleware(
    CORSMiddleware,
    **cors_kwargs
)

RATE_LIMITED_PREFIXES = (
    "/api/chat",
    "/api/documents/upload",
    "/api/tools/translate",
    "/api/tools/grammar-fix",
)


@app.middleware("http")
async def public_beta_rate_limit(request: Request, call_next):
    if request.url.path.startswith(RATE_LIMITED_PREFIXES):
        forwarded_for = request.headers.get("x-forwarded-for", "")
        client_ip = forwarded_for.split(",")[0].strip() if forwarded_for else None
        key = client_ip or (request.client.host if request.client else "unknown")
        allowed, remaining = rate_limiter.allow(
            key=f"{key}:{request.url.path}",
            limit=settings.FREE_REQUESTS_PER_DAY,
            window_seconds=24 * 60 * 60,
        )
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": f"Daily free beta limit reached ({settings.FREE_REQUESTS_PER_DAY} requests). Please try again tomorrow."
                },
                headers={"X-RateLimit-Remaining": "0"},
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response

    return await call_next(request)

# Register routers
app.include_router(auth.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(document.router, prefix="/api")
app.include_router(tools.router, prefix="/api")

@app.get("/api/health")
def health_check():
    """Simple API health check endpoint."""
    return {
        "status": "healthy",
        "app": "BharatAI Backend",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
