import { createContext, useContext } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../../shared/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const queryClient = useQueryClient();

  const { data: user, isLoading } = useQuery({
    queryKey: ["me"],
    queryFn: () => api.get("/me").then((r) => r.data),
    retry: false,
    staleTime: 60_000,
    throwOnError: false,
  });

  const loginMutation = useMutation({
    mutationFn: ({ email, password }) => api.post("/auth/login", { email, password }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["me"] }),
  });

  const registerMutation = useMutation({
    mutationFn: ({ email, password, display_name }) =>
      api.post("/auth/register", { email, password, display_name }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["me"] }),
  });

  const logout = async () => {
    await api.post("/auth/logout");
    queryClient.setQueryData(["me"], null);
    queryClient.invalidateQueries();
  };

  const value = {
    user: user ?? null,
    isAuthenticated: Boolean(user),
    isLoading,
    login: loginMutation.mutateAsync,
    loginError: loginMutation.error,
    isLoggingIn: loginMutation.isPending,
    register: registerMutation.mutateAsync,
    registerError: registerMutation.error,
    isRegistering: registerMutation.isPending,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
