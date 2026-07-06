from datetime import date

from pydantic import BaseModel

from movies.schemas import CreditOut, GenreOut


class TvShowDetailOut(BaseModel):
    id: int
    title: str
    first_air_date: date | None = None
    number_of_seasons: int | None = None
    number_of_episodes: int | None = None
    vote_average: float | None = None
    poster_path: str | None = None
    backdrop_path: str | None = None
    overview: str | None = None
    genres: list[GenreOut] = []
    cast: list[CreditOut] = []
    trailer_key: str | None = None
