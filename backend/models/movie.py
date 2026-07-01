from datetime import date, datetime, timezone

from sqlalchemy import JSON, Date, DateTime, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # = TMDB id, no surrogate
    media_type: Mapped[str] = mapped_column(String(10), nullable=False, default="movie")
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    release_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    runtime: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vote_average: Mapped[float | None] = mapped_column(Numeric(3, 1), nullable=True)
    popularity: Mapped[float | None] = mapped_column(Float, nullable=True)
    poster_path: Mapped[str | None] = mapped_column(String(300), nullable=True)
    backdrop_path: Mapped[str | None] = mapped_column(String(300), nullable=True)
    overview: Mapped[str | None] = mapped_column(String, nullable=True)
    raw: Mapped[dict] = mapped_column(JSON, nullable=False)  # full TMDB payload
    synced_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    genres = relationship("MovieGenre", back_populates="movie", cascade="all, delete-orphan")
    credits = relationship("MovieCredit", back_populates="movie", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="movie", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="movie", cascade="all, delete-orphan")


class Genre(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)


class MovieGenre(Base):
    __tablename__ = "movie_genres"

    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id"), primary_key=True)

    movie = relationship("Movie", back_populates="genres")
    genre = relationship("Genre")


class Person(Base):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # = TMDB person id
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    profile_path: Mapped[str | None] = mapped_column(String(300), nullable=True)
    known_for_department: Mapped[str | None] = mapped_column(String(80), nullable=True)
    raw: Mapped[dict] = mapped_column(JSON, nullable=False)
    synced_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    credits = relationship("MovieCredit", back_populates="person")


class MovieCredit(Base):
    __tablename__ = "movie_credits"

    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True)
    person_id: Mapped[int] = mapped_column(ForeignKey("people.id"), primary_key=True)
    credit_type: Mapped[str] = mapped_column(String(10), primary_key=True)  # 'cast' | 'crew'
    job: Mapped[str] = mapped_column(String(80), primary_key=True, default="")  # crew only; '' for cast rows
    character: Mapped[str | None] = mapped_column(String(255), nullable=True)
    department: Mapped[str | None] = mapped_column(String(80), nullable=True)
    cast_order: Mapped[int | None] = mapped_column(Integer, nullable=True)

    movie = relationship("Movie", back_populates="credits")
    person = relationship("Person", back_populates="credits")
