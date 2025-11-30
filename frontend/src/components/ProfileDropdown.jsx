import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProfileDropdown = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const getInitials = (name) => {
    if (!name) return 'U';
    const parts = name.trim().split(' ');
    if (parts.length === 1) return parts[0].charAt(0).toUpperCase();
    return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
  };

  const handleProfileClick = () => {
    setIsOpen(false);
    navigate('/profile');
  };

  const handleLogout = () => {
    setIsOpen(false);
    logout();
  };

  const profileImageUrl = user?.profile?.profile_image_url || user?.profile_image_url;
  const userName = user?.profile?.full_name || user?.full_name || user?.email || '';

  return (
    <div className="profile-dropdown-container" ref={dropdownRef}>
      <button
        className="profile-avatar-btn"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        {profileImageUrl ? (
          <img
            src={profileImageUrl}
            alt="Profile"
            className="profile-avatar-img"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'flex';
            }}
          />
        ) : null}
        <span
          className="profile-avatar-initials"
          style={{ display: profileImageUrl ? 'none' : 'flex' }}
        >
          {getInitials(userName)}
        </span>
      </button>

      {isOpen && (
        <div className="profile-dropdown-menu">
          <div className="dropdown-user-info">
            <span className="dropdown-user-name">{userName || 'User'}</span>
            <span className="dropdown-user-email">{user?.email}</span>
          </div>
          <div className="dropdown-divider"></div>
          <button className="dropdown-item" onClick={handleProfileClick}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
            Profile
          </button>
          <button className="dropdown-item dropdown-item-logout" onClick={handleLogout}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
              <polyline points="16 17 21 12 16 7"></polyline>
              <line x1="21" y1="12" x2="9" y2="12"></line>
            </svg>
            Logout
          </button>
        </div>
      )}

      <style jsx>{`
        .profile-dropdown-container {
          position: relative;
          font-family: 'Inter', sans-serif;
        }

        .profile-avatar-btn {
          width: 38px;
          height: 38px;
          border-radius: 50%;
          border: 1px solid rgba(196, 191, 192, 0.3);
          background: linear-gradient(135deg, #4075C9 0%, #2a5699 100%);
          cursor: pointer;
          padding: 0;
          overflow: hidden;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.3s ease;
        }

        .profile-avatar-btn:hover {
          border-color: #4075C9;
          transform: scale(1.05);
          box-shadow: 0 0 20px rgba(64, 117, 201, 0.3);
        }

        .profile-avatar-img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .profile-avatar-initials {
          color: #ffffff;
          font-family: 'Inter', sans-serif;
          font-size: 13px;
          font-weight: 600;
          display: flex;
          align-items: center;
          justify-content: center;
          width: 100%;
          height: 100%;
        }

        .profile-dropdown-menu {
          position: absolute;
          top: calc(100% + 10px);
          right: 0;
          min-width: 200px;
          background: rgba(10, 10, 18, 0.98);
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          border: 1px solid rgba(64, 117, 201, 0.2);
          border-radius: 4px;
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
          overflow: hidden;
          animation: dropdownFadeIn 0.2s ease-out;
          z-index: 1000;
        }

        @keyframes dropdownFadeIn {
          from {
            opacity: 0;
            transform: translateY(-8px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .dropdown-user-info {
          padding: 14px 16px;
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .dropdown-user-name {
          font-family: 'Inter', sans-serif;
          font-size: 13px;
          font-weight: 600;
          color: #ffffff;
        }

        .dropdown-user-email {
          font-family: 'Inter', sans-serif;
          font-size: 11px;
          color: #C4BFC0;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .dropdown-divider {
          height: 1px;
          background: rgba(64, 117, 201, 0.15);
          margin: 0;
        }

        .dropdown-item {
          width: 100%;
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 10px 16px;
          background: transparent;
          border: none;
          color: #C4BFC0;
          font-family: 'Inter', sans-serif;
          font-size: 13px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.3s ease;
          text-align: left;
        }

        .dropdown-item:hover {
          background: rgba(64, 117, 201, 0.1);
          color: #ffffff;
        }

        .dropdown-item svg {
          opacity: 0.7;
          flex-shrink: 0;
        }

        .dropdown-item:hover svg {
          opacity: 1;
        }

        .dropdown-item-logout:hover {
          background: rgba(239, 68, 68, 0.1);
          color: #ef4444;
        }

        .dropdown-item-logout:hover svg {
          stroke: #ef4444;
        }
      `}</style>
    </div>
  );
};

export default ProfileDropdown;
