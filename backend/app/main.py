from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Load .env file if present (no-op when not found or python-dotenv not installed)
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv(override=True)
except ImportError:
    pass

from app.config import settings
from app.logging_config import configure_logging
from app.middleware import CorrelationIDMiddleware
from app.routers import api, health, nl

configure_logging(settings.LOG_LEVEL)

app = FastAPI(
    title="NL Security Control",
    version="1.0.0",
    description=(
        "Natural Language Security System Control API.\n\n"
        "Send free-text commands to `/nl/execute` — the system interprets them "
        "and dispatches to the appropriate security endpoint automatically.\n\n"
        "Interactive docs: `/docs` (Swagger UI) · `/redoc` (ReDoc)"
    ),
    openapi_tags=[
        {"name": "NL", "description": "Natural language command processing"},
        {"name": "Security API", "description": "Direct security system control endpoints"},
        {"name": "Health", "description": "Service health and status"},
    ],
)

# Middleware (order matters: CORS first, then correlation ID)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Correlation-ID"],
)
app.add_middleware(CorrelationIDMiddleware)

# Routers
app.include_router(health.router)
app.include_router(nl.router)
app.include_router(api.router, prefix="/api")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "ok": False,
            "error": "internal_server_error",
            "detail": str(exc),
        },
    )
