from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.router import router as auth_router
from config import settings
from me.router import router as me_router
from movies.router import router as movies_router
from people.router import router as people_router
from search.router import router as search_router
from watchlist.router import router as watchlist_router

app = FastAPI(title="Marquee API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(movies_router, prefix="/api/v1")
app.include_router(people_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")
app.include_router(watchlist_router, prefix="/api/v1")
app.include_router(me_router, prefix="/api/v1")


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}
