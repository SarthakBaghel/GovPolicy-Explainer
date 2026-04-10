"use client";

import { useEffect, useState } from "react";
import { clearToken, getToken, setToken } from "@/lib/auth";

export function useAuth() {
  const [token, setTokenState] = useState<string | null>(null);

  useEffect(() => {
    setTokenState(getToken());
  }, []);

  const saveToken = (value: string) => {
    setToken(value);
    setTokenState(value);
  };

  const logout = () => {
    clearToken();
    setTokenState(null);
  };

  return {
    token,
    isAuthenticated: Boolean(token),
    saveToken,
    logout,
  };
}
