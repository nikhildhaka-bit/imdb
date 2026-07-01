from pydantic import BaseModel


class TasteItem(BaseModel):
    genre: str
    count: int
    pct: int


class MyRatingOut(BaseModel):
    movie_id: int
    title: str
    year: int | None
    poster_path: str | None
    score: int
    rated_at: str


class MyReviewOut(BaseModel):
    movie_id: int
    title: str
    year: int | None
    poster_path: str | None
    body: str
    updated_at: str


class ProfileOut(BaseModel):
    id: str
    email: str
    display_name: str
    avatar_url: str | None
    member_since: str
    rated_count: int
    review_count: int
    watchlist_count: int
    taste: list[TasteItem]
