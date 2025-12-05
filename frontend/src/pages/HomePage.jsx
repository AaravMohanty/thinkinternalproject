import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { alumniAPI } from '../utils/api';
import ProfileDropdown from '../components/ProfileDropdown';
import SearchableDropdown from '../components/SearchableDropdown';
import Chatbot from '../components/Chatbot';
import '../styles/people.css';

const HomePage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  // State
  const [allAlumni, setAllAlumni] = useState([]);
  const [filteredAlumni, setFilteredAlumni] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showFilters, setShowFilters] = useState(false);

  // Recommendations state
  const [recommendations, setRecommendations] = useState([]);
  const [excludedIds, setExcludedIds] = useState([]);
  const [loadingRecs, setLoadingRecs] = useState(false);
  const [recsMessage, setRecsMessage] = useState('');

  // AI Email state
  const [generatingEmailFor, setGeneratingEmailFor] = useState(null);
  const [emailOverlay, setEmailOverlay] = useState(null);

  // Expanded card state
  const [expandedCard, setExpandedCard] = useState(null);

  // Filter options
  const [filterOptions, setFilterOptions] = useState({
    majors: [],
    years: [],
    companies: [],
    industries: []
  });

  // Filter state
  const [filters, setFilters] = useState({
    searchName: '',
    searchTitle: '',
    selectedMajors: [],
    selectedYears: [],
    selectedCompanies: [],
    selectedIndustries: [],
    sortBy: 'name',
    sortAscending: true
  });

  useEffect(() => {
    loadFilterOptions();
    loadAlumni();
    if (user) {
      loadRecommendations();
    }
  }, [user]);

  const loadRecommendations = async (newExcludeIds = []) => {
    try {
      setLoadingRecs(true);
      setRecsMessage('');
      const data = await alumniAPI.getRecommendations(newExcludeIds, 8);
      if (data.success) {
        if (data.recommendations && data.recommendations.length > 0) {
          setRecommendations(data.recommendations);
          const newIds = data.recommendations.map(r => r.csv_row_id);
          setExcludedIds(prev => [...new Set([...prev, ...newIds])]);
        } else {
          setRecommendations([]);
          setRecsMessage(data.message || 'No recommendations available');
        }
      }
    } catch (error) {
      console.error('Error loading recommendations:', error);
      setRecsMessage('Could not load recommendations');
    } finally {
      setLoadingRecs(false);
    }
  };

  const refreshRecommendations = () => {
    loadRecommendations(excludedIds);
  };

  const resetRecommendations = () => {
    setExcludedIds([]);
    loadRecommendations([]);
  };

  useEffect(() => {
    applyFilters();
  }, [filters, allAlumni]);

  const loadFilterOptions = async () => {
    try {
      const data = await alumniAPI.getFilters();
      if (data.success) {
        setFilterOptions(data.filters);
      }
    } catch (error) {
      console.error('Error loading filter options:', error);
    }
  };

  const loadAlumni = async () => {
    try {
      setLoading(true);
      const data = await alumniAPI.getAll();
      if (data.success) {
        setAllAlumni(data.data);
      }
    } catch (error) {
      console.error('Error loading alumni:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = allAlumni.filter(alumni => {
      if (filters.searchName && !alumni.name.toLowerCase().includes(filters.searchName.toLowerCase())) {
        return false;
      }
      if (filters.searchTitle) {
        const titleMatch = alumni.role_title?.toLowerCase().includes(filters.searchTitle.toLowerCase()) ||
                          alumni.headline?.toLowerCase().includes(filters.searchTitle.toLowerCase());
        if (!titleMatch) return false;
      }
      if (filters.selectedMajors.length > 0 && !filters.selectedMajors.includes(alumni.major)) {
        return false;
      }
      if (filters.selectedYears.length > 0 && !filters.selectedYears.includes(alumni.grad_year)) {
        return false;
      }
      if (filters.selectedCompanies.length > 0) {
        const hasCompany = alumni.companies_list?.some(c => filters.selectedCompanies.includes(c));
        if (!hasCompany) return false;
      }
      if (filters.selectedIndustries.length > 0 && !filters.selectedIndustries.includes(alumni.company_industry)) {
        return false;
      }
      return true;
    });

    filtered.sort((a, b) => {
      let aValue = a[filters.sortBy] || '';
      let bValue = b[filters.sortBy] || '';
      if (filters.sortBy === 'grad_year') {
        aValue = parseInt(aValue) || 0;
        bValue = parseInt(bValue) || 0;
      } else {
        aValue = aValue.toString().toLowerCase();
        bValue = bValue.toString().toLowerCase();
      }
      if (aValue < bValue) return filters.sortAscending ? -1 : 1;
      if (aValue > bValue) return filters.sortAscending ? 1 : -1;
      return 0;
    });

    setFilteredAlumni(filtered);
  };

  const resetFilters = () => {
    setFilters({
      searchName: '',
      searchTitle: '',
      selectedMajors: [],
      selectedYears: [],
      selectedCompanies: [],
      selectedIndustries: [],
      sortBy: 'name',
      sortAscending: true
    });
  };

  const handleComposeWithAI = async (alumni) => {
    const alumniId = alumni.id || alumni.name;
    if (emailOverlay && emailOverlay.alumniId === alumniId) {
      setEmailOverlay(null);
      return;
    }
    if (generatingEmailFor) return;
    setGeneratingEmailFor(alumniId);

    try {
      const response = await alumniAPI.generateEmail(alumni);
      if (response.success && response.email) {
        setEmailOverlay({
          alumniId,
          email: response.email,
          subject: response.subject || 'Connecting from Purdue THINK'
        });
      } else {
        console.error('Failed to generate email:', response.error);
        alert('Failed to generate email. Please try again.');
      }
    } catch (error) {
      console.error('Error generating email:', error);
      alert('Failed to generate email. Please try again.');
    } finally {
      setGeneratingEmailFor(null);
    }
  };

  const handleCopyEmail = async () => {
    if (!emailOverlay) return;
    try {
      const fullText = `Subject: ${emailOverlay.subject}\n\n${emailOverlay.email}`;
      await navigator.clipboard.writeText(fullText);
      alert('Email copied to clipboard!');
    } catch (error) {
      const textarea = document.createElement('textarea');
      textarea.value = `Subject: ${emailOverlay.subject}\n\n${emailOverlay.email}`;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      alert('Email copied to clipboard!');
    }
  };

  const getActiveFilterCount = () => {
    let count = 0;
    if (filters.searchName) count++;
    if (filters.searchTitle) count++;
    if (filters.selectedMajors.length > 0) count++;
    if (filters.selectedYears.length > 0) count++;
    if (filters.selectedCompanies.length > 0) count++;
    if (filters.selectedIndustries.length > 0) count++;
    return count;
  };

  const createAlumniCard = (alumni) => {
    const profileImage = alumni.profile_image_url || '';
    const fallbackLogo = '/assets/Copy of P Logo for dark background (1).png';
    const isLocalAsset = profileImage && String(profileImage).startsWith('/assets/');
    const isValidUrl = profileImage && String(profileImage).startsWith('http') && profileImage !== 'nan' && profileImage !== 'null';

    let imageUrl = fallbackLogo;
    let isFallback = true;
    if (isLocalAsset) {
      imageUrl = profileImage.substring(1);
      isFallback = false;
    } else if (isValidUrl) {
      imageUrl = profileImage;
      isFallback = false;
    }

    const uniqueCompanies = alumni.companies_list && alumni.companies_list.length > 0
      ? [...new Set(alumni.companies_list)].filter(c => c && c !== 'null' && c !== 'undefined')
      : [];
    const companyDisplay = uniqueCompanies.length > 0
      ? uniqueCompanies.slice(0, 3).join(' • ')
      : alumni.company || 'N/A';

    const uniqueRoles = alumni.roles_list && alumni.roles_list.length > 0
      ? [...new Set(alumni.roles_list)].filter(r => r && r !== 'null' && r !== 'undefined')
      : [];
    const roleDisplay = uniqueRoles.length > 0
      ? uniqueRoles.slice(0, 2).join(', ')
      : alumni.role_title || alumni.headline || 'N/A';

    const infoItems = [];
    if (alumni.major) infoItems.push(alumni.major);
    if (alumni.grad_year) infoItems.push(`Class of ${String(alumni.grad_year).replace('.0', '')}`);
    if (alumni.location) infoItems.push(alumni.location);
    const infoText = infoItems.join(' • ');

    const safeString = (val) => {
      if (val === null || val === undefined) return '';
      const str = String(val);
      if (str === 'nan' || str === 'null' || str === 'None' || str === 'none' || str.trim() === '') return '';
      return str;
    };

    const linkedinUrl = safeString(alumni.linkedin) || safeString(alumni.Linkedin) || safeString(alumni.linkedinProfileUrl);
    const emailAddress = safeString(alumni.professional_email) || safeString(alumni.professionalEmail) || safeString(alumni.email) || safeString(alumni['Personal Gmail']);
    const hasEmailOverlay = emailOverlay && emailOverlay.alumniId === (alumni.id || alumni.name);
    const cardId = alumni.id || alumni.name;
    const isExpanded = expandedCard === cardId;

    const handleCardClick = () => {
      if (!hasEmailOverlay && !isExpanded) {
        setExpandedCard(cardId);
      }
    };

    return (
      <div
        key={cardId}
        className={`alumni-card ${hasEmailOverlay ? 'has-overlay' : ''} ${isExpanded ? 'expanded' : ''}`}
        onClick={handleCardClick}
        style={{ cursor: (!hasEmailOverlay && !isExpanded) ? 'pointer' : 'default' }}
      >
        <div className="card-image-section">
          {isFallback ? (
            <div className="card-image-fallback">
              <img src={fallbackLogo} alt="PurdueTHINK Logo" />
            </div>
          ) : (
            <img
              src={imageUrl}
              alt={alumni.name}
              className="card-image"
              onError={(e) => {
                e.target.style.display = 'none';
                const fallback = document.createElement('div');
                fallback.className = 'card-image-fallback';
                fallback.innerHTML = `<img src="${fallbackLogo}" alt="PurdueTHINK Logo" />`;
                e.target.parentElement.insertBefore(fallback, e.target);
              }}
            />
          )}

          {(linkedinUrl || emailAddress || user) && (
            <div className="card-contact-icons">
              {linkedinUrl && (
                <a href={linkedinUrl} target="_blank" rel="noopener noreferrer" className="contact-icon linkedin-icon" title="LinkedIn Profile" onClick={(e) => e.stopPropagation()}>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                  </svg>
                </a>
              )}
              {emailAddress && (
                <a href={`mailto:${emailAddress}`} className="contact-icon email-icon" title="Email" onClick={(e) => e.stopPropagation()}>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                    <polyline points="22,6 12,13 2,6"></polyline>
                  </svg>
                </a>
              )}
              {user && (
                <button
                  className={`contact-icon ai-compose-icon ${generatingEmailFor === cardId ? 'loading' : ''}`}
                  title="Generate AI Email"
                  onClick={(e) => { e.stopPropagation(); handleComposeWithAI(alumni); }}
                  disabled={generatingEmailFor === cardId}
                >
                  {generatingEmailFor === cardId ? (
                    <svg width="20" height="20" viewBox="0 0 24 24" className="spinning">
                      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" fill="none" strokeDasharray="31.4" strokeDashoffset="10" />
                    </svg>
                  ) : (
                    <img src="/assets/Copy of P Logo for dark background (1).png" alt="AI" className="ai-icon-img" />
                  )}
                </button>
              )}
            </div>
          )}
        </div>
        <div className="card-body">
          <h3 className="card-name">{alumni.name}</h3>
          <p className="card-role">{roleDisplay}</p>
          <p className="card-company">{companyDisplay}</p>
          {infoText && <p className="card-info">{infoText}</p>}
        </div>

        {/* Info Overlay - shown when card is clicked */}
        {isExpanded && !hasEmailOverlay && (
          <div className="info-overlay" onClick={(e) => e.stopPropagation()}>
            <div className="info-overlay-header">
              <h3>{alumni.name}</h3>
              <button className="overlay-close-btn" onClick={(e) => { e.stopPropagation(); setExpandedCard(null); }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>
            <div className="info-overlay-content">
              {roleDisplay && roleDisplay !== 'N/A' && (
                <div className="info-row">
                  <span className="info-label">Role</span>
                  <span className="info-value">{roleDisplay}</span>
                </div>
              )}
              {companyDisplay && companyDisplay !== 'N/A' && (
                <div className="info-row">
                  <span className="info-label">Company</span>
                  <span className="info-value">{companyDisplay}</span>
                </div>
              )}
              {alumni.major && (
                <div className="info-row">
                  <span className="info-label">Major</span>
                  <span className="info-value">{alumni.major}</span>
                </div>
              )}
              {alumni.grad_year && (
                <div className="info-row">
                  <span className="info-label">Graduation</span>
                  <span className="info-value">Class of {String(alumni.grad_year).replace('.0', '')}</span>
                </div>
              )}
              {alumni.location && (
                <div className="info-row">
                  <span className="info-label">Location</span>
                  <span className="info-value">{alumni.location}</span>
                </div>
              )}
              {alumni.company_industry && (
                <div className="info-row">
                  <span className="info-label">Industry</span>
                  <span className="info-value">{alumni.company_industry}</span>
                </div>
              )}
              {alumni.headline && (
                <div className="info-row full-width">
                  <span className="info-label">About</span>
                  <span className="info-value">{alumni.headline}</span>
                </div>
              )}
            </div>
            <div className="info-overlay-actions">
              {linkedinUrl && (
                <a href={linkedinUrl} target="_blank" rel="noopener noreferrer" className="info-action-btn" onClick={(e) => e.stopPropagation()}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                  </svg>
                  LinkedIn
                </a>
              )}
              {emailAddress && (
                <a href={`mailto:${emailAddress}`} className="info-action-btn" onClick={(e) => e.stopPropagation()}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                    <polyline points="22,6 12,13 2,6"></polyline>
                  </svg>
                  Email
                </a>
              )}
            </div>
          </div>
        )}

        {/* Email Overlay - shown when AI email is generated */}
        {hasEmailOverlay && (
          <div className="email-overlay" onClick={(e) => e.stopPropagation()}>
            <div className="email-overlay-header">
              <span>Generated Email</span>
              <button className="overlay-close-btn" onClick={(e) => { e.stopPropagation(); setEmailOverlay(null); }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>
            <div className="email-overlay-content">
              <div className="email-subject"><strong>Subject:</strong> {emailOverlay.subject}</div>
              <div className="email-body">{emailOverlay.email}</div>
            </div>
            <button className="email-overlay-copy" onClick={(e) => { e.stopPropagation(); handleCopyEmail(); }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
              </svg>
              Copy to Clipboard
            </button>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="alumni-page">
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
          <Link to="/" className="nav-link active">Alumni</Link>
          {user?.profile?.is_director && (
            <Link to="/admin" className="nav-link">Admin</Link>
          )}
          <ProfileDropdown />
        </div>
      </nav>

      {/* Page Header */}
      <header className="page-header">
        <div className="header-content">
          <div className="header-text">
            <span className="header-label">EXPLORE</span>
            <h1 className="header-title">Alumni Network</h1>
            <div className="header-divider"></div>
            <p className="header-subtitle">Connect with {allAlumni.length} Purdue THINK members and alumni</p>
          </div>
          <div className="header-actions">
            <button className="filter-toggle-btn" onClick={() => setShowFilters(true)}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="4" y1="21" x2="4" y2="14"></line>
                <line x1="4" y1="10" x2="4" y2="3"></line>
                <line x1="12" y1="21" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12" y2="3"></line>
                <line x1="20" y1="21" x2="20" y2="16"></line>
                <line x1="20" y1="12" x2="20" y2="3"></line>
                <line x1="1" y1="14" x2="7" y2="14"></line>
                <line x1="9" y1="8" x2="15" y2="8"></line>
                <line x1="17" y1="16" x2="23" y2="16"></line>
              </svg>
              Filters
              {getActiveFilterCount() > 0 && (
                <span className="filter-count">{getActiveFilterCount()}</span>
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Filter Panel Overlay */}
      <div className={`filter-overlay ${showFilters ? 'active' : ''}`} onClick={() => setShowFilters(false)}></div>

      {/* Filter Panel */}
      <aside className={`filter-panel ${showFilters ? 'active' : ''}`}>
        <div className="filter-panel-header">
          <h2>Filters</h2>
          <button className="filter-close-btn" onClick={() => setShowFilters(false)}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        <div className="filter-panel-content">
          <div className="filter-group">
            <label>Search by Name</label>
            <input
              type="text"
              className="filter-input"
              placeholder="e.g., John, Smith"
              value={filters.searchName}
              onChange={(e) => setFilters(prev => ({ ...prev, searchName: e.target.value }))}
            />
          </div>

          <div className="filter-group">
            <label>Job Title</label>
            <input
              type="text"
              className="filter-input"
              placeholder="e.g., software, analyst"
              value={filters.searchTitle}
              onChange={(e) => setFilters(prev => ({ ...prev, searchTitle: e.target.value }))}
            />
          </div>

          <div className="filter-group">
            <SearchableDropdown
              label="Major"
              options={filterOptions.majors}
              selectedValues={filters.selectedMajors}
              onChange={(values) => setFilters(prev => ({ ...prev, selectedMajors: values }))}
              placeholder="Select majors..."
              searchPlaceholder="Search majors..."
            />
          </div>

          <div className="filter-group">
            <SearchableDropdown
              label="Graduation Year"
              options={filterOptions.years}
              selectedValues={filters.selectedYears}
              onChange={(values) => setFilters(prev => ({ ...prev, selectedYears: values }))}
              placeholder="Select years..."
              searchPlaceholder="Search years..."
            />
          </div>

          <div className="filter-group">
            <SearchableDropdown
              label="Company"
              options={filterOptions.companies}
              selectedValues={filters.selectedCompanies}
              onChange={(values) => setFilters(prev => ({ ...prev, selectedCompanies: values }))}
              placeholder="Select companies..."
              searchPlaceholder="Search companies..."
            />
          </div>

          <div className="filter-group">
            <SearchableDropdown
              label="Industry"
              options={filterOptions.industries}
              selectedValues={filters.selectedIndustries}
              onChange={(values) => setFilters(prev => ({ ...prev, selectedIndustries: values }))}
              placeholder="Select industries..."
              searchPlaceholder="Search industries..."
            />
          </div>

          <div className="filter-group">
            <label>Sort By</label>
            <select
              className="filter-select"
              value={filters.sortBy}
              onChange={(e) => setFilters(prev => ({ ...prev, sortBy: e.target.value }))}
            >
              <option value="name">Name</option>
              <option value="company">Company</option>
              <option value="grad_year">Graduation Year</option>
              <option value="major">Major</option>
            </select>
          </div>

          <div className="filter-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={filters.sortAscending}
                onChange={(e) => setFilters(prev => ({ ...prev, sortAscending: e.target.checked }))}
              />
              <span>Ascending Order</span>
            </label>
          </div>
        </div>

        <div className="filter-panel-footer">
          <button className="filter-reset-btn" onClick={resetFilters}>Reset All</button>
          <button className="filter-apply-btn" onClick={() => setShowFilters(false)}>Apply Filters</button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="alumni-main">
        {/* AI Recommendations */}
        {user && (
          <section className="recommendations-section">
            <div className="recommendations-header">
              <div className="recommendations-title">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
                <h2>Recommended for You</h2>
              </div>
              <div className="recommendations-actions">
                <button className="btn-secondary" onClick={refreshRecommendations} disabled={loadingRecs}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M23 4v6h-6M1 20v-6h6"/>
                    <path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/>
                  </svg>
                  New
                </button>
                <button className="btn-tertiary" onClick={resetRecommendations} disabled={loadingRecs}>Reset</button>
              </div>
            </div>

            {loadingRecs ? (
              <div className="recommendations-loading">
                <div className="spinner-small"></div>
                <span>Finding matches...</span>
              </div>
            ) : recommendations.length > 0 ? (
              <div className="recommendations-scroll">
                {recommendations.map(alumni => createAlumniCard(alumni))}
              </div>
            ) : recsMessage ? (
              <div className="recommendations-empty"><p>{recsMessage}</p></div>
            ) : null}
          </section>
        )}

        {/* Results Count */}
        <div className="results-info">
          <span className="results-count">Showing {filteredAlumni.length} of {allAlumni.length} alumni</span>
        </div>

        {/* Alumni Grid */}
        {loading ? (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading alumni data...</p>
          </div>
        ) : filteredAlumni.length === 0 ? (
          <div className="empty-state">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
            </svg>
            <h3>No results found</h3>
            <p>Try adjusting your filters or search terms</p>
          </div>
        ) : (
          <div className="alumni-grid">
            {filteredAlumni.map(alumni => createAlumniCard(alumni))}
          </div>
        )}
      </main>

      {/* AI Chatbot */}
      {user && <Chatbot />}
    </div>
  );
};

export default HomePage;
