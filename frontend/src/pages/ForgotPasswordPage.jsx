import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../utils/api';
import '../styles/auth.css';

const ForgotPasswordPage = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage({ type: '', text: '' });

    if (!email || !email.includes('@')) {
      setMessage({ type: 'error', text: 'Please enter a valid email address' });
      return;
    }

    setLoading(true);

    try {
      const result = await authAPI.forgotPassword(email);

      if (result.success) {
        setMessage({ type: 'success', text: result.message || 'Password reset link sent! Please check your email.' });
        setEmail('');

        // Redirect to login after 5 seconds
        setTimeout(() => {
          navigate('/auth');
        }, 5000);
      } else {
        setMessage({ type: 'error', text: result.error || 'Failed to send reset link. Please try again.' });
      }
    } catch (error) {
      console.error('Forgot password error:', error);
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
            <span className="auth-label">ACCOUNT RECOVERY</span>
            <h1 className="auth-title">Reset Password</h1>
            <div className="auth-divider"></div>
            <p className="auth-subtitle">
              Enter your email address and we'll send you a link to reset your password.
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
              <label htmlFor="email" className="form-label">Email Address</label>
              <input
                type="email"
                id="email"
                className="form-input"
                placeholder="your.email@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
              />
            </div>

            <button type="submit" className="auth-submit-btn" disabled={loading}>
              {loading ? (
                <>
                  <span className="loading-spinner"></span>Sending...
                </>
              ) : (
                'Send Reset Link'
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

export default ForgotPasswordPage;
