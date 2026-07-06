from datetime import date, datetime, timezone

from sqlalchemy import JSON, Date, DateTime, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class TvShow(Base):
    __tablename__ = "tv_shows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # = TMDB tv id — a separate
    # namespace from movie ids, which is exactly why this isn't just a row in `movies`.
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    first_air_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    number_of_seasons: Mapped[int | None] = mapped_column(Integer, nullable=True)
    number_of_episodes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vote_average: Mapped[float | None] = mapped_column(Numeric(3, 1), nullable=True)
    popularity: Mapped[float | None] = mapped_column(Float, nullable=True)
    poster_path: Mapped[str | None] = mapped_column(String(300), nullable=True)
    backdrop_path: Mapped[str | None] = mapped_column(String(300), nullable=True)
    overview: Mapped[str | None] = mapped_column(String, nullable=True)
    raw: Mapped[dict] = mapped_column(JSON, nullable=False)  # full TMDB payload
    synced_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    genres = relationship("TvShowGenre", back_populates="tv_show", cascade="all, delete-orphan")
    credits = relationship("TvShowCredit", back_populates="tv_show", cascade="all, delete-orphan")


class TvShowGenre(Base):
    __tablename__ = "tv_show_genres"

    tv_show_id: Mapped[int] = mapped_column(ForeignKey("tv_shows.id", ondelete="CASCADE"), primary_key=True)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id"), primary_key=True)

    tv_show = relationship("TvShow", back_populates="genres")
    genre = relationship("Genre")


class TvShowCredit(Base):
    __tablename__ = "tv_show_credits"

    tv_show_id: Mapped[int] = mapped_column(ForeignKey("tv_shows.id", ondelete="CASCADE"), primary_key=True)
    person_id: Mapped[int] = mapped_column(ForeignKey("people.id"), primary_key=True)
    credit_type: Mapped[str] = mapped_column(String(10), primary_key=True)  # 'cast' | 'crew'
    job: Mapped[str] = mapped_column(String(80), primary_key=True, default="")  # crew only; '' for cast rows
    character: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cast_order: Mapped[int | None] = mapped_column(Integer, nullable=True)

    tv_show = relationship("TvShow", back_populates="credits")
    person = relationship("Person")
