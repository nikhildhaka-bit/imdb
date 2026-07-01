import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./features/auth/AuthContext";
import RequireAuth from "./features/auth/RequireAuth";
import Layout from "./app/Layout";
import HomePage from "./features/browse/HomePage";
import MoviesPage from "./features/browse/MoviesPage";
import SearchPage from "./features/search/SearchPage";
import MovieDetailPage from "./features/movie/MovieDetailPage";
import PersonDetailPage from "./features/person/PersonDetailPage";
import AuthPage from "./features/auth/AuthPage";
import ProfilePage from "./features/profile/ProfilePage";
import WatchlistPage from "./features/watchlist/WatchlistPage";

const queryClient = new QueryClient({
  defaultOptions: { queries: { refetchOnWindowFocus: false } },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route element={<Layout />}>
              <Route path="/" element={<HomePage />} />
              <Route path="/movies" element={<MoviesPage />} />
              <Route path="/search" element={<SearchPage />} />
              <Route path="/movie/:id" element={<MovieDetailPage />} />
              <Route path="/person/:id" element={<PersonDetailPage />} />
              <Route path="/login" element={<AuthPage />} />
              <Route path="/register" element={<AuthPage />} />
              <Route
                path="/profile"
                element={
                  <RequireAuth>
                    <ProfilePage />
                  </RequireAuth>
                }
              />
              <Route
                path="/watchlist"
                element={
                  <RequireAuth>
                    <WatchlistPage />
                  </RequireAuth>
                }
              />
            </Route>
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
