import React, { createContext, useContext, useState, useCallback } from "react";
import { api } from "../services/api.ts";

interface AuthState {
  token: string | null;
  userId: string | null;
  email: string | null;
}

interface AuthContextValue extends AuthState {
  isAuthenticated: boolean;
  login: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [state, setState] = useState<AuthState>(() => {
    const token = localStorage.getItem("rift_token");
    return { token, userId: null, email: null };
  });

  const login = useCallback((token: string) => {
    localStorage.setItem("rift_token", token);
    setState((s) => ({ ...s, token }));
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("rift_token");
    setState({ token: null, userId: null, email: null });
    window.location.href = "/login";
  }, []);

  return (
    <AuthContext.Provider
      value={{
        ...state,
        isAuthenticated: !!state.token,
        login,
        logout,
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
