import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { adminAPI } from '../utils/api';
import ProfileDropdown from '../components/ProfileDropdown';
import '../styles/admin.css';
import '../styles/people.css';

const AdminPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('members');
  const [members, setMembers] = useState([]);
  const [settings, setSettings] = useState(null);
  const [auditLog, setAuditLog] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [newReferralCode, setNewReferralCode] = useState('');
  const [showDeleteModal, setShowDeleteModal] = useState(null);
  const [showPromoteModal, setShowPromoteModal] = useState(null);
  const [showDemoteModal, setShowDemoteModal] = useState(null);

  // Check if user is director
  useEffect(() => {
    if (user && !user.is_director) {
      navigate('/');
    }
  }, [user, navigate]);

  // Load initial data
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [membersRes, settingsRes, auditRes] = await Promise.all([
        adminAPI.getMembers(),
        adminAPI.getSettings(),
        adminAPI.getAuditLog(50),
      ]);

      if (membersRes.success) setMembers(membersRes.members || []);
      if (settingsRes.success) {
        setSettings(settingsRes.settings);
        setNewReferralCode(settingsRes.settings?.active_referral_code || '');
      }
      if (auditRes.success) setAuditLog(auditRes.actions || []);
    } catch (err) {
      setError('Failed to load admin data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateReferralCode = async () => {
    if (!newReferralCode.trim()) {
      setError('Referral code cannot be empty');
      return;
    }

    try {
      const res = await adminAPI.updateReferralCode(newReferralCode.trim());
      if (res.success) {
        setSuccess('Referral code updated successfully!');
        setSettings({ ...settings, active_referral_code: newReferralCode.trim() });
        setTimeout(() => setSuccess(''), 3000);
        loadData();
      } else {
        setError(res.error || 'Failed to update referral code');
      }
    } catch (err) {
      setError('Failed to update referral code');
    }
  };

  const handleDeleteMember = async (userId) => {
    try {
      const res = await adminAPI.deleteMember(userId);
      if (res.success) {
        setSuccess('Member deleted successfully!');
        setMembers(members.filter(m => m.user_id !== userId));
        setShowDeleteModal(null);
        setTimeout(() => setSuccess(''), 3000);
        loadData();
      } else {
        setError(res.error || 'Failed to delete member');
      }
    } catch (err) {
      setError('Failed to delete member');
    }
  };

  const handlePromote = async (userId) => {
    try {
      const res = await adminAPI.promoteToDirector(userId);
      if (res.success) {
        setSuccess('Member promoted to Director!');
        setMembers(members.map(m =>
          m.user_id === userId ? { ...m, is_director: true } : m
        ));
        setShowPromoteModal(null);
        setTimeout(() => setSuccess(''), 3000);
        loadData();
      } else {
        setError(res.error || 'Failed to promote member');
      }
    } catch (err) {
      setError('Failed to promote member');
    }
  };

  const handleDemote = async (userId) => {
    try {
      const res = await adminAPI.demoteDirector(userId);
      if (res.success) {
        setSuccess('Director demoted to Member!');
        setMembers(members.map(m =>
          m.user_id === userId ? { ...m, is_director: false } : m
        ));
        setShowDemoteModal(null);
        setTimeout(() => setSuccess(''), 3000);
        loadData();
      } else {
        setError(res.error || 'Failed to demote director');
      }
    } catch (err) {
      setError('Failed to demote director');
    }
  };

  const filteredMembers = members.filter(member => {
    const query = searchQuery.toLowerCase();
    const email = member.personal_email || member.email || '';
    return (
      member.full_name?.toLowerCase().includes(query) ||
      email.toLowerCase().includes(query) ||
      member.major?.toLowerCase().includes(query)
    );
  });

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getActionLabel = (actionType) => {
    const labels = {
      'SET_REFERRAL_CODE': 'Changed Referral Code',
      'REMOVE_MEMBER': 'Removed Member',
      'PROMOTE_DIRECTOR': 'Promoted to Director',
      'DEMOTE_DIRECTOR': 'Demoted Director',
    };
    return labels[actionType] || actionType;
  };

  if (!user?.is_director) {
    return (
      <div className="admin-page">
        <div className="page-background">
          <div className="light-ray ray-1"></div>
          <div className="light-ray ray-2"></div>
        </div>
        <nav className="main-nav">
          <Link to="/" className="nav-left">
            <img src="/assets/Copy of P logo for medium or dark background (1).png" alt="PurdueTHINK" className="nav-logo" />
            <span className="nav-title">THINKedIn</span>
          </Link>
          <div className="nav-right">
            <a href="/" className="nav-link" onClick={(e) => { e.preventDefault(); navigate('/'); }}>Alumni</a>
            <a href="/admin" className="nav-link active" onClick={(e) => { e.preventDefault(); navigate('/admin'); }}>Admin</a>
            <ProfileDropdown />
          </div>
        </nav>
        <div className="admin-error-container">
          <div className="admin-error">
            <h2>Access Denied</h2>
            <p>You must be a Director to access this page.</p>
            <button onClick={() => navigate('/')}>Go Home</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-page">
      {/* Background Light Rays */}
      <div className="page-background">
        <div className="light-ray ray-1"></div>
        <div className="light-ray ray-2"></div>
      </div>

      {/* Navigation */}
      <nav className="main-nav">
        <Link to="/" className="nav-left">
          <img src="/assets/Copy of P logo for medium or dark background (1).png" alt="PurdueTHINK" className="nav-logo" />
          <span className="nav-title">THINKedIn</span>
        </Link>
        <div className="nav-right">
          <a href="/" className="nav-link" onClick={(e) => { e.preventDefault(); navigate('/'); }}>Alumni</a>
          <a href="/admin" className="nav-link active" onClick={(e) => { e.preventDefault(); navigate('/admin'); }}>Admin</a>
          <ProfileDropdown />
        </div>
      </nav>

      {/* Page Header */}
      <header className="page-header">
        <div className="header-content">
          <div className="header-text">
            <span className="header-label">DIRECTOR</span>
            <h1 className="header-title">Admin Dashboard</h1>
            <div className="header-divider"></div>
            <p className="header-subtitle">Manage members, referral codes, and view audit logs</p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="admin-main">
        {/* Messages */}
        {error && (
          <div className="admin-message error">
            <span>{error}</span>
            <button onClick={() => setError('')}>&times;</button>
          </div>
        )}
        {success && (
          <div className="admin-message success">
            <span>{success}</span>
            <button onClick={() => setSuccess('')}>&times;</button>
          </div>
        )}

        {/* Tabs */}
        <div className="admin-tabs">
        <button
          className={`admin-tab ${activeTab === 'members' ? 'active' : ''}`}
          onClick={() => setActiveTab('members')}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
          Members ({members.length})
        </button>
        <button
          className={`admin-tab ${activeTab === 'referral' ? 'active' : ''}`}
          onClick={() => setActiveTab('referral')}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/>
          </svg>
          Referral Code
        </button>
        <button
          className={`admin-tab ${activeTab === 'audit' ? 'active' : ''}`}
          onClick={() => setActiveTab('audit')}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
            <polyline points="10 9 9 9 8 9"/>
          </svg>
          Audit Log
        </button>
      </div>

      {/* Content */}
      <div className="admin-content">
        {loading ? (
          <div className="admin-loading">
            <div className="admin-spinner"></div>
            <p>Loading...</p>
          </div>
        ) : (
          <>
            {/* Members Tab */}
            {activeTab === 'members' && (
              <div className="admin-section">
                <div className="admin-section-header">
                  <h2>Member Management</h2>
                  <div className="admin-search">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="11" cy="11" r="8"/>
                      <path d="M21 21l-4.35-4.35"/>
                    </svg>
                    <input
                      type="text"
                      placeholder="Search by name, email, or major..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                    />
                  </div>
                </div>

                <div className="admin-table-container">
                  <table className="admin-table">
                    <thead>
                      <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Major</th>
                        <th>Grad Year</th>
                        <th>Role</th>
                        <th>Joined</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredMembers.length === 0 ? (
                        <tr>
                          <td colSpan="7" className="admin-empty">
                            {searchQuery ? 'No members match your search' : 'No members found'}
                          </td>
                        </tr>
                      ) : (
                        filteredMembers.map((member) => (
                          <tr key={member.user_id} className={member.is_director ? 'director-row' : ''}>
                            <td>
                              <div className="member-name">
                                {member.full_name || 'N/A'}
                                {member.user_id === user?.user_id && <span className="you-badge">(You)</span>}
                              </div>
                            </td>
                            <td>{member.personal_email || member.email || 'N/A'}</td>
                            <td>{member.major || 'N/A'}</td>
                            <td>{member.graduation_year || 'N/A'}</td>
                            <td>
                              <span className={`role-badge ${member.is_director ? 'director' : 'member'}`}>
                                {member.is_director ? 'Director' : 'Member'}
                              </span>
                            </td>
                            <td>{formatDate(member.created_at)}</td>
                            <td>
                              <div className="action-buttons">
                                {member.user_id !== user?.user_id && (
                                  <>
                                    {member.is_director ? (
                                      <button
                                        className="action-btn demote"
                                        onClick={() => setShowDemoteModal(member)}
                                        title="Demote to Member"
                                      >
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                          <path d="M19 14l-7 7m0 0l-7-7m7 7V3"/>
                                        </svg>
                                      </button>
                                    ) : (
                                      <button
                                        className="action-btn promote"
                                        onClick={() => setShowPromoteModal(member)}
                                        title="Promote to Director"
                                      >
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                          <path d="M5 10l7-7m0 0l7 7m-7-7v18"/>
                                        </svg>
                                      </button>
                                    )}
                                    <button
                                      className="action-btn delete"
                                      onClick={() => setShowDeleteModal(member)}
                                      title="Delete Member"
                                    >
                                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <polyline points="3 6 5 6 21 6"/>
                                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                                        <line x1="10" y1="11" x2="10" y2="17"/>
                                        <line x1="14" y1="11" x2="14" y2="17"/>
                                      </svg>
                                    </button>
                                  </>
                                )}
                              </div>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Referral Code Tab */}
            {activeTab === 'referral' && (
              <div className="admin-section">
                <div className="admin-section-header">
                  <h2>Referral Code Management</h2>
                </div>

                <div className="referral-card">
                  <div className="referral-current">
                    <label>Current Active Code</label>
                    <div className="referral-code-display">
                      <span>{settings?.active_referral_code || 'Not set'}</span>
                      <button
                        className="copy-btn"
                        onClick={() => {
                          navigator.clipboard.writeText(settings?.active_referral_code || '');
                          setSuccess('Code copied to clipboard!');
                          setTimeout(() => setSuccess(''), 2000);
                        }}
                        title="Copy to clipboard"
                      >
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                        </svg>
                      </button>
                    </div>
                  </div>

                  <div className="referral-update">
                    <label>Update Referral Code</label>
                    <div className="referral-input-group">
                      <input
                        type="text"
                        value={newReferralCode}
                        onChange={(e) => setNewReferralCode(e.target.value.toUpperCase())}
                        placeholder="Enter new referral code"
                      />
                      <button
                        className="update-btn"
                        onClick={handleUpdateReferralCode}
                        disabled={!newReferralCode.trim() || newReferralCode === settings?.active_referral_code}
                      >
                        Update Code
                      </button>
                    </div>
                    <p className="referral-hint">
                      This code is required for new users to sign up. Share it with people you want to invite.
                    </p>
                  </div>

                  <div className="referral-info">
                    <h4>Special Director Codes</h4>
                    <p>Users who sign up with these codes automatically become Directors:</p>
                    <ul>
                      <li><code>OPS</code> - Director of Operations code</li>
                      <li><code>SUPER_OPS_2025</code> - Super Operations code</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {/* Audit Log Tab */}
            {activeTab === 'audit' && (
              <div className="admin-section">
                <div className="admin-section-header">
                  <h2>Audit Log</h2>
                  <button className="refresh-btn" onClick={loadData}>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M23 4v6h-6"/>
                      <path d="M1 20v-6h6"/>
                      <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
                    </svg>
                    Refresh
                  </button>
                </div>

                <div className="admin-table-container">
                  <table className="admin-table audit-table">
                    <thead>
                      <tr>
                        <th>Timestamp</th>
                        <th>Director</th>
                        <th>Action</th>
                        <th>Target</th>
                        <th>Details</th>
                      </tr>
                    </thead>
                    <tbody>
                      {auditLog.length === 0 ? (
                        <tr>
                          <td colSpan="5" className="admin-empty">No audit log entries</td>
                        </tr>
                      ) : (
                        auditLog.map((action) => (
                          <tr key={action.id}>
                            <td>{formatDate(action.timestamp)}</td>
                            <td>{action.director_name || action.director_user_id?.slice(0, 8) || 'System'}</td>
                            <td>
                              <span className={`action-badge ${action.action_type?.toLowerCase()}`}>
                                {getActionLabel(action.action_type)}
                              </span>
                            </td>
                            <td>{action.target_name || action.target_user_id?.slice(0, 8) || 'N/A'}</td>
                            <td className="details-cell">
                              {action.details ? (
                                <span title={JSON.stringify(action.details, null, 2)}>
                                  {action.details.reason || action.details.new_code || JSON.stringify(action.details).slice(0, 50)}
                                </span>
                              ) : 'N/A'}
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        )}
      </div>
      </main>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="admin-modal-overlay" onClick={() => setShowDeleteModal(null)}>
          <div className="admin-modal" onClick={(e) => e.stopPropagation()}>
            <h3>Delete Member</h3>
            <p>Are you sure you want to delete <strong>{showDeleteModal.full_name || showDeleteModal.email}</strong>?</p>
            <p className="warning">This will permanently remove all their data including:</p>
            <ul className="delete-list">
              <li>User profile and account</li>
              <li>Resume and uploaded files</li>
              <li>Chat history</li>
              <li>All connections and activity</li>
            </ul>
            <div className="modal-buttons">
              <button className="cancel-btn" onClick={() => setShowDeleteModal(null)}>
                Cancel
              </button>
              <button className="confirm-delete-btn" onClick={() => handleDeleteMember(showDeleteModal.user_id)}>
                Delete Permanently
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Promote Confirmation Modal */}
      {showPromoteModal && (
        <div className="admin-modal-overlay" onClick={() => setShowPromoteModal(null)}>
          <div className="admin-modal" onClick={(e) => e.stopPropagation()}>
            <h3>Promote to Director</h3>
            <p>Are you sure you want to promote <strong>{showPromoteModal.full_name || showPromoteModal.email}</strong> to Director?</p>
            <p className="info">Directors have full admin access including:</p>
            <ul>
              <li>Manage referral codes</li>
              <li>View and manage all members</li>
              <li>Promote/demote other directors</li>
              <li>Delete member accounts</li>
            </ul>
            <div className="modal-buttons">
              <button className="cancel-btn" onClick={() => setShowPromoteModal(null)}>
                Cancel
              </button>
              <button className="confirm-promote-btn" onClick={() => handlePromote(showPromoteModal.user_id)}>
                Promote to Director
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Demote Confirmation Modal */}
      {showDemoteModal && (
        <div className="admin-modal-overlay" onClick={() => setShowDemoteModal(null)}>
          <div className="admin-modal" onClick={(e) => e.stopPropagation()}>
            <h3>Demote Director</h3>
            <p>Are you sure you want to demote <strong>{showDemoteModal.full_name || showDemoteModal.email}</strong> to regular member?</p>
            <p className="info">They will lose all admin privileges.</p>
            <div className="modal-buttons">
              <button className="cancel-btn" onClick={() => setShowDemoteModal(null)}>
                Cancel
              </button>
              <button className="confirm-demote-btn" onClick={() => handleDemote(showDemoteModal.user_id)}>
                Demote to Member
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminPage;
