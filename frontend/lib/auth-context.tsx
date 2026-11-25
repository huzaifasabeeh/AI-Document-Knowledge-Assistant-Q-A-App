"use client";

import React, { createContext, useCallback, useContext, useEffect, useState } from "react";
import { AuthUser, HealthStatus } from "./types";
import {
  ApiError,
  getHealth,
  getMe,
  loginUser,
  logoutUser,
  signupUser,
} from "./api";

const SESSION_TOKEN_KEY = "docmind_auth_token";

interface AuthContextType {
  user: AuthUser | null;
  token: string | null;
  health: HealthStatus | null;
  healthError: string | null;
  authNotice: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  clearAuthNotice: () => void;
  refreshHealth: () => Promise<HealthStatus | null>;
  invalidateSession: (notice?: string) => void;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, confirmation: string) => Promise<string>;
  logout: () => Promise<string>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);
  const [authNotice, setAuthNotice] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const clearClientStorage = useCallback(() => {
    if (typeof window === "undefined") return;
    sessionStorage.removeItem(SESSION_TOKEN_KEY);
    // Clean up any legacy demo localStorage items if present in the browser.
    localStorage.removeItem("docmind_user");
    localStorage.removeItem("docmind_token");
    localStorage.removeItem("docmind_documents");
    localStorage.removeItem("docmind_messages");
    localStorage.removeItem("docmind_collections");
    localStorage.removeItem("docmind_session_id");
  }, []);

  const refreshHealth = useCallback(async (): Promise<HealthStatus | null> => {
    try {
      const h = await getHealth();
      setHealth(h);
      setHealthError(null);
      return h;
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Backend service unavailable.";
      setHealthError(msg);
      return null;
    }
  }, []);

  const invalidateSession = useCallback(
    (notice?: string) => {
      clearClientStorage();
      setUser(null);
      setToken(null);
      if (notice) {
        setAuthNotice(notice);
      }
    },
    [clearClientStorage]
  );

  useEffect(() => {
    let active = true;

    async function initAuth() {
      // Remove legacy unverified demo storage immediately
      if (typeof window !== "undefined") {
        localStorage.removeItem("docmind_user");
        localStorage.removeItem("docmind_token");
        localStorage.removeItem("docmind_documents");
        localStorage.removeItem("docmind_messages");
        localStorage.removeItem("docmind_collections");
        localStorage.removeItem("docmind_session_id");
      }

      const h = await refreshHealth();
      if (!active) return;

      const savedToken =
        typeof window !== "undefined" ? sessionStorage.getItem(SESSION_TOKEN_KEY) : null;

      if (!savedToken) {
        setIsLoading(false);
        return;
      }

      if (h && !h.auth_configured) {
        invalidateSession("Account sign-in is not configured yet. Please contact the app owner.");
        setIsLoading(false);
        return;
      }

      try {
        const res = await getMe(savedToken);
        if (!active) return;
        setToken(savedToken);
        setUser(res.user);
      } catch (err) {
        if (!active) return;
        const msg =
          err instanceof ApiError
            ? err.message
            : "Your session could not be verified. Please sign in again.";
        invalidateSession(msg);
      } finally {
        if (active) {
          setIsLoading(false);
        }
      }
    }

    initAuth();
    return () => {
      active = false;
    };
  }, [invalidateSession, refreshHealth]);

  const login = async (email: string, password: string): Promise<void> => {
    const res = await loginUser(email, password);
    clearClientStorage();
    sessionStorage.setItem(SESSION_TOKEN_KEY, res.token);
    setToken(res.token);
    setUser(res.user);
    setAuthNotice(null);
  };

  const signup = async (
    email: string,
    password: string,
    confirmation: string
  ): Promise<string> => {
    const res = await signupUser(email, password, confirmation);
    return res.message;
  };

  const logout = async (): Promise<string> => {
    const currentToken = token;
    clearClientStorage();
    setUser(null);
    setToken(null);

    let notice = "You have been signed out.";
    if (currentToken) {
      try {
        const res = await logoutUser(currentToken);
        notice = res.notice;
      } catch {
        notice = "Signed out locally. Remote sign-out could not be confirmed.";
      }
    }
    setAuthNotice(notice);
    return notice;
  };

  const clearAuthNotice = () => setAuthNotice(null);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        health,
        healthError,
        authNotice,
        isAuthenticated: !!user && !!token,
        isLoading,
        clearAuthNotice,
        refreshHealth,
        invalidateSession,
        login,
        signup,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}
