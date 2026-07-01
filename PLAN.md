# IMDB Clone — Project Plan

## Stack Summary

| Layer | Technology |
|---|---|
| Frontend | React.js |
| UI Library | Shadcn/ui (Tailwind CSS under the hood) |
| Animations | Framer Motion |
| Data Fetching | TanStack Query + Axios |
| Global State | React Context (auth only) |
| Backend | Python FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy + Alembic (migrations) |
| Auth | Email + Password + JWT (bcrypt) |
| Data Source | TMDB API (cache-on-demand) |

---

## Features

### Movies & TV
- Browse movies and TV shows (trending, popular, top rated)
- Search by title with **typeahead autocomplete** (debounced, skeleton suggestions)
- Movie detail page — poster, overview, cast, crew, trailer, runtime, genres
- Filter by genre, year, rating
- Actor / director detail page
- TMDB "More like this" recommendations on every movie page

### Users
- Register and login (email + password)
- JWT authentication
- User profile page
- Rate movies (1–10 stars) — editable and deletable
- Write, edit, and delete reviews
- Personal watchlist (add/remove movies)
- Personalized homepage recommendation feed (based on user's top-rated genres)

### UX
- Skeleton shimmer screens while loading (search results, movie cards, suggestions)
- Framer Motion animations — staggered card entrance, page transitions, hover effects
- Typeahead search dropdown with skeleton → real suggestions (400ms debounce)

---

## Database Schema

```sql
users (
  id            SERIAL PRIMARY KEY,
  email         TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  name          TEXT,
  avatar_url    TEXT,
  created_at    TIMESTAMP DEFAULT NOW()
)

movies (
  id            SERIAL PRIMARY KEY,
  tmdb_id       INTEGER UNIQUE NOT NULL,
  title         TEXT NOT NULL,
  poster_url    TEXT,
  release_date  DATE,
  data          JSONB,          -- full TMDB response, no field mapping needed
  synced_at     TIMESTAMP       -- used to detect stale cache
)

ratings (
  id         SERIAL PRIMARY KEY,
  user_id    INTEGER REFERENCES users(id),
  movie_id   INTEGER REFERENCES movies(id),
  rating     SMALLINT CHECK (rating BETWEEN 1 AND 10),
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE (user_id, movie_id)
)

reviews (
  id         SERIAL PRIMARY KEY,
  user_id    INTEGER REFERENCES users(id),
  movie_id   INTEGER REFERENCES movies(id),
  content    TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP
)

watchlists (
  id         SERIAL PRIMARY KEY,
  user_id    INTEGER REFERENCES users(id),
  name       TEXT DEFAULT 'My Watchlist',
  created_at TIMESTAMP DEFAULT NOW()
)

watchlist_items (
  id           SERIAL PRIMARY KEY,
  watchlist_id INTEGER REFERENCES watchlists(id),
  movie_id     INTEGER REFERENCES movies(id),
  added_at     TIMESTAMP DEFAULT NOW(),
  UNIQUE (watchlist_id, movie_id)
)
```

---

## TMDB Data Strategy

**Cache-on-demand (lazy caching):**
1. User searches "Inception"
2. FastAPI checks `movies` table first
3. Found → return instantly (no API call)
4. Not found → call TMDB API → save to `movies` table → return to user

**Search flow:**
- Always call TMDB `/search/movie?query=...` for search results (queries vary too much to cache)
- Cache individual movie details on first view
- `synced_at` older than 30 days → re-fetch from TMDB automatically

**JSONB benefits:**
- Stores full TMDB response without mapping 50+ fields
- Queryable and indexable in PostgreSQL
- TMDB API changes → update `serialize_movie()` in one place + re-sync, no schema migration

---

## Project Structure (Monorepo)

```
imdb/
├── frontend/
│   ├── src/
│   │   ├── features/
│   │   │   ├── movies/
│   │   │   │   ├── MovieCard.jsx
│   │   │   │   ├── MovieDetail.jsx
│   │   │   │   ├── MovieGrid.jsx
│   │   │   │   └── useMovies.js
│   │   │   ├── auth/
│   │   │   │   ├── LoginForm.jsx
│   │   │   │   ├── RegisterForm.jsx
│   │   │   │   └── useAuth.js
│   │   │   ├── search/
│   │   │   │   ├── SearchBar.jsx
│   │   │   │   ├── SearchSuggestions.jsx
│   │   │   │   └── useSearch.js
│   │   │   ├── ratings/
│   │   │   │   └── StarRating.jsx
│   │   │   ├── reviews/
│   │   │   │   ├── ReviewForm.jsx
│   │   │   │   └── ReviewList.jsx
│   │   │   ├── watchlist/
│   │   │   │   ├── WatchlistPage.jsx
│   │   │   │   └── useWatchlist.js
│   │   │   └── recommendations/
│   │   │       └── RecommendationFeed.jsx
│   │   ├── components/         ← shared UI (Navbar, SkeletonCard, Button)
│   │   ├── pages/              ← route-level pages
│   │   ├── context/
│   │   │   └── AuthContext.jsx
│   │   └── App.jsx
│   └── package.json
│
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── movies/
│   │   ├── router.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── users/
│   │   ├── router.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── auth/
│   │   ├── router.py
│   │   └── jwt.py
│   ├── ratings/
│   │   ├── router.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── reviews/
│   │   ├── router.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── watchlist/
│   │   ├── router.py
│   │   ├── models.py
│   │   └── schemas.py
│   └── requirements.txt
│
└── PLAN.md
```

---

## Development Setup

**Two terminals, no Docker:**

```bash
# Terminal 1 — Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload

# Terminal 2 — Frontend
cd frontend
npm install
npm run dev
```

PostgreSQL installed locally on your machine.

---

## Key API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login, returns JWT |
| GET | `/movies/search?q=` | Search movies (TMDB + cache) |
| GET | `/movies/{tmdb_id}` | Movie detail (cache-on-demand) |
| GET | `/movies/trending` | Trending movies from TMDB |
| GET | `/movies/{id}/recommendations` | TMDB recommendations |
| POST | `/ratings` | Rate a movie |
| PUT | `/ratings/{id}` | Edit rating |
| DELETE | `/ratings/{id}` | Delete rating |
| POST | `/reviews` | Write a review |
| PUT | `/reviews/{id}` | Edit review |
| DELETE | `/reviews/{id}` | Delete review |
| GET | `/watchlist` | Get user's watchlist |
| POST | `/watchlist` | Add movie to watchlist |
| DELETE | `/watchlist/{id}` | Remove from watchlist |
| GET | `/users/me/recommendations` | Personalized feed |

---

## Recommended Build Order

1. **Backend foundation** — PostgreSQL setup, SQLAlchemy models, Alembic migrations
2. **Auth** — register, login, JWT middleware
3. **Movies** — TMDB integration, search, cache-on-demand, movie detail
4. **Frontend foundation** — React + Shadcn/ui setup, routing, AuthContext
5. **Search UI** — typeahead, skeleton suggestions, Framer Motion
6. **Movie pages** — browse, detail, cast/crew
7. **Ratings** — star rating component, API integration
8. **Watchlist** — add/remove, watchlist page
9. **Reviews** — write, edit, delete
10. **Recommendations** — TMDB "More like this" + personalized feed
11. **Profile page** — user's ratings, reviews, watchlist summary
12. **Polish** — animations, loading states, error handling
