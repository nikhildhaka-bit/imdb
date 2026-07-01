class Movie:
    def __init__(self, title, release_year, runtime_minutes):
        self.title = title
        self.release_year = release_year
        self.runtime_minutes = runtime_minutes

    # a normal method -- needs `self`, works on THIS specific movie
    def summary(self):
        return f"{self.title} ({self.release_year})"

    # @property -- looks like an attribute when you USE it, but runs code
    @property
    def runtime_hours(self):
        return round(self.runtime_minutes / 60, 2)

    # @classmethod -- gets the CLASS itself (cls), used as alt constructor
    @classmethod
    def from_tmdb_json(cls, data: dict):
        return cls(
            title=data["title"],
            release_year=int(data["release_date"][:4]),
            runtime_minutes=data["runtime"],
        )

    # @staticmethod -- doesn't need self OR cls, just grouped here for organization
    @staticmethod
    def is_valid_rating(rating):
        return 1 <= rating <= 10


inception = Movie("Inception", 2010, 148)

print(inception.summary())
print(inception.runtime_hours)          # NOTE: no parentheses!
print(Movie.is_valid_rating(11))
print(Movie.is_valid_rating(9))

tmdb_data = {"title": "Tenet", "release_date": "2020-08-26", "runtime": 150}
tenet = Movie.from_tmdb_json(tmdb_data)
print(tenet.summary())
