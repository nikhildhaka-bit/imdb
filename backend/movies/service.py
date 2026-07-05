import logging
from datetime import date, datetime, timedelta, timezone

import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from config import settings
from models import FeedCache, Genre, Movie, MovieCredit, MovieGenre, Person, Rating, WatchlistItem
from movies.schemas import MovieCardOut
from movies.tmdb_client import tmdb_client

logger = logging.getLogger(__name__)

STALE_AFTER = timedelta(days=settings.tmdb_stale_after_days)


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


def _is_stale(synced_at: datetime) -> bool:
    now = datetime.now(timezone.utc)
    synced = synced_at if synced_at.tzinfo else synced_at.replace(tzinfo=timezone.utc)
    return now - synced > STALE_AFTER


def upsert_movie(db: Session, payload: dict) -> Movie:
    movie = db.get(Movie, payload["id"])
    if movie is None:
        movie = Movie(id=payload["id"])
        db.add(movie)

    movie.media_type = "movie"
    movie.title = payload["title"]
    movie.release_date = _parse_date(payload.get("release_date"))
    movie.runtime = payload.get("runtime")
    movie.vote_average = payload.get("vote_average")
    movie.popularity = payload.get("popularity")
    movie.poster_path = payload.get("poster_path")
    movie.backdrop_path = payload.get("backdrop_path")
    movie.overview = payload.get("overview")
    movie.raw = payload
    movie.synced_at = datetime.now(timezone.utc)
    db.flush()

    # genres: promote to indexed M2M (D5)
    db.query(MovieGenre).filter(MovieGenre.movie_id == movie.id).delete()
    for g in payload.get("genres", []):
        if db.get(Genre, g["id"]) is None:
            db.add(Genre(id=g["id"], name=g["name"]))
        db.add(MovieGenre(movie_id=movie.id, genre_id=g["id"]))

    # credits: promote people to rows so filmography is a single index scan (D2)
    credits = payload.get("credits", {})
    db.query(MovieCredit).filter(MovieCredit.movie_id == movie.id).delete()
    seen_person_ids: set[int] = set()
    for c in credits.get("cast", [])[:20]:
        _ensure_person_stub(db, c, seen_person_ids)
        db.add(
            MovieCredit(
                movie_id=movie.id, person_id=c["id"], credit_type="cast", job="",
                character=c.get("character"), cast_order=c.get("order"),
            )
        )
    for c in credits.get("crew", []):
        if c.get("job") not in ("Director", "Writer", "Screenplay"):
            continue
        _ensure_person_stub(db, c, seen_person_ids)
        db.add(
            MovieCredit(
                movie_id=movie.id, person_id=c["id"], credit_type="crew", job=c["job"],
                department=c.get("department"),
            )
        )

    db.commit()
    db.refresh(movie)
    return movie


def _ensure_person_stub(db: Session, credit_payload: dict, seen_person_ids: set[int]) -> None:
    """Cheap upsert from embedded credit data — full bio/filmography synced on visit (D2).

    `seen_person_ids` tracks ids added earlier in this same (unflushed) transaction, since
    db.get() can't see pending inserts that haven't been flushed yet.
    """
    person_id = credit_payload["id"]
    if person_id in seen_person_ids:
        return
    seen_person_ids.add(person_id)
    if db.get(Person, person_id) is not None:
        return
    db.add(
        Person(
            id=person_id,
            name=credit_payload.get("name", "Unknown"),
            profile_path=credit_payload.get("profile_path"),
            known_for_department=credit_payload.get("known_for_department"),
            raw={},
            synced_at=datetime(2000, 1, 1, tzinfo=timezone.utc),  # force a real sync on first visit
        )
    )


async def get_or_sync_movie(db: Session, tmdb_id: int) -> Movie:
    """Cache-on-demand with serve-stale-while-revalidate (D4)."""
    movie = db.get(Movie, tmdb_id)
    if movie is not None and not _is_stale(movie.synced_at):
        logger.debug(f"Movie {tmdb_id} served from cache")
        return movie

    logger.info(f"Movie {tmdb_id} {'stale, refreshing' if movie else 'not cached, fetching'} from TMDB")
    try:
        payload = await tmdb_client.get_movie(tmdb_id)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            logger.info(f"Movie {tmdb_id} not found on TMDB")
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Movie not found") from exc
        raise
    return upsert_movie(db, payload)


def upsert_person(db: Session, payload: dict) -> Person:
    person = db.get(Person, payload["id"])
    if person is None:
        person = Person(id=payload["id"])
        db.add(person)

    person.name = payload["name"]
    person.profile_path = payload.get("profile_path")
    person.known_for_department = payload.get("known_for_department")
    person.raw = payload
    person.synced_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(person)
    return person


async def get_or_sync_person(db: Session, tmdb_id: int) -> Person:
    person = db.get(Person, tmdb_id)
    if person is not None and not _is_stale(person.synced_at):
        logger.debug(f"Person {tmdb_id} served from cache")
        return person

    logger.info(f"Person {tmdb_id} {'stale, refreshing' if person else 'not cached, fetching'} from TMDB")
    try:
        payload = await tmdb_client.get_person(tmdb_id)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            logger.info(f"Person {tmdb_id} not found on TMDB")
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Person not found") from exc
        raise
    return upsert_person(db, payload)


async def get_or_sync_feed(db: Session, feed_key: str) -> list[dict]:
    """Trending/popular/top_rated are cached as short-TTL ordered ID lists, separate
    from per-movie caching (D7) — they carry their own genre_ids/popularity for scoring."""
    cache = db.get(FeedCache, feed_key)
    ttl = timedelta(hours=6)
    if cache is not None and datetime.now(timezone.utc) - cache.synced_at.replace(tzinfo=timezone.utc) < ttl:
        logger.debug(f"Feed '{feed_key}' served from cache")
        return cache.movie_ids

    logger.info(f"Feed '{feed_key}' cache {'expired' if cache else 'missing'}, refreshing from TMDB")
    payload = await tmdb_client.get_feed(feed_key)
    items = payload.get("results", [])
    if cache is None:
        cache = FeedCache(feed_key=feed_key, movie_ids=items)
        db.add(cache)
    else:
        cache.movie_ids = items
        cache.synced_at = datetime.now(timezone.utc)
    db.commit()
    return items


def tmdb_item_to_card(item: dict) -> MovieCardOut:
    release_date = item.get("release_date") or ""
    return MovieCardOut(
        id=item["id"],
        title=item.get("title") or item.get("name") or "",
        year=int(release_date[:4]) if release_date[:4].isdigit() else None,
        rating=item.get("vote_average"),
        poster_path=item.get("poster_path"),
    )


def movie_to_card(movie: Movie) -> MovieCardOut:
    return MovieCardOut(
        id=movie.id,
        title=movie.title,
        year=movie.release_date.year if movie.release_date else None,
        rating=float(movie.vote_average) if movie.vote_average is not None else None,
        poster_path=movie.poster_path,
    )


def jaccard_similar(source_genre_ids: set[int], candidates: list[dict], exclude_id: int, limit: int = 10) -> list[dict]:
    """D6 'more like this': weighted genre overlap (Jaccard) with a popularity tiebreak."""
    scored = []
    for c in candidates:
        if c["id"] == exclude_id:
            continue
        cand_genres = set(c.get("genre_ids", []))
        union = source_genre_ids | cand_genres
        jaccard = len(source_genre_ids & cand_genres) / len(union) if union else 0
        if jaccard == 0:
            continue
        pop_tiebreak = min(c.get("popularity") or 0, 200) / 2000
        scored.append((jaccard + pop_tiebreak, c))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:limit]]


def genre_affinity(db: Session, user_id: str) -> dict[int, float]:
    """(score - 5.5) summed per rated genre, normalized to [-1, 1] (D6)."""
    ratings = db.query(Rating).filter(Rating.user_id == user_id).all()
    affinity: dict[int, float] = {}
    for r in ratings:
        weight = r.score - 5.5
        for mg in r.movie.genres:
            affinity[mg.genre_id] = affinity.get(mg.genre_id, 0) + weight

    max_abs = max((abs(v) for v in affinity.values()), default=0)
    if max_abs == 0:
        return {}
    return {genre_id: value / max_abs for genre_id, value in affinity.items()}


async def personalized_feed(db: Session, user_id: str, limit: int = 20) -> list[MovieCardOut]:
    """Genre-affinity score blended with a little global popularity; cold start falls
    back to trending (D6)."""
    affinity = genre_affinity(db, user_id)
    if not affinity:
        trending = await get_or_sync_feed(db, "trending")
        return [tmdb_item_to_card(item) for item in trending[:limit]]

    exclude_ids = {r.movie_id for r in db.query(Rating).filter(Rating.user_id == user_id).all()}
    exclude_ids |= {w.movie_id for w in db.query(WatchlistItem).filter(WatchlistItem.user_id == user_id).all()}

    candidates: dict[int, dict] = {}
    for feed_key in ("trending", "popular", "top_rated"):
        for item in await get_or_sync_feed(db, feed_key):
            candidates.setdefault(item["id"], item)

    max_popularity = max((c.get("popularity") or 0 for c in candidates.values()), default=0) or 1
    popularity_weight = 0.15

    scored = []
    for movie_id, item in candidates.items():
        if movie_id in exclude_ids:
            continue
        score = sum(affinity.get(g, 0) for g in item.get("genre_ids", []))
        score += popularity_weight * ((item.get("popularity") or 0) / max_popularity)
        if score <= 0:
            continue
        scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [tmdb_item_to_card(item) for _, item in scored[:limit]]
