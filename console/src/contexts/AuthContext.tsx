import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { authApi, User } from "../api/modules/auth";
import { setApiToken, isAuthenticated as checkIsAuthenticated } from "../api/config";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  authenticated: boolean;
  authEnabled: boolean;
  allowRegistration: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);
  const [authEnabled, setAuthEnabled] = useState(false);
  const [allowRegistration, setAllowRegistration] = useState(true);

  const checkAuth = async () => {
    try {
      const status = await authApi.getStatus();
      setAuthEnabled(status.enabled);
      setAllowRegistration(status.allow_registration);

      if (status.authenticated && status.user) {
        setUser(status.user);
        setAuthenticated(true);
      } else if (checkIsAuthenticated() && !status.enabled) {
        // Auth was disabled, clear token
        setApiToken(null);
        setUser(null);
        setAuthenticated(false);
      }
    } catch (error) {
      console.error("Failed to check auth status:", error);
      // On error, assume auth is disabled to prevent lockout
      setAuthEnabled(false);
      setAllowRegistration(true);
      setAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const login = async (username: string, password: string) => {
    const response = await authApi.login({ username, password });
    setApiToken(response.access_token);
    setUser(response.user);
    setAuthenticated(true);
  };

  const register = async (username: string, password: string) => {
    const response = await authApi.register({ username, password });
    setApiToken(response.access_token);
    setUser(response.user);
    setAuthenticated(true);
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      setApiToken(null);
      setUser(null);
      setAuthenticated(false);
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        authenticated,
        authEnabled,
        allowRegistration,
        login,
        register,
        logout,
        checkAuth,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

export default AuthContext;
