/**
 * Authentication Utility Module
 * Handles JWT token storage, session management, and API authentication
 */

const API_BASE_URL = 'http://localhost:5001';

const Auth = {
  /**
   * Store authentication token in localStorage
   */
  setToken(token) {
    localStorage.setItem('think_auth_token', token);
  },

  /**
   * Get authentication token from localStorage
   */
  getToken() {
    return localStorage.getItem('think_auth_token');
  },

  /**
   * Store refresh token in localStorage
   */
  setRefreshToken(token) {
    localStorage.setItem('think_refresh_token', token);
  },

  /**
   * Get refresh token from localStorage
   */
  getRefreshToken() {
    return localStorage.getItem('think_refresh_token');
  },

  /**
   * Remove authentication token
   */
  clearToken() {
    localStorage.removeItem('think_auth_token');
    localStorage.removeItem('think_refresh_token');
    localStorage.removeItem('think_user_data');
  },

  /**
   * Store user data in localStorage
   */
  setUserData(userData) {
    localStorage.setItem('think_user_data', JSON.stringify(userData));
  },

  /**
   * Get user data from localStorage
   */
  getUserData() {
    const data = localStorage.getItem('think_user_data');
    return data ? JSON.parse(data) : null;
  },

  /**
   * Check if user is authenticated (has valid token)
   */
  isAuthenticated() {
    return !!this.getToken();
  },

  /**
   * Check if user is a director
   */
  isDirector() {
    const userData = this.getUserData();
    return userData && userData.is_director === true;
  },

  /**
   * Login with email and password
   * @param {string} email
   * @param {string} password
   * @returns {Promise<{success: boolean, error?: string}>}
   */
  async login(email, password) {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok && data.success && data.user && data.user.session) {
        // Store tokens and user data
        this.setToken(data.user.session.access_token);
        this.setRefreshToken(data.user.session.refresh_token);
        this.setUserData(data.user);

        return { success: true, user: data.user };
      } else {
        return {
          success: false,
          error: data.error || 'Login failed. Please check your credentials.',
        };
      }
    } catch (error) {
      console.error('Login error:', error);
      return {
        success: false,
        error: 'Network error. Please check your connection and try again.',
      };
    }
  },

  /**
   * Sign up with email, password, and referral code
   * @param {Object} signupData - {email, password, referralCode, fullName}
   * @returns {Promise<{success: boolean, error?: string}>}
   */
  async signup(signupData) {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: signupData.email,
          password: signupData.password,
          referral_code: signupData.referralCode,
          full_name: signupData.fullName,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        return { success: true, message: data.message };
      } else {
        return {
          success: false,
          error: data.error || 'Signup failed. Please try again.',
        };
      }
    } catch (error) {
      console.error('Signup error:', error);
      return {
        success: false,
        error: 'Network error. Please check your connection and try again.',
      };
    }
  },

  /**
   * Logout - clear token and redirect to login
   */
  async logout() {
    try {
      const token = this.getToken();

      if (token) {
        // Call backend logout endpoint
        await fetch(`${API_BASE_URL}/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear local storage regardless of backend response
      this.clearToken();
      window.location.href = 'login.html';
    }
  },

  /**
   * Refresh the session using the stored refresh token
   * @returns {Promise<{success: boolean, user?: Object}>}
   */
  async refreshSession() {
    try {
      const refreshToken = this.getRefreshToken();

      if (!refreshToken) {
        return { success: false };
      }

      const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success && data.user && data.user.session) {
          // Store new tokens
          this.setToken(data.user.session.access_token);
          this.setRefreshToken(data.user.session.refresh_token);
          this.setUserData(data.user);
          return { success: true, user: data.user };
        }
      }

      return { success: false };
    } catch (error) {
      console.error('Session refresh error:', error);
      return { success: false };
    }
  },

  /**
   * Get current user session from backend
   * @returns {Promise<{user: Object} | null>}
   */
  async getCurrentUser() {
    try {
      const token = this.getToken();

      if (!token) {
        return null;
      }

      const response = await fetch(`${API_BASE_URL}/auth/session`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        // Update stored user data
        this.setUserData(data.user);
        return data;
      } else if (response.status === 401) {
        // Token expired - try to refresh
        console.log('Access token expired, attempting refresh...');
        const refreshResult = await this.refreshSession();

        if (refreshResult.success) {
          console.log('Session refreshed successfully');
          return { user: refreshResult.user };
        }

        // Refresh failed, clear everything
        this.clearToken();
        return null;
      } else {
        return null;
      }
    } catch (error) {
      console.error('Get current user error:', error);
      return null;
    }
  },

  /**
   * Make an authenticated API request
   * @param {string} endpoint - API endpoint (e.g., '/api/profile')
   * @param {Object} options - Fetch options (method, body, etc.)
   * @returns {Promise<Response>}
   */
  async authenticatedFetch(endpoint, options = {}) {
    let token = this.getToken();

    if (!token) {
      throw new Error('Not authenticated');
    }

    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options.headers,
    };

    let response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    // If unauthorized, try to refresh the token
    if (response.status === 401) {
      console.log('Request returned 401, attempting token refresh...');
      const refreshResult = await this.refreshSession();

      if (refreshResult.success) {
        // Retry the request with the new token
        token = this.getToken();
        headers['Authorization'] = `Bearer ${token}`;

        response = await fetch(`${API_BASE_URL}${endpoint}`, {
          ...options,
          headers,
        });

        if (response.status === 401) {
          // Still unauthorized after refresh - give up
          this.clearToken();
          window.location.href = 'login.html';
          throw new Error('Session expired');
        }
      } else {
        // Refresh failed, redirect to login
        this.clearToken();
        window.location.href = 'login.html';
        throw new Error('Session expired');
      }
    }

    return response;
  },

  /**
   * Require authentication - redirect to login if not authenticated
   * Call this at the top of protected pages
   */
  requireAuth() {
    if (!this.isAuthenticated()) {
      window.location.href = 'login.html';
      return false;
    }
    return true;
  },

  /**
   * Require director role - redirect to home if not a director
   * Call this on admin pages
   */
  requireDirector() {
    if (!this.isAuthenticated()) {
      window.location.href = 'login.html';
      return false;
    }

    if (!this.isDirector()) {
      window.location.href = 'home.html';
      return false;
    }

    return true;
  },

  /**
   * Initialize user session on page load
   * Fetches current user data and updates localStorage
   * @returns {Promise<Object|null>} User data or null if not authenticated
   */
  async init() {
    if (!this.isAuthenticated()) {
      return null;
    }

    const session = await this.getCurrentUser();

    if (!session) {
      this.clearToken();
      return null;
    }

    return session.user;
  },
};

// Expose Auth globally for use in HTML script tags
window.Auth = Auth;
