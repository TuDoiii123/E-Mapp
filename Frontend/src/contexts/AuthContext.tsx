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

  useEffect(() => {
    const checkAuth = async () => {
      const token = getToken();
      if (token) {
        try {
          const response = await authAPI.getProfile();
          if (response.success) {
            setUser(response.data.user);
          } else {
            removeToken();
          }
        } catch {
          // Token expired or invalid — clear it
          removeToken();
        }
      }
      setIsLoading(false);
    };

    checkAuth();
  }, []);

  const login = async (cccdNumber: string, password: string) => {
    const response = await authAPI.login({ cccdNumber, password });
    if (response.success) {
      setUser(response.data.user);
    } else {
      throw new Error(response.message || 'Đăng nhập thất bại');
    }
  };

  const register = async (userData: any) => {
    const response = await authAPI.register(userData);
    if (response.success) {
      setUser(response.data.user);
    } else {
      throw new Error(response.message || 'Đăng ký thất bại');
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch {
      removeToken();
    } finally {
      setUser(null);
    }
  };

  const refreshProfile = async () => {
    try {
      const response = await authAPI.getProfile();
      if (response.success) {
        setUser(response.data.user);
      }
    } catch {
      // Profile refresh failed silently
    }
  };

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated: !!user || !!getToken(),
      isLoading,
      login,
      register,
      logout,
      refreshProfile,
    }}>
      {children}
    </AuthContext.Provider>
  );
};
