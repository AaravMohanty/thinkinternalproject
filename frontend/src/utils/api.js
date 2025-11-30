// API utility functions
const API_BASE_URL = 'http://localhost:5001';

// Get auth token from localStorage
export const getToken = () => localStorage.getItem('auth_token');

// Set auth token
export const setToken = (token) => localStorage.setItem('auth_token', token);

// Remove auth token
export const removeToken = () => localStorage.removeItem('auth_token');

// Get refresh token from localStorage
export const getRefreshToken = () => localStorage.getItem('refresh_token');

// Set refresh token
export const setRefreshToken = (token) => localStorage.setItem('refresh_token', token);

// Remove refresh token
export const removeRefreshToken = () => localStorage.removeItem('refresh_token');

// Get user data from localStorage
export const getUserData = () => {
  const data = localStorage.getItem('user_data');
  return data ? JSON.parse(data) : null;
};

// Set user data
export const setUserData = (data) => {
  localStorage.setItem('user_data', JSON.stringify(data));
};

// Remove user data
export const removeUserData = () => {
  localStorage.removeItem('user_data');
};

// Check if user is authenticated
export const isAuthenticated = () => {
  return !!getToken();
};

// Refresh the session using refresh token
export const refreshSession = async () => {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    return { success: false };
  }

  try {
    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (response.ok) {
      const data = await response.json();
      if (data.success && data.user?.session) {
        setToken(data.user.session.access_token);
        setRefreshToken(data.user.session.refresh_token);
        setUserData(data.user);
        return { success: true, user: data.user };
      }
    }
    return { success: false };
  } catch (error) {
    console.error('Session refresh error:', error);
    return { success: false };
  }
};

// API request helper with auth and auto-refresh on 401
export const apiRequest = async (endpoint, options = {}) => {
  let token = getToken();

  const config = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };

  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }

  let response = await fetch(`${API_BASE_URL}${endpoint}`, config);

  // If 401, try to refresh the token
  if (response.status === 401) {
    console.log('Request returned 401, attempting token refresh...');
    const refreshResult = await refreshSession();

    if (refreshResult.success) {
      // Retry the request with new token
      token = getToken();
      config.headers['Authorization'] = `Bearer ${token}`;
      response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    } else {
      // Refresh failed - redirect to login
      removeToken();
      removeRefreshToken();
      removeUserData();
      window.location.href = '/auth';
      throw new Error('Session expired');
    }
  }

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || 'Request failed');
  }

  return data;
};

// Auth API calls
export const authAPI = {
  async login(email, password) {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();

    if (response.ok && data.success && data.user?.session) {
      setToken(data.user.session.access_token);
      setRefreshToken(data.user.session.refresh_token);
      setUserData(data.user);
      return { success: true, user: data.user };
    }

    return { success: false, error: data.error || 'Login failed' };
  },

  async signup(signupData) {
    const response = await fetch(`${API_BASE_URL}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
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
    }

    return { success: false, error: data.error || 'Signup failed' };
  },

  async logout() {
    removeToken();
    removeRefreshToken();
    removeUserData();
  },

  async forgotPassword(email) {
    return apiRequest('/auth/forgot-password', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  },

  async resetPassword(token, password) {
    const response = await fetch(`${API_BASE_URL}/auth/update-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ password }),
    });

    return response.json();
  },
};

// Profile API calls
export const profileAPI = {
  async get() {
    return apiRequest('/api/profile');
  },

  async update(profileData) {
    return apiRequest('/api/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
  },

  async uploadResume(file) {
    const formData = new FormData();
    formData.append('resume', file);

    const token = getToken();
    const response = await fetch(`${API_BASE_URL}/api/resume/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });

    return response.json();
  },

  // Search for potential matching alumni profiles in CSV data
  async matchProfile(fullName, email) {
    return apiRequest('/api/match-profile', {
      method: 'POST',
      body: JSON.stringify({ full_name: fullName, email }),
    });
  },

  // Link user's account to an existing CSV alumni record
  async linkProfile(csvIndex) {
    return apiRequest('/api/link-profile', {
      method: 'POST',
      body: JSON.stringify({ csv_index: csvIndex }),
    });
  },

  // Delete user's own account
  async deleteAccount() {
    return apiRequest('/api/account', {
      method: 'DELETE',
    });
  },
};

// Alumni API calls
export const alumniAPI = {
  async getAll(filters = {}) {
    const params = new URLSearchParams(filters);
    return apiRequest(`/api/alumni?${params}`);
  },

  async getFilters() {
    return apiRequest('/api/filters');
  },

  // Get AI-powered alumni recommendations
  async getRecommendations(excludeIds = [], count = 10) {
    return apiRequest('/api/recommendations', {
      method: 'POST',
      body: JSON.stringify({ exclude_ids: excludeIds, count }),
    });
  },

  // Generate AI-powered networking email
  async generateEmail(alumniData) {
    return apiRequest('/api/generate-email', {
      method: 'POST',
      body: JSON.stringify({ alumni: alumniData }),
    });
  },
};

// Chat API calls
export const chatAPI = {
  // Send a message to the AI advisor
  async sendMessage(message, sessionId = null) {
    return apiRequest('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ message, session_id: sessionId }),
    });
  },

  // Get chat history
  async getHistory(sessionId = null) {
    const params = sessionId ? `?session_id=${sessionId}` : '';
    return apiRequest(`/api/chat/history${params}`);
  },

  // Start a new chat session
  async newSession() {
    return apiRequest('/api/chat/new', {
      method: 'POST',
    });
  },
};

// Admin API calls (Directors only)
export const adminAPI = {
  // Get platform settings (referral code, etc.)
  async getSettings() {
    return apiRequest('/admin/settings');
  },

  // Update referral code
  async updateReferralCode(newCode) {
    return apiRequest('/admin/settings/referral-code', {
      method: 'PUT',
      body: JSON.stringify({ referral_code: newCode }),
    });
  },

  // Get all members
  async getMembers() {
    return apiRequest('/admin/members');
  },

  // Delete a member (complete removal)
  async deleteMember(userId) {
    return apiRequest(`/admin/members/${userId}`, {
      method: 'DELETE',
    });
  },

  // Promote member to director
  async promoteToDirector(userId) {
    return apiRequest(`/admin/promote-director/${userId}`, {
      method: 'POST',
    });
  },

  // Demote director to member
  async demoteDirector(userId) {
    return apiRequest(`/admin/demote-director/${userId}`, {
      method: 'POST',
    });
  },

  // Get audit log
  async getAuditLog(limit = 100) {
    return apiRequest(`/admin/audit-log?limit=${limit}`);
  },
};
