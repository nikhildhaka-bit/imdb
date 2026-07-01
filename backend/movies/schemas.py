from datetime import date

from pydantic import BaseModel, Field


class GenreOut(BaseModel):
    id: int
    name: str


class CreditOut(BaseModel):
    person_id: int
    name: str
    role: str  # character (cast) or job (crew)
    profile_path: str | None = None


class MovieCardOut(BaseModel):
    id: int
    title: str
    year: int | None = None
    rating: float | None = None
    poster_path: str | None = None


class MovieDetailOut(BaseModel):
    id: int
    title: str
    release_date: date | None = None
    runtime: int | None = None
    vote_average: float | None = None
    poster_path: str | None = None
    backdrop_path: str | None = None
    overview: str | None = None
    genres: list[GenreOut] = []
    cast: list[CreditOut] = []
    director: str | None = None
    trailer_key: str | None = None
    my_rating: int | None = None
    in_watchlist: bool = False


class Page(BaseModel):
    items: list
    page: int
    total: int


class RatingIn(BaseModel):
    score: int = Field(ge=1, le=10)


class ReviewIn(BaseModel):
    body: str = Field(min_length=1, max_length=10_000)


class ReviewOut(BaseModel):
    user_id: str
    display_name: str
    body: str
    created_at: str
    updated_at: str
