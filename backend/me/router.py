from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database import get_db
from me.schemas import MyRatingOut, MyReviewOut, ProfileOut, TasteItem
from models import Genre, Rating, Review, User, WatchlistItem
from movies.schemas import Page
from movies.service import personalized_feed

router = APIRouter(prefix="/me", tags=["me"])


@router.get("", response_model=ProfileOut)
def my_profile(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ratings = db.query(Rating).filter(Rating.user_id == user.id).all()

    genre_counts: dict[int, int] = {}
    for r in ratings:
        for mg in r.movie.genres:
            genre_counts[mg.genre_id] = genre_counts.get(mg.genre_id, 0) + 1

    top_genres = sorted(genre_counts.items(), key=lambda kv: kv[1], reverse=True)[:5]
    max_count = top_genres[0][1] if top_genres else 1
    taste = [
        TasteItem(genre=db.get(Genre, genre_id).name, count=count, pct=round(count / max_count * 100))
        for genre_id, count in top_genres
    ]

    return ProfileOut(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        member_since=user.created_at.strftime("%Y"),
        rated_count=len(ratings),
        review_count=db.query(Review).filter(Review.user_id == user.id).count(),
        watchlist_count=db.query(WatchlistItem).filter(WatchlistItem.user_id == user.id).count(),
        taste=taste,
    )


@router.get("/feed", response_model=Page)
async def my_feed(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cards = await personalized_feed(db, user.id)
    return Page(items=cards, page=1, total=len(cards))


@router.get("/ratings", response_model=Page)
def my_ratings(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(Rating).filter(Rating.user_id == user.id).order_by(Rating.updated_at.desc()).all()
    items = [
        MyRatingOut(
            movie_id=r.movie_id,
            title=r.movie.title,
            year=r.movie.release_date.year if r.movie.release_date else None,
            poster_path=r.movie.poster_path,
            score=r.score,
            rated_at=r.updated_at.isoformat(),
        )
        for r in rows
    ]
    return Page(items=items, page=1, total=len(items))


@router.get("/reviews", response_model=Page)
def my_reviews(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(Review).filter(Review.user_id == user.id).order_by(Review.updated_at.desc()).all()
    items = [
        MyReviewOut(
            movie_id=r.movie_id,
            title=r.movie.title,
            year=r.movie.release_date.year if r.movie.release_date else None,
            poster_path=r.movie.poster_path,
            body=r.body,
            updated_at=r.updated_at.isoformat(),
        )
        for r in rows
    ]
    return Page(items=items, page=1, total=len(items))
