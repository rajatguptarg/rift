import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import type { AuthSessionResponse, UserSummary } from "../types/api";

interface AuthState {
  token: string | null;
  user: UserSummary | null;
  isLoading: boolean;
}

interface AuthContextValue extends AuthState {
  isAuthenticated: boolean;
  login: (session: AuthSessionResponse) => void;
  logout: () => void;
  setUser: (user: UserSummary) => void;
}

const STORAGE_KEY = "rift_token";

const AuthContext = createContext<AuthContextValue | null>(null);

export const AuthProvider: React.FC<{
  children: React.ReactNode;
}> = ({ children }) => {
  const [state, setState] = useState<AuthState>(() => {
    const token = localStorage.getItem(STORAGE_KEY);
    return { token, user: null, isLoading: !!token };
  });

  // Hydrate user on mount if we have a token
  useEffect(() => {
    if (!state.token) return;
    import("../services/api").then(({ api }) => {
      api
        .get<{ user: UserSummary }>("/api/v1/auth/me")
        .then((res) => {
          setState((s) => ({ ...s, user: res.data.user, isLoading: false }));
        })
        .catch(() => {
          // Invalid/expired token — clear it
          localStorage.removeItem(STORAGE_KEY);
          setState({ token: null, user: null, isLoading: false });
        });
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Listen for auth expiry events dispatched by the api interceptor
  useEffect(() => {
    const handler = () => {
      setState({ token: null, user: null, isLoading: false });
    };
    window.addEventListener("rift:auth:expired", handler);
    return () => window.removeEventListener("rift:auth:expired", handler);
  }, []);

  const login = useCallback((session: AuthSessionResponse) => {
    localStorage.setItem(STORAGE_KEY, session.access_token);
    setState({ token: session.access_token, user: session.user, isLoading: false });
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    setState({ token: null, user: null, isLoading: false });
  }, []);

  const setUser = useCallback((user: UserSummary) => {
    setState((s) => ({ ...s, user }));
  }, []);

  return (
    <AuthContext.Provider
      value={{
        ...state,
        isAuthenticated: !!state.token && !state.isLoading,
        login,
        logout,
        setUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
