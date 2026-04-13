// contexts/AuthContext.tsx
// stores auth token + profile id so all screens can use it

import React, { createContext, useContext, useState } from 'react';

type AuthContextType = {
  token: string | null;
  profileId: number | null;
  login: (token: string, profileId: number) => void;
  logout: () => void;
};

// default context values (before login)
const AuthContext = createContext<AuthContextType>({
  token: null,
  profileId: null,
  login: () => {},
  logout: () => {},
});

// wrap the app with this to share login state
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [profileId, setProfileId] = useState<number | null>(null);

  const login = (t: string, id: number) => {
    setToken(t);
    setProfileId(id);
  };

  const logout = () => {
    setToken(null);
    setProfileId(null);
  };

  return (
    <AuthContext.Provider value={{ token, profileId, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// hook to use in any screen
export function useAuth() {
  return useContext(AuthContext);
}
