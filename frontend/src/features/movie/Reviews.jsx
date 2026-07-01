import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../../shared/api";
import { useAuth } from "../auth/AuthContext";

export default function Reviews({ movieId }) {
  const { user, isAuthenticated } = useAuth();
  const queryClient = useQueryClient();
  const [draft, setDraft] = useState("");
  const [editing, setEditing] = useState(false);

  const { data } = useQuery({
    queryKey: ["movie-reviews", movieId],
    queryFn: () => api.get(`/movies/${movieId}/reviews`).then((r) => r.data),
  });

  const myReview = data?.items.find((r) => r.user_id === user?.id);
  const otherReviews = (data?.items ?? []).filter((r) => r.user_id !== user?.id);

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ["movie-reviews", movieId] });

  const saveMutation = useMutation({
    mutationFn: (body) => api.put(`/movies/${movieId}/review`, { body }),
    onSuccess: () => {
      invalidate();
      setEditing(false);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => api.delete(`/movies/${movieId}/review`),
    onSuccess: invalidate,
  });

  return (
    <div className="mb-10">
      <div className="font-extrabold text-lg text-ink mb-4">Reviews</div>

      {isAuthenticated && (
        <div className="mb-6">
          {myReview && !editing ? (
            <div className="rounded-xl bg-surface-2 border border-white/5 p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-sm text-ink">Your review</span>
                <div className="flex gap-3 font-mono text-xs text-faint">
                  <button onClick={() => { setDraft(myReview.body); setEditing(true); }} className="hover:text-ink">
                    Edit
                  </button>
                  <button onClick={() => deleteMutation.mutate()} className="hover:text-crimson">
                    Delete
                  </button>
                </div>
              </div>
              <p className="text-sm text-muted leading-relaxed">{myReview.body}</p>
            </div>
          ) : (
            <div className="flex flex-col gap-2">
              <textarea
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                placeholder="Write a review…"
                rows={3}
                className="rounded-xl bg-surface-2 border border-white/10 p-3 text-sm text-ink outline-none focus:border-crimson/50"
              />
              <div className="flex gap-2 self-end">
                {editing && (
                  <button onClick={() => setEditing(false)} className="h-8 px-3 rounded-lg text-xs text-muted">
                    Cancel
                  </button>
                )}
                <button
                  disabled={!draft.trim()}
                  onClick={() => saveMutation.mutate(draft.trim())}
                  className="h-8 px-4 rounded-lg bg-crimson text-white text-xs font-bold disabled:opacity-40"
                >
                  {myReview ? "Save" : "Post review"}
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="flex flex-col gap-3">
        {otherReviews.map((r) => (
          <div key={r.user_id} className="rounded-xl bg-surface-2 border border-white/5 p-4">
            <div className="flex items-center justify-between mb-1.5">
              <span className="font-semibold text-sm text-ink">{r.display_name}</span>
            </div>
            <p className="text-sm text-muted leading-relaxed">{r.body}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
