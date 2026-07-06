from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import TvShowCredit
from movies.schemas import CreditOut, GenreOut
from tv.schemas import TvShowDetailOut
from tv.service import get_or_sync_tv_show

router = APIRouter(tags=["tv"])


@router.get("/tv/{tv_id}", response_model=TvShowDetailOut)
async def tv_show_detail(tv_id: int, db: Session = Depends(get_db)):
    tv_show = await get_or_sync_tv_show(db, tv_id)

    genres = [GenreOut(id=tg.genre_id, name=tg.genre.name) for tg in tv_show.genres]

    cast = (
        db.query(TvShowCredit)
        .filter(TvShowCredit.tv_show_id == tv_show.id, TvShowCredit.credit_type == "cast")
        .order_by(TvShowCredit.cast_order)
        .limit(10)
        .all()
    )
    cast_out = [
        CreditOut(person_id=c.person_id, name=c.person.name, role=c.character or "", profile_path=c.person.profile_path)
        for c in cast
    ]

    trailer_key = None
    for video in tv_show.raw.get("videos", {}).get("results", []):
        if video.get("site") == "YouTube" and video.get("type") == "Trailer":
            trailer_key = video["key"]
            break

    return TvShowDetailOut(
        id=tv_show.id,
        title=tv_show.title,
        first_air_date=tv_show.first_air_date,
        number_of_seasons=tv_show.number_of_seasons,
        number_of_episodes=tv_show.number_of_episodes,
        vote_average=float(tv_show.vote_average) if tv_show.vote_average is not None else None,
        poster_path=tv_show.poster_path,
        backdrop_path=tv_show.backdrop_path,
        overview=tv_show.overview,
        genres=genres,
        cast=cast_out,
        trailer_key=trailer_key,
    )
