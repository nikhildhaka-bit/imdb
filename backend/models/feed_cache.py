from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class FeedCache(Base):
    """Ordered TMDB list endpoints (trending/popular/top_rated) — short-TTL ID arrays,
    separate from per-movie caching (D7)."""

    __tablename__ = "feed_cache"

    feed_key: Mapped[str] = mapped_column(String(40), primary_key=True)  # e.g. 'trending', 'popular', 'top_rated'
    movie_ids: Mapped[list] = mapped_column(JSON, nullable=False)
    synced_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
