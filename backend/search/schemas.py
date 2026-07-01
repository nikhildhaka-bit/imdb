from pydantic import BaseModel


class SearchResultOut(BaseModel):
    id: int
    media_type: str  # 'movie' | 'tv' | 'person'
    title: str
    year: int | None = None
    rating: float | None = None
    poster_path: str | None = None
    meta: str
