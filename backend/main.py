import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from auth.router import router as auth_router
from config import settings
from logging_config import setup_logging
from me.router import router as me_router
from movies.router import router as movies_router
from people.router import router as people_router
from search.router import router as search_router
from tv.router import router as tv_router
from watchlist.router import router as watchlist_router

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Marquee API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (time.perf_counter() - start) * 1000
        logger.exception(f"{request.method} {request.url.path} raised an unhandled exception after {duration_ms:.0f}ms")
        raise

    duration_ms = (time.perf_counter() - start) * 1000
    log = logger.warning if response.status_code >= 500 else logger.info
    log(f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms:.0f}ms)")
    return response


app.include_router(auth_router, prefix="/api/v1")
app.include_router(movies_router, prefix="/api/v1")
app.include_router(people_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")
app.include_router(tv_router, prefix="/api/v1")
app.include_router(watchlist_router, prefix="/api/v1")
app.include_router(me_router, prefix="/api/v1")


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}
