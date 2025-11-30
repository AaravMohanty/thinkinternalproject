import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { authAPI } from '../utils/api';
import '../styles/auth.css';

const ResetPasswordPage = () => {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [accessToken, setAccessToken] = useState('');
  const [isValidLink, setIsValidLink] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // Get access token from URL hash (Supabase sends it as #access_token=...)
    const hashParams = new URLSearchParams(location.hash.substring(1));
    const token = hashParams.get('access_token');
    const type = hashParams.get('type');

    if (!token || type !== 'recovery') {
      setMessage({ type: 'error', text: 'Invalid or expired password reset link. Please request a new one.' });
      setIsValidLink(false);
    } else {
      setAccessToken(token);
    }
  }, [location]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage({ type: '', text: '' });

    if (password.length < 8) {
      setMessage({ type: 'error', text: 'Password must be at least 8 characters long' });
      return;
    }

    if (password !== confirmPassword) {
      setMessage({ type: 'error', text: 'Passwords do not match' });
      return;
    }

    setLoading(true);

    try {
      const result = await authAPI.resetPassword(accessToken, password);

      if (result.success) {
        setMessage({ type: 'success', text: 'Password reset successfully! Redirecting to login...' });
        setPassword('');
        setConfirmPassword('');

        // Redirect to login after 2 seconds
        setTimeout(() => {
          navigate('/auth');
        }, 2000);
      } else {
        setMessage({ type: 'error', text: result.error || 'Failed to reset password. Please try again.' });
      }
    } catch (error) {
      console.error('Reset password error:', error);
      setMessage({ type: 'error', text: 'Network error. Please check your connection and try again.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page forgot-password-page">
      {/* Background Light Rays */}
      <div className="forgot-bg">
        <div className="light-ray ray-1"></div>
        <div className="light-ray ray-2"></div>
      </div>

      {/* Centered Form */}
      <div className="forgot-form-wrapper">
        <div className="auth-form-container">
          {/* Logo */}
          <div className="auth-logo-wrapper">
            <img
              src="/assets/Copy of P logo for medium or dark background (1).png"
              alt="PurdueTHINK Logo"
              className="auth-logo"
            />
          </div>

          {/* Header */}
          <div className="auth-header">
            <span className="auth-label">SECURE YOUR ACCOUNT</span>
            <h1 className="auth-title">New Password</h1>
            <div className="auth-divider"></div>
            <p className="auth-subtitle">
              Enter your new password below. Make sure it's at least 8 characters.
            </p>
          </div>

          {/* Messages */}
          {message.text && (
            <div className={message.type === 'error' ? 'auth-error' : 'auth-success'}>
              {message.text}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label htmlFor="password" className="form-label">New Password</label>
              <input
                type="password"
                id="password"
                className="form-input"
                placeholder="Enter new password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={8}
                disabled={!isValidLink}
              />
              <span className="form-hint">Must be at least 8 characters</span>
            </div>

            <div className="form-group">
              <label htmlFor="confirmPassword" className="form-label">Confirm Password</label>
              <input
                type="password"
                id="confirmPassword"
                className="form-input"
                placeholder="Confirm new password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength={8}
                disabled={!isValidLink}
              />
            </div>

            <button type="submit" className="auth-submit-btn" disabled={loading || !isValidLink}>
              {loading ? (
                <>
                  <span className="loading-spinner"></span>Resetting...
                </>
              ) : (
                'Reset Password'
              )}
            </button>
          </form>

          {/* Back Link */}
          <button
            className="back-to-login-btn"
            onClick={() => navigate('/auth')}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M19 12H5M12 19l-7-7 7-7" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Back to Login
          </button>
        </div>
      </div>
    </div>
  );
};

export default ResetPasswordPage;
