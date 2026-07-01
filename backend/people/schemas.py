from pydantic import BaseModel


class FilmographyItem(BaseModel):
    movie_id: int
    title: str
    year: int | None = None
    role: str
    rating: float | None = None
    poster_path: str | None = None


class PersonDetailOut(BaseModel):
    id: int
    name: str
    profile_path: str | None = None
    known_for_department: str | None = None
    bio: str | None = None
    birthday: str | None = None
    credits_count: int
    avg_rating: float | None = None
    filmography: list[FilmographyItem]
