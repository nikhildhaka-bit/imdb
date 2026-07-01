from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user, get_optional_user, require_csrf
from database import get_db
from models import Movie, MovieCredit, Rating, Review, User, WatchlistItem
from movies.schemas import (
    CreditOut,
    GenreOut,
    MovieDetailOut,
    Page,
    RatingIn,
    ReviewIn,
    ReviewOut,
)
from movies.service import get_or_sync_movie, get_or_sync_feed, jaccard_similar, tmdb_item_to_card
from movies.tmdb_client import tmdb_client

router = APIRouter(tags=["movies"])

PAGE_SIZE = 20


@router.get("/movies", response_model=Page)
async def browse_movies(
    feed: str | None = None,
    genre: int | None = None,
    year: int | None = None,
    min_rating: float | None = None,
    page: int = 1,
    db: Session = Depends(get_db),
):
    if feed:
        if feed not in ("trending", "popular", "top_rated"):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "feed must be trending, popular, or top_rated")
        items = await get_or_sync_feed(db, feed)
        if genre is not None:
            items = [i for i in items if genre in i.get("genre_ids", [])]
        if year is not None:
            items = [i for i in items if (i.get("release_date") or "")[:4] == str(year)]
        if min_rating is not None:
            items = [i for i in items if (i.get("vote_average") or 0) >= min_rating]
        total = len(items)
        start = (page - 1) * PAGE_SIZE
        page_items = items[start : start + PAGE_SIZE]
    else:
        params = {"sort_by": "popularity.desc", "page": page}
        if genre is not None:
            params["with_genres"] = genre
        if year is not None:
            params["primary_release_year"] = year
        if min_rating is not None:
            params["vote_average.gte"] = min_rating
        payload = await tmdb_client.discover_movies(params)
        page_items = payload.get("results", [])
        total = payload.get("total_results", len(page_items))

    return Page(items=[tmdb_item_to_card(i) for i in page_items], page=page, total=total)


@router.get("/movies/{movie_id}", response_model=MovieDetailOut)
async def movie_detail(movie_id: int, db: Session = Depends(get_db), user: User | None = Depends(get_optional_user)):
    movie = await get_or_sync_movie(db, movie_id)

    genres = [GenreOut(id=mg.genre_id, name=mg.genre.name) for mg in movie.genres]

    cast = (
        db.query(MovieCredit)
        .filter(MovieCredit.movie_id == movie.id, MovieCredit.credit_type == "cast")
        .order_by(MovieCredit.cast_order)
        .limit(10)
        .all()
    )
    cast_out = [
        CreditOut(person_id=c.person_id, name=c.person.name, role=c.character or "", profile_path=c.person.profile_path)
        for c in cast
    ]

    director_credit = (
        db.query(MovieCredit)
        .filter(MovieCredit.movie_id == movie.id, MovieCredit.credit_type == "crew", MovieCredit.job == "Director")
        .first()
    )
    director = director_credit.person.name if director_credit else None

    trailer_key = None
    for video in movie.raw.get("videos", {}).get("results", []):
        if video.get("site") == "YouTube" and video.get("type") == "Trailer":
            trailer_key = video["key"]
            break

    my_rating = None
    in_watchlist = False
    if user is not None:
        rating = db.get(Rating, (user.id, movie.id))
        my_rating = rating.score if rating else None
        in_watchlist = db.get(WatchlistItem, (user.id, movie.id)) is not None

    return MovieDetailOut(
        id=movie.id,
        title=movie.title,
        release_date=movie.release_date,
        runtime=movie.runtime,
        vote_average=float(movie.vote_average) if movie.vote_average is not None else None,
        poster_path=movie.poster_path,
        backdrop_path=movie.backdrop_path,
        overview=movie.overview,
        genres=genres,
        cast=cast_out,
        director=director,
        trailer_key=trailer_key,
        my_rating=my_rating,
        in_watchlist=in_watchlist,
    )


@router.get("/movies/{movie_id}/similar", response_model=Page)
async def similar_movies(movie_id: int, db: Session = Depends(get_db)):
    movie = await get_or_sync_movie(db, movie_id)
    source_genre_ids = {mg.genre_id for mg in movie.genres}

    payload = await tmdb_client.get_similar(movie_id)
    candidates = payload.get("results", [])
    ranked = jaccard_similar(source_genre_ids, candidates, exclude_id=movie_id)

    cards = [tmdb_item_to_card(c) for c in ranked]
    return Page(items=cards, page=1, total=len(cards))


@router.get("/movies/{movie_id}/reviews", response_model=Page)
def movie_reviews(movie_id: int, page: int = 1, db: Session = Depends(get_db)):
    query = db.query(Review).filter(Review.movie_id == movie_id).order_by(Review.created_at.desc())
    total = query.count()
    rows = query.offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE).all()
    items = [
        ReviewOut(
            user_id=r.user_id,
            display_name=r.user.display_name,
            body=r.body,
            created_at=r.created_at.isoformat(),
            updated_at=r.updated_at.isoformat(),
        )
        for r in rows
    ]
    return Page(items=items, page=page, total=total)


@router.put("/movies/{movie_id}/rating", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_csrf)])
async def upsert_rating(
    movie_id: int, payload: RatingIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    await get_or_sync_movie(db, movie_id)  # ensure the movie exists before rating it
    rating = db.get(Rating, (user.id, movie_id))
    if rating is None:
        db.add(Rating(user_id=user.id, movie_id=movie_id, score=payload.score))
    else:
        rating.score = payload.score
        rating.updated_at = datetime.now(timezone.utc)
    db.commit()


@router.delete("/movies/{movie_id}/rating", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_csrf)])
def delete_rating(movie_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rating = db.get(Rating, (user.id, movie_id))
    if rating is not None:
        db.delete(rating)
        db.commit()


@router.put("/movies/{movie_id}/review", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_csrf)])
async def upsert_review(
    movie_id: int, payload: ReviewIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    await get_or_sync_movie(db, movie_id)
    review = db.get(Review, (user.id, movie_id))
    if review is None:
        db.add(Review(user_id=user.id, movie_id=movie_id, body=payload.body))
    else:
        review.body = payload.body
        review.updated_at = datetime.now(timezone.utc)
    db.commit()


@router.delete("/movies/{movie_id}/review", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_csrf)])
def delete_review(movie_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    review = db.get(Review, (user.id, movie_id))
    if review is not None:
        db.delete(review)
        db.commit()
