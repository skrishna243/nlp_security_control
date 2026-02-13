import time

from fastapi import APIRouter

from app.store import store

router = APIRouter(tags=["Health"])

_START_TIME = time.time()


@router.get("/healthz")
def healthz():
    return {
        "ok": True,
        "uptime_seconds": round(time.time() - _START_TIME, 1),
        "system_state": store.get_state(),
    }
