from fastapi import APIRouter, Query

from movies.schemas import Page
from movies.tmdb_client import tmdb_client
from search.schemas import SearchResultOut

router = APIRouter(tags=["search"])


def _to_result(item: dict) -> SearchResultOut | None:
    # TMDB IDs for movies and TV shows are separate, overlapping namespaces — the
    # frontend must route "tv" hits to /tv/{id}, never /movie/{id}, or it'll land
    # on a completely unrelated title that happens to share that numeric id.
    media_type = item.get("media_type")
    if media_type not in ("movie", "tv", "person"):
        return None

    if media_type == "person":
        return SearchResultOut(
            id=item["id"],
            media_type=media_type,
            title=item.get("name", ""),
            poster_path=item.get("profile_path"),
            meta=f"Person · {item.get('known_for_department', '')}".strip(" ·"),
        )

    release_date = item.get("release_date") or item.get("first_air_date") or ""
    year = int(release_date[:4]) if release_date[:4].isdigit() else None
    return SearchResultOut(
        id=item["id"],
        media_type=media_type,
        title=item.get("title") or item.get("name") or "",
        year=year,
        rating=item.get("vote_average"),
        poster_path=item.get("poster_path"),
        meta=f"{'Movie' if media_type == 'movie' else 'TV'} · {year or ''}".strip(" ·"),
    )


@router.get("/search", response_model=Page)
async def search(q: str = Query(min_length=1), page: int = 1):
    payload = await tmdb_client.search_multi(q, page)
    results = [r for r in (_to_result(item) for item in payload.get("results", [])) if r is not None]
    return Page(items=results, page=page, total=payload.get("total_results", len(results)))
