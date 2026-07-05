import asyncio
import logging
import random
import time

import httpx

from config import settings

BASE_URL = "https://api.themoviedb.org/3"
logger = logging.getLogger(__name__)


class TokenBucket:
    """Keeps the TMDB client well under TMDB's rate ceiling (D4)."""

    def __init__(self, rate_per_sec: float = 8.0, capacity: int = 8):
        self.rate = rate_per_sec
        self.capacity = capacity
        self.tokens = float(capacity)
        self.updated_at = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self):
        async with self._lock:
            while True:
                now = time.monotonic()
                elapsed = now - self.updated_at
                self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
                self.updated_at = now
                if self.tokens >= 1:
                    self.tokens -= 1
                    return
                await asyncio.sleep((1 - self.tokens) / self.rate)


class TMDBClient:
    def __init__(self):
        self._client = httpx.AsyncClient(
            base_url=BASE_URL,
            headers={
                "Authorization": f"Bearer {settings.tmdb_read_access_token}",
                "accept": "application/json",
            },
            timeout=10.0,
        )
        self._bucket = TokenBucket()
        self._inflight: dict[str, asyncio.Future] = {}

    async def close(self):
        await self._client.aclose()

    async def _get(self, path: str, params: dict | None = None) -> dict:
        """Rate-limited GET with exponential backoff + jitter on 429, single-flight per key (D4)."""
        key = f"{path}?{params}"
        if key in self._inflight:
            return await self._inflight[key]

        future: asyncio.Future = asyncio.get_event_loop().create_future()
        self._inflight[key] = future
        try:
            result = await self._fetch_with_retry(path, params)
            future.set_result(result)
            return result
        except Exception as exc:
            future.set_exception(exc)
            raise
        finally:
            self._inflight.pop(key, None)

    async def _fetch_with_retry(self, path: str, params: dict | None, max_retries: int = 4) -> dict:
        for attempt in range(max_retries):
            await self._bucket.acquire()
            start = time.monotonic()
            response = await self._client.get(path, params=params)
            duration_ms = (time.monotonic() - start) * 1000
            if response.status_code == 429:
                backoff = (2**attempt) + random.random()
                logger.warning(f"TMDB rate-limited on {path} (attempt {attempt + 1}/{max_retries}), backing off {backoff:.1f}s")
                await asyncio.sleep(backoff)
                continue
            if response.status_code == 404:
                logger.info(f"TMDB request: {path} -> 404 ({duration_ms:.0f}ms)")
                response.raise_for_status()
            elif response.status_code >= 400:
                logger.error(f"TMDB request failed: {path} -> {response.status_code} ({duration_ms:.0f}ms)")
                response.raise_for_status()
            logger.debug(f"TMDB request: {path} -> {response.status_code} ({duration_ms:.0f}ms)")
            return response.json()
        logger.error(f"TMDB request exhausted all {max_retries} retries: {path}")
        response.raise_for_status()
        return response.json()

    async def get_movie(self, tmdb_id: int) -> dict:
        return await self._get(f"/movie/{tmdb_id}", {"append_to_response": "credits,videos"})

    async def get_similar(self, tmdb_id: int) -> dict:
        return await self._get(f"/movie/{tmdb_id}/recommendations")

    async def get_person(self, tmdb_id: int) -> dict:
        return await self._get(f"/person/{tmdb_id}", {"append_to_response": "movie_credits"})

    async def search_multi(self, query: str, page: int = 1) -> dict:
        return await self._get("/search/multi", {"query": query, "page": page, "include_adult": "false"})

    async def discover_movies(self, params: dict) -> dict:
        return await self._get("/discover/movie", params)

    async def get_feed(self, feed_key: str) -> dict:
        mapping = {
            "trending": "/trending/movie/week",
            "popular": "/movie/popular",
            "top_rated": "/movie/top_rated",
        }
        return await self._get(mapping[feed_key])


tmdb_client = TMDBClient()
