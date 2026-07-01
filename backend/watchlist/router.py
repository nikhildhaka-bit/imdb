from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user, require_csrf
from database import get_db
from models import User, WatchlistItem
from movies.schemas import Page
from movies.service import get_or_sync_movie, movie_to_card

router = APIRouter(prefix="/me/watchlist", tags=["watchlist"])


@router.get("", response_model=Page)
def get_watchlist(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    items = (
        db.query(WatchlistItem)
        .filter(WatchlistItem.user_id == user.id)
        .order_by(WatchlistItem.added_at.desc())
        .all()
    )
    cards = [movie_to_card(item.movie) for item in items]
    return Page(items=cards, page=1, total=len(cards))


@router.put("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_csrf)])
async def add_to_watchlist(movie_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    await get_or_sync_movie(db, movie_id)
    existing = db.get(WatchlistItem, (user.id, movie_id))
    if existing is None:
        db.add(WatchlistItem(user_id=user.id, movie_id=movie_id, added_at=datetime.now(timezone.utc)))
        db.commit()


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_csrf)])
def remove_from_watchlist(movie_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    existing = db.get(WatchlistItem, (user.id, movie_id))
    if existing is not None:
        db.delete(existing)
        db.commit()
