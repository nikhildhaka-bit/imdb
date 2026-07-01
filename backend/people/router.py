from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from people.schemas import FilmographyItem, PersonDetailOut
from movies.service import get_or_sync_person

router = APIRouter(tags=["people"])


@router.get("/people/{person_id}", response_model=PersonDetailOut)
async def person_detail(person_id: int, db: Session = Depends(get_db)):
    person = await get_or_sync_person(db, person_id)
    raw = person.raw

    credits = raw.get("movie_credits", {})
    is_behind_the_camera = person.known_for_department in ("Directing", "Writing", "Production", "Crew")

    seen: dict[int, dict] = {}
    for entry in credits.get("crew", []):
        if entry.get("job") not in ("Director", "Writer", "Screenplay"):
            continue
        seen.setdefault(entry["id"], {**entry, "role": entry["job"]})
    if not is_behind_the_camera:
        # acting filmography only for people primarily known for acting — directors/writers
        # also rack up incidental cast credits (self-appearances, documentaries) that don't
        # belong on a "filmography as Director" page
        for entry in credits.get("cast", []):
            seen.setdefault(entry["id"], {**entry, "role": entry.get("character") or "Actor"})

    filmography = sorted(seen.values(), key=lambda e: e.get("release_date") or "", reverse=True)
    items = [
        FilmographyItem(
            movie_id=e["id"],
            title=e.get("title") or e.get("name") or "",
            year=int(e["release_date"][:4]) if e.get("release_date") else None,
            role=e["role"],
            rating=e.get("vote_average"),
            poster_path=e.get("poster_path"),
        )
        for e in filmography
    ]

    ratings = [i.rating for i in items if i.rating]
    avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else None

    return PersonDetailOut(
        id=person.id,
        name=person.name,
        profile_path=person.profile_path,
        known_for_department=person.known_for_department,
        bio=raw.get("biography") or None,
        birthday=raw.get("birthday"),
        credits_count=len(items),
        avg_rating=avg_rating,
        filmography=items,
    )
