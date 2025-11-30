import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI, apiRequest, isAuthenticated, getUserData, setUserData, refreshSession, removeToken, removeRefreshToken, removeUserData } from '../utils/api';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Validate session on mount
    const validateSession = async () => {
      if (!isAuthenticated()) {
        setLoading(false);
        return;
      }

      // First load from localStorage for faster initial render
      const userData = getUserData();
      if (userData) {
        setUser(userData);
      }

      // Then validate with server (will auto-refresh if needed)
      try {
        const response = await apiRequest('/auth/session');
        if (response.success && response.user) {
          setUser(response.user);
          setUserData(response.user);
        }
      } catch (error) {
        console.error('Session validation failed:', error);
        // Session is invalid, clear everything
        removeToken();
        removeRefreshToken();
        removeUserData();
        setUser(null);
      }

      setLoading(false);
    };

    validateSession();
  }, []);

  const login = async (email, password) => {
    const result = await authAPI.login(email, password);
    if (result.success) {
      setUser(result.user);
    }
    return result;
  };

  const signup = async (signupData) => {
    return await authAPI.signup(signupData);
  };

  const logout = () => {
    authAPI.logout();
    setUser(null);
  };

  const updateUser = (userData) => {
    setUser(userData);
    setUserData(userData);
  };

  const value = {
    user,
    loading,
    login,
    signup,
    logout,
    updateUser,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
