import functools
import time


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {end - start:.4f}s")
        return result
    return wrapper


@timer
def slow_add(a, b):
    time.sleep(0.5)
    return a + b


print(slow_add(2, 3))


def retry(times):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    print(f"attempt {attempt} failed: {e}")
            raise last_exc
        return wrapper
    return decorator


attempt_counter = {"n": 0}


@retry(times=3)
def flaky_fetch():
    attempt_counter["n"] += 1
    if attempt_counter["n"] < 3:
        raise ConnectionError("TMDB API timed out")
    return "movie data"


print(flaky_fetch())


def cache(func):
    store = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        if key in store:
            print(f"cache hit for {key}")
            return store[key]
        print(f"cache miss for {key}")
        result = func(*args, **kwargs)
        store[key] = result
        return result
    return wrapper


@cache
def fetch_movie(tmdb_id):
    print(f"  -> hitting TMDB API for movie {tmdb_id}...")
    time.sleep(0.3)
    return {"id": tmdb_id, "title": "Inception"}


print(fetch_movie(27205))
print(fetch_movie(27205))
print(fetch_movie(155))
