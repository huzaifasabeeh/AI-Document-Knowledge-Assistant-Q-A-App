"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { UserProfile } from "./types";

interface AuthContextType {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, pass: string) => Promise<boolean>;
  signup: (name: string, email: string, pass: string) => Promise<boolean>;
  logout: () => void;
  updateProfile: (profile: Partial<UserProfile>) => void;
}

const defaultUser: UserProfile = {
  name: "Alex Morgan",
  email: "alex.morgan@acme.co",
  avatarUrl: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&auto=format&fit=crop&q=80",
  workspaceName: "Personal workspace",
  storageUsedMb: 128,
  storageLimitMb: 1024,
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Session persistence across browser refresh
    const saved = localStorage.getItem("docmind_user");
    if (saved) {
      try {
        setUser(JSON.parse(saved));
      } catch {
        setUser(defaultUser);
        localStorage.setItem("docmind_user", JSON.stringify(defaultUser));
      }
    } else {
      // Default logged in session so user immediately lands on workspace
      setUser(defaultUser);
      localStorage.setItem("docmind_user", JSON.stringify(defaultUser));
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string): Promise<boolean> => {
    const updated = {
      ...defaultUser,
      email: email || defaultUser.email,
    };
    setUser(updated);
    localStorage.setItem("docmind_user", JSON.stringify(updated));
    return true;
  };

  const signup = async (name: string, email: string): Promise<boolean> => {
    const updated = {
      ...defaultUser,
      name: name || defaultUser.name,
      email: email || defaultUser.email,
    };
    setUser(updated);
    localStorage.setItem("docmind_user", JSON.stringify(updated));
    return true;
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("docmind_user");
  };

  const updateProfile = (profile: Partial<UserProfile>) => {
    if (!user) return;
    const updated = { ...user, ...profile };
    setUser(updated);
    localStorage.setItem("docmind_user", JSON.stringify(updated));
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        signup,
        logout,
        updateProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
