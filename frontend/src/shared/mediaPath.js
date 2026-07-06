// Search results mix three unrelated TMDB id namespaces (movie, tv, person) —
// centralizing this mapping avoids a tv/movie id ever landing on the wrong route.
export function resultPath(item) {
  if (item.media_type === "person") return `/person/${item.id}`;
  if (item.media_type === "tv") return `/tv/${item.id}`;
  return `/movie/${item.id}`;
}
