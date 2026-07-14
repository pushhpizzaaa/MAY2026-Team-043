import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { authApi } from "../services/endpoints";

const AuthContext = createContext(null);

const TOKEN_KEY = "sob_token";
const USER_KEY = "sob_user";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  });
  const [loading, setLoading] = useState(false);

  const persist = (token, u) => {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(u));
    setUser(u);
  };

  const login = async (email, password) => {
    setLoading(true);
    try {
      const { token, user: u } = await authApi.login({ email, password });
      persist(token, u);
      return u;
    } finally {
      setLoading(false);
    }
  };

  const register = async (body) => {
    setLoading(true);
    try {
      const { token, user: u } = await authApi.register(body);
      persist(token, u);
      return u;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setUser(null);
  };

  // Keep the stored user object fresh across tabs.
  useEffect(() => {
    const sync = () => {
      const raw = localStorage.getItem(USER_KEY);
      setUser(raw ? JSON.parse(raw) : null);
    };
    window.addEventListener("storage", sync);
    return () => window.removeEventListener("storage", sync);
  }, []);

  const value = useMemo(
    () => ({ user, loading, login, register, logout, isAuthenticated: !!user }),
    [user, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
