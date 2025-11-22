import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authAPI, User, getToken, removeToken } from '../services/api';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (cccdNumber: string, password: string) => Promise<void>;
  register: (userData: any) => Promise<void>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check if user is authenticated on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = getToken();
      if (token) {
        // Temporarily skip fetching profile from server.
        // We keep the token and treat presence of token as authenticated
        // for now; user details will be null until a profile endpoint
        // is re-enabled.
        setUser(null);
      }
      setIsLoading(false);
    };

    checkAuth();
  }, []);

  const login = async (cccdNumber: string, password: string) => {
    try {
      const response = await authAPI.login({ cccdNumber, password });
      if (response.success) {
        setUser(response.data.user);
      } else {
        throw new Error(response.message || 'Đăng nhập thất bại');
      }
    } catch (error: any) {
      throw error;
    }
  };

  const register = async (userData: any) => {
    try {
      const response = await authAPI.register(userData);
      if (response.success) {
        setUser(response.data.user);
      } else {
        throw new Error(response.message || 'Đăng ký thất bại');
      }
    } catch (error: any) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      removeToken();
    }
  };

  const refreshProfile = async () => {
    // Temporarily disabled while profile endpoints are removed
    console.warn('refreshProfile is temporarily disabled');
    return;
  };

  const value: AuthContextType = {
    user,
    // Consider token presence as authentication while profile fetch is disabled
    isAuthenticated: !!user || !!getToken(),
    isLoading,
    login,
    register,
    logout,
    refreshProfile,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

