import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../styles/auth.css';

const AuthPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, signup } = useAuth();
  const navigate = useNavigate();

  // Login form state
  const [loginData, setLoginData] = useState({
    email: '',
    password: '',
  });

  // Signup form state
  const [signupData, setSignupData] = useState({
    fullName: '',
    email: '',
    password: '',
    referralCode: '',
  });

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const result = await login(loginData.email, loginData.password);

      if (result.success) {
        const userData = result.user;
        if (userData && !userData.profile?.onboarding_completed) {
          navigate('/onboarding');
        } else {
          navigate('/');
        }
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSignupSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (signupData.password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setLoading(true);

    try {
      const result = await signup(signupData);

      if (result.success) {
        const loginResult = await login(signupData.email, signupData.password);

        if (loginResult.success) {
          navigate('/onboarding');
        } else {
          setError('Account created! Please login.');
          setIsLogin(true);
          setLoginData({ email: signupData.email, password: '' });
        }
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      {/* Left Side - Group Image */}
      <div className="auth-image-side">
        <img
          src="/assets/0Y6A2762-Enhanced-NR.jpg"
          alt="THINK Group"
          className="auth-group-image"
        />
        <div className="auth-image-overlay"></div>
      </div>

      {/* Right Side - Auth Form */}
      <div className="auth-form-side">
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
            <span className="auth-label">WELCOME TO</span>
            <h1 className="auth-title">THINKedIn</h1>
            <div className="auth-divider"></div>
            <p className="auth-subtitle">Connect with Purdue THINK members and alumni</p>
          </div>

          {/* Tab Switcher */}
          <div className="auth-tabs">
            <button
              className={`auth-tab ${isLogin ? 'active' : ''}`}
              onClick={() => {
                setIsLogin(true);
                setError('');
              }}
            >
              Login
            </button>
            <button
              className={`auth-tab ${!isLogin ? 'active' : ''}`}
              onClick={() => {
                setIsLogin(false);
                setError('');
              }}
            >
              Sign Up
            </button>
          </div>

          {/* Error Message */}
          {error && <div className="auth-error">{error}</div>}

          {/* Login Form */}
          {isLogin && (
            <form onSubmit={handleLoginSubmit} className="auth-form">
              <div className="form-group">
                <label htmlFor="loginEmail" className="form-label">
                  Email
                </label>
                <input
                  type="email"
                  id="loginEmail"
                  className="form-input"
                  placeholder="your.email@example.com"
                  value={loginData.email}
                  onChange={(e) => setLoginData({ ...loginData, email: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="loginPassword" className="form-label">
                  Password
                </label>
                <input
                  type="password"
                  id="loginPassword"
                  className="form-input"
                  placeholder="Enter your password"
                  value={loginData.password}
                  onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                  required
                />
                <a href="/forgot-password" className="forgot-link">
                  Forgot password?
                </a>
              </div>

              <button type="submit" className="auth-submit-btn" disabled={loading}>
                {loading ? (
                  <>
                    <span className="loading-spinner"></span>Signing in...
                  </>
                ) : (
                  'Sign In'
                )}
              </button>
            </form>
          )}

          {/* Signup Form */}
          {!isLogin && (
            <form onSubmit={handleSignupSubmit} className="auth-form">
              <div className="form-group">
                <label htmlFor="signupName" className="form-label">
                  Full Name
                </label>
                <input
                  type="text"
                  id="signupName"
                  className="form-input"
                  placeholder="John Doe"
                  value={signupData.fullName}
                  onChange={(e) => setSignupData({ ...signupData, fullName: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="signupEmail" className="form-label">
                  Email
                </label>
                <input
                  type="email"
                  id="signupEmail"
                  className="form-input"
                  placeholder="your.email@example.com"
                  value={signupData.email}
                  onChange={(e) => setSignupData({ ...signupData, email: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="signupPassword" className="form-label">
                  Password
                </label>
                <input
                  type="password"
                  id="signupPassword"
                  className="form-input"
                  placeholder="At least 8 characters"
                  value={signupData.password}
                  onChange={(e) => setSignupData({ ...signupData, password: e.target.value })}
                  required
                  minLength={8}
                />
              </div>

              <div className="form-group">
                <label htmlFor="referralCode" className="form-label">
                  Referral Code
                </label>
                <input
                  type="text"
                  id="referralCode"
                  className="form-input"
                  placeholder="Enter referral code"
                  value={signupData.referralCode}
                  onChange={(e) => setSignupData({ ...signupData, referralCode: e.target.value })}
                  required
                />
              </div>

              <button type="submit" className="auth-submit-btn" disabled={loading}>
                {loading ? (
                  <>
                    <span className="loading-spinner"></span>Creating account...
                  </>
                ) : (
                  'Create Account'
                )}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default AuthPage;
