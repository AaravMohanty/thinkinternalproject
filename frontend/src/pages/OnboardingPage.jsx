import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { profileAPI } from '../utils/api';
import '../styles/onboarding.css';

const OnboardingPage = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploadedResume, setUploadedResume] = useState(null);
  const navigate = useNavigate();
  const { updateUser, user } = useAuth();

  // Profile matching state
  const [potentialMatches, setPotentialMatches] = useState([]);
  const [selectedMatch, setSelectedMatch] = useState(null);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [isLinked, setIsLinked] = useState(false);

  const [profileData, setProfileData] = useState({
    major: '',
    graduationYear: '',
    companies: '',
    roles: '',
    linkedinUrl: '',
  });

  // Search for matches when component mounts (user just signed up)
  useEffect(() => {
    if (user?.profile?.full_name) {
      searchForMatches();
    }
  }, []);

  const searchForMatches = async () => {
    try {
      const result = await profileAPI.matchProfile(
        user?.profile?.full_name || '',
        user?.email || ''
      );
      if (result.success && result.matches) {
        setPotentialMatches(result.matches);
      }
    } catch (err) {
      console.error('Error searching for matches:', err);
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (file.type !== 'application/pdf') {
      setError('Please upload a PDF file');
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setError('File size must be less than 5MB');
      return;
    }

    setUploadedResume(file);
    setError('');
  };

  const handleNext = async () => {
    setError('');

    if (currentStep === 1) {
      // Upload resume if provided
      if (uploadedResume) {
        setLoading(true);
        try {
          const result = await profileAPI.uploadResume(uploadedResume);
          if (result.success && result.parsed_data) {
            const parsed = result.parsed_data;
            const companies = parsed.work_experience?.map(job => job.company).filter(Boolean) || [];
            const roles = parsed.work_experience?.map(job => job.title).filter(Boolean) || [];

            setProfileData({
              major: parsed.major || '',
              graduationYear: parsed.graduation_year || '',
              companies: companies.join(', '),
              roles: roles.join(', '),
              linkedinUrl: parsed.linkedin_url || '',
            });
          }
        } catch (err) {
          console.error('Resume upload error:', err);
          setError('Resume uploaded but parsing had issues. Please fill in the fields manually.');
        } finally {
          setLoading(false);
        }
      }
      // Move to profile matching step
      setCurrentStep(2);
    } else if (currentStep === 2) {
      // User chose "None of these" or no matches found - proceed to profile
      setCurrentStep(3);
    } else if (currentStep === 3) {
      await handleComplete();
    }
  };

  const handleSelectMatch = (match) => {
    setSelectedMatch(match);
    setShowConfirmModal(true);
  };

  const handleConfirmMatch = async () => {
    if (!selectedMatch) return;

    setLoading(true);
    setShowConfirmModal(false);

    try {
      const result = await profileAPI.linkProfile(selectedMatch.csv_index);

      if (result.success) {
        setIsLinked(true);
        // Pre-fill profile data from CSV
        if (result.csv_data) {
          setProfileData(prev => ({
            ...prev,
            major: result.csv_data.major || prev.major,
            graduationYear: result.csv_data.graduation_year?.toString() || prev.graduationYear,
            companies: result.csv_data.companies?.join(', ') || prev.companies,
            roles: result.csv_data.roles?.join(', ') || prev.roles,
          }));
        }
        // Update user context with the linked profile (including profile_image_url)
        if (result.profile) {
          const updatedUser = { ...user, profile: result.profile };
          updateUser(updatedUser);
        }
        setCurrentStep(3);
      } else {
        setError(result.error || 'Failed to link profile');
      }
    } catch (err) {
      console.error('Error linking profile:', err);
      setError('Failed to link profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelConfirm = () => {
    setShowConfirmModal(false);
    setSelectedMatch(null);
  };

  const handleComplete = async () => {
    if (!profileData.major || !profileData.graduationYear) {
      setError('Please fill in required fields (Major and Graduation Year)');
      return;
    }

    setLoading(true);
    try {
      const companiesArray = profileData.companies
        ? profileData.companies.split(',').map(c => c.trim()).filter(Boolean)
        : [];
      const rolesArray = profileData.roles
        ? profileData.roles.split(',').map(r => r.trim()).filter(Boolean)
        : [];

      const result = await profileAPI.update({
        major: profileData.major,
        graduation_year: parseInt(profileData.graduationYear),
        companies: companiesArray,
        roles: rolesArray,
        linkedin_url: profileData.linkedinUrl,
        onboarding_completed: true,
      });

      if (result.success) {
        // Use the full profile returned from the server (includes profile_image_url)
        const updatedUser = { ...user, profile: result.profile };
        updateUser(updatedUser);
        navigate('/');
      } else {
        setError(result.error || 'Failed to save profile');
      }
    } catch (err) {
      console.error('Profile update error:', err);
      setError('Failed to save profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Alumni card component
  const AlumniCard = ({ alumni, onSelect, isSelectable = true }) => {
    const fallbackLogo = '/assets/Copy of P Logo for dark background (1).png';

    // Handle image URL
    let imageUrl = fallbackLogo;
    let isFallback = true;

    if (alumni.profile_image_url) {
      const profileImage = alumni.profile_image_url;
      if (profileImage.startsWith('/assets/')) {
        imageUrl = profileImage.substring(1);
        isFallback = false;
      } else if (profileImage.startsWith('http')) {
        imageUrl = profileImage;
        isFallback = false;
      }
    }

    // Display roles and companies
    const uniqueCompanies = alumni.companies_list?.length > 0
      ? [...new Set(alumni.companies_list)].filter(c => c && c !== 'null')
      : [];
    const companyDisplay = uniqueCompanies.length > 0
      ? uniqueCompanies.slice(0, 3).join(' • ')
      : alumni.company || 'N/A';

    const uniqueRoles = alumni.roles_list?.length > 0
      ? [...new Set(alumni.roles_list)].filter(r => r && r !== 'null')
      : [];
    const roleDisplay = uniqueRoles.length > 0
      ? uniqueRoles.slice(0, 2).join(' → ')
      : alumni.role_title || 'N/A';

    const infoItems = [];
    if (alumni.major) infoItems.push(alumni.major);
    if (alumni.grad_year && alumni.grad_year !== 'nan') infoItems.push(`Class of ${alumni.grad_year}`);
    if (alumni.location) infoItems.push(alumni.location);
    const infoText = infoItems.join(' • ');

    return (
      <div
        className={`match-card ${isSelectable ? 'selectable' : ''}`}
        onClick={() => isSelectable && onSelect?.(alumni)}
      >
        <div className="match-card-image-section">
          {isFallback ? (
            <div className="match-card-image-fallback">
              <img src={fallbackLogo} alt="PurdueTHINK Logo" />
            </div>
          ) : (
            <img
              src={imageUrl}
              alt={alumni.name}
              className="match-card-image"
              onError={(e) => {
                e.target.style.display = 'none';
                e.target.parentElement.innerHTML = `<div class="match-card-image-fallback"><img src="${fallbackLogo}" alt="PurdueTHINK Logo" /></div>`;
              }}
            />
          )}
          <div className="match-card-gradient"></div>
        </div>
        <div className="match-card-body">
          <h3 className="match-card-name">{alumni.name}</h3>
          <p className="match-card-role">{roleDisplay}</p>
          <p className="match-card-company">{companyDisplay}</p>
          {infoText && <p className="match-card-info">{infoText}</p>}
          {isSelectable && (
            <div className="match-card-select-hint">Click to select</div>
          )}
        </div>
      </div>
    );
  };

  const progress = ((currentStep - 1) / 2) * 100;

  const getStepTitle = () => {
    if (currentStep === 2) return 'Is This You?';
    return 'Complete Your Profile';
  };

  const getStepSubtitle = () => {
    if (currentStep === 1) return 'Upload your resume to auto-fill your profile, or skip to enter manually.';
    if (currentStep === 2) return 'We found some profiles that might be you. Select yours to link your account.';
    return 'Fill in your details to complete your profile.';
  };

  return (
    <div className="onboarding-page">
      {/* Background Light Rays */}
      <div className="onboarding-bg">
        <div className="light-ray ray-1"></div>
        <div className="light-ray ray-2"></div>
      </div>

      {/* Main Card */}
      <div className={`onboarding-card ${currentStep === 2 && potentialMatches.length > 0 ? 'wide' : ''}`}>
        {/* Header */}
        <div className="onboarding-header">
          <span className="onboarding-label">
            {currentStep === 1 ? 'STEP 1 OF 3' : currentStep === 2 ? 'STEP 2 OF 3' : 'STEP 3 OF 3'}
          </span>
          <h1 className="onboarding-title">{getStepTitle()}</h1>
          <div className="onboarding-divider"></div>
          <p className="onboarding-subtitle">{getStepSubtitle()}</p>
        </div>

        {/* Progress */}
        <div className="onboarding-progress">
          <div className="onboarding-progress-line-segment onboarding-progress-line-1">
            <div 
              className={`onboarding-progress-fill ${currentStep >= 3 ? 'completed' : ''}`}
              style={{ width: currentStep >= 2 ? '100%' : '0%' }}
            ></div>
          </div>
          <div className="onboarding-progress-line-segment onboarding-progress-line-2">
            <div 
              className="onboarding-progress-fill" 
              style={{ width: currentStep >= 3 ? '100%' : '0%' }}
            ></div>
          </div>
          {[1, 2, 3].map((step) => (
            <div key={step} className="onboarding-step">
              <div className={`onboarding-step-circle ${
                step === currentStep ? 'active' : step < currentStep ? 'completed' : 'pending'
              }`}>
                {step < currentStep ? '✓' : step}
              </div>
              <div className="onboarding-step-label">
                {step === 1 ? 'Resume' : step === 2 ? 'Match' : 'Profile'}
              </div>
            </div>
          ))}
        </div>

        {/* Error Message */}
        {error && <div className="onboarding-error">{error}</div>}

        {/* Step 1: Resume Upload */}
        {currentStep === 1 && (
          <div>
            <label className="onboarding-upload-label">Upload Your Resume (Optional)</label>
            <div
              className={`onboarding-upload-zone ${uploadedResume ? 'has-file' : ''}`}
              onClick={() => document.getElementById('resumeFile').click()}
            >
              <div className="onboarding-upload-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" strokeLinecap="round" strokeLinejoin="round"/>
                  <polyline points="14 2 14 8 20 8" strokeLinecap="round" strokeLinejoin="round"/>
                  <line x1="12" y1="18" x2="12" y2="12" strokeLinecap="round" strokeLinejoin="round"/>
                  <line x1="9" y1="15" x2="15" y2="15" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <p className="onboarding-upload-text">
                <span>Click to upload</span> or drag and drop
              </p>
              <p className="onboarding-upload-hint">PDF only, max 5MB</p>
              <input
                type="file"
                id="resumeFile"
                accept=".pdf"
                hidden
                onChange={handleFileUpload}
              />
              {uploadedResume && (
                <div className="onboarding-upload-file">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  {uploadedResume.name}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Step 2: Profile Matching */}
        {currentStep === 2 && (
          <div>
            {potentialMatches.length > 0 ? (
              <>
                <div className={`onboarding-matches-grid ${potentialMatches.length === 1 ? 'single' : ''}`}>
                  {potentialMatches.map((match) => (
                    <AlumniCard
                      key={match.csv_index}
                      alumni={match}
                      onSelect={handleSelectMatch}
                    />
                  ))}
                </div>
                <button className="onboarding-none-btn" onClick={handleNext}>
                  None of these are me — Create new profile
                </button>
              </>
            ) : (
              <div className="onboarding-welcome">
                <div className="onboarding-welcome-icon">👋</div>
                <h3>Welcome, new member!</h3>
                <p>We didn't find an existing profile for you. Let's create one!</p>
              </div>
            )}
          </div>
        )}

        {/* Step 3: Profile Details */}
        {currentStep === 3 && (
          <div>
            {isLinked && (
              <div className="onboarding-success">
                Your account has been linked to your existing profile. Update any details below.
              </div>
            )}

            <div className="onboarding-form-group">
              <label className="onboarding-form-label">
                Major <span className="required">*</span>
              </label>
              <input
                type="text"
                className="onboarding-form-input"
                placeholder="Computer Science"
                value={profileData.major}
                onChange={(e) => setProfileData({ ...profileData, major: e.target.value })}
                required
              />
            </div>

            <div className="onboarding-form-group">
              <label className="onboarding-form-label">
                Graduation Year <span className="required">*</span>
              </label>
              <input
                type="number"
                className="onboarding-form-input"
                placeholder="2025"
                min="1950"
                max="2030"
                value={profileData.graduationYear}
                onChange={(e) => setProfileData({ ...profileData, graduationYear: e.target.value })}
                required
              />
            </div>

            <div className="onboarding-form-group">
              <label className="onboarding-form-label">Companies</label>
              <input
                type="text"
                className="onboarding-form-input"
                placeholder="Google, Microsoft, Amazon"
                value={profileData.companies}
                onChange={(e) => setProfileData({ ...profileData, companies: e.target.value })}
              />
              <p className="onboarding-form-hint">Separate multiple companies with commas</p>
            </div>

            <div className="onboarding-form-group">
              <label className="onboarding-form-label">Roles</label>
              <input
                type="text"
                className="onboarding-form-input"
                placeholder="Software Engineer, Intern, PM"
                value={profileData.roles}
                onChange={(e) => setProfileData({ ...profileData, roles: e.target.value })}
              />
              <p className="onboarding-form-hint">Separate multiple roles with commas</p>
            </div>

            <div className="onboarding-form-group">
              <label className="onboarding-form-label">LinkedIn URL</label>
              <input
                type="url"
                className="onboarding-form-input"
                placeholder="https://linkedin.com/in/yourprofile"
                value={profileData.linkedinUrl}
                onChange={(e) => setProfileData({ ...profileData, linkedinUrl: e.target.value })}
              />
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="onboarding-actions">
          {currentStep > 1 && (
            <button
              className="onboarding-btn onboarding-btn-secondary"
              onClick={() => setCurrentStep(currentStep - 1)}
            >
              Back
            </button>
          )}
          {(currentStep === 1 || currentStep === 3 || (currentStep === 2 && potentialMatches.length === 0)) && (
            <button
              className="onboarding-btn onboarding-btn-primary"
              onClick={handleNext}
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="onboarding-spinner"></span>
                  {currentStep === 1 ? 'Uploading...' : currentStep === 3 ? 'Completing...' : 'Loading...'}
                </>
              ) : (
                currentStep === 3 ? 'Complete Profile' : 'Continue'
              )}
            </button>
          )}
        </div>
      </div>

      {/* Confirmation Modal */}
      {showConfirmModal && selectedMatch && (
        <div className="onboarding-modal-overlay">
          <div className="onboarding-modal">
            <h2 className="onboarding-modal-title">Confirm Your Identity</h2>
            <p className="onboarding-modal-text">
              Are you sure you are <strong>{selectedMatch.name}</strong>?
            </p>

            <div className="onboarding-modal-preview">
              <div className="onboarding-modal-avatar">
                {selectedMatch.profile_image_url ? (
                  <img
                    src={selectedMatch.profile_image_url}
                    alt={selectedMatch.name}
                    onError={(e) => {
                      e.target.src = '/assets/Copy of P Logo for dark background (1).png';
                      e.target.className = 'fallback';
                    }}
                  />
                ) : (
                  <img
                    src="/assets/Copy of P Logo for dark background (1).png"
                    alt="Logo"
                    className="fallback"
                  />
                )}
              </div>
              <div className="onboarding-modal-info">
                <p className="onboarding-modal-name">{selectedMatch.name}</p>
                <p className="onboarding-modal-detail">{selectedMatch.role_title || 'N/A'}</p>
                <p className="onboarding-modal-detail">{selectedMatch.company || 'N/A'}</p>
              </div>
            </div>

            <p className="onboarding-modal-warning">
              This action will link your account to this existing profile.
            </p>

            <div className="onboarding-modal-actions">
              <button
                className="onboarding-btn onboarding-btn-secondary"
                onClick={handleCancelConfirm}
              >
                Cancel
              </button>
              <button
                className="onboarding-btn onboarding-btn-primary"
                onClick={handleConfirmMatch}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="onboarding-spinner"></span>
                    Linking...
                  </>
                ) : (
                  'Yes, this is me'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OnboardingPage;
