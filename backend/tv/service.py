import logging
from datetime import date, datetime, timezone

import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models import Genre, TvShow, TvShowCredit, TvShowGenre
from movies.service import _ensure_person_stub, _is_stale
from movies.tmdb_client import tmdb_client

logger = logging.getLogger(__name__)


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


def upsert_tv_show(db: Session, payload: dict) -> TvShow:
    tv_show = db.get(TvShow, payload["id"])
    if tv_show is None:
        tv_show = TvShow(id=payload["id"])
        db.add(tv_show)

    tv_show.title = payload.get("name") or payload.get("original_name") or ""
    tv_show.first_air_date = _parse_date(payload.get("first_air_date"))
    tv_show.number_of_seasons = payload.get("number_of_seasons")
    tv_show.number_of_episodes = payload.get("number_of_episodes")
    tv_show.vote_average = payload.get("vote_average")
    tv_show.popularity = payload.get("popularity")
    tv_show.poster_path = payload.get("poster_path")
    tv_show.backdrop_path = payload.get("backdrop_path")
    tv_show.overview = payload.get("overview")
    tv_show.raw = payload
    tv_show.synced_at = datetime.now(timezone.utc)
    db.flush()

    db.query(TvShowGenre).filter(TvShowGenre.tv_show_id == tv_show.id).delete()
    for g in payload.get("genres", []):
        if db.get(Genre, g["id"]) is None:
            db.add(Genre(id=g["id"], name=g["name"]))
        db.add(TvShowGenre(tv_show_id=tv_show.id, genre_id=g["id"]))

    cast = payload.get("credits", {}).get("cast", [])
    db.query(TvShowCredit).filter(TvShowCredit.tv_show_id == tv_show.id).delete()
    seen_person_ids: set[int] = set()
    for c in cast[:20]:
        _ensure_person_stub(db, c, seen_person_ids)
        db.add(
            TvShowCredit(
                tv_show_id=tv_show.id, person_id=c["id"], credit_type="cast",
                character=c.get("character"), cast_order=c.get("order"),
            )
        )

    db.commit()
    db.refresh(tv_show)
    return tv_show


async def get_or_sync_tv_show(db: Session, tmdb_id: int) -> TvShow:
    """Cache-on-demand with serve-stale-while-revalidate, same pattern as movies."""
    tv_show = db.get(TvShow, tmdb_id)
    if tv_show is not None and not _is_stale(tv_show.synced_at):
        logger.debug(f"TV show {tmdb_id} served from cache")
        return tv_show

    logger.info(f"TV show {tmdb_id} {'stale, refreshing' if tv_show else 'not cached, fetching'} from TMDB")
    try:
        payload = await tmdb_client.get_tv_show(tmdb_id)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            logger.info(f"TV show {tmdb_id} not found on TMDB")
            raise HTTPException(status.HTTP_404_NOT_FOUND, "TV show not found") from exc
        raise
    return upsert_tv_show(db, payload)
