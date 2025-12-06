import { useState, useEffect, useCallback } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { profileAPI } from '../utils/api';
import ProfileDropdown from '../components/ProfileDropdown';
import Cropper from 'react-easy-crop';
import '../styles/people.css';

const ProfilePage = () => {
  const { user, updateUser, logout } = useAuth();
  const navigate = useNavigate();

  const [originalProfile, setOriginalProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [uploadedProfilePic, setUploadedProfilePic] = useState(null);

  // Image cropping state
  const [showCropModal, setShowCropModal] = useState(false);
  const [imageToCrop, setImageToCrop] = useState(null);
  const [crop, setCrop] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [croppedAreaPixels, setCroppedAreaPixels] = useState(null);

  // Delete account state
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState('');

  const [formData, setFormData] = useState({
    fullName: '',
    personalEmail: '',
    phone: '',
    major: '',
    graduationYear: '',
    location: '',
    linkedinUrl: '',
    bio: '',
    careerInterests: '',
    emailTemplate: ''
  });

  // Separate arrays for roles and companies
  const [roles, setRoles] = useState(['']);
  const [companies, setCompanies] = useState(['']);

  const [profilePicUrl, setProfilePicUrl] = useState('');

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      const data = await profileAPI.get();
      if (data.success) {
        setOriginalProfile(data.profile);
        populateForm(data.profile);
      } else {
        setMessage({ type: 'error', text: 'Failed to load profile' });
      }
    } catch (error) {
      console.error('Error loading profile:', error);
      setMessage({ type: 'error', text: 'Failed to load profile' });
    } finally {
      setLoading(false);
    }
  };

  const populateForm = (profile) => {
    setFormData({
      fullName: profile.full_name || '',
      personalEmail: profile.personal_email || '',
      phone: profile.phone || '',
      major: profile.major || '',
      graduationYear: profile.graduation_year || '',
      location: profile.location || '',
      linkedinUrl: profile.linkedin_url || '',
      bio: profile.bio || '',
      careerInterests: Array.isArray(profile.career_interests)
        ? profile.career_interests.join(', ')
        : profile.career_interests || '',
      emailTemplate: profile.email_template || ''
    });

    // Populate roles and companies as separate arrays
    const loadedRoles = profile.roles || [];
    const loadedCompanies = profile.companies || [];

    // Fall back to old single company/title fields if arrays are empty
    if (loadedRoles.length > 0) {
      setRoles(loadedRoles);
    } else if (profile.current_title) {
      setRoles([profile.current_title]);
    } else {
      setRoles(['']);
    }

    if (loadedCompanies.length > 0) {
      setCompanies(loadedCompanies);
    } else if (profile.current_company) {
      setCompanies([profile.current_company]);
    } else {
      setCompanies(['']);
    }

    setProfilePicUrl(profile.profile_image_url || '');
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  // Role handlers
  const handleRoleChange = (index, value) => {
    const newRoles = [...roles];
    newRoles[index] = value;
    setRoles(newRoles);
  };

  const addRole = () => {
    setRoles([...roles, '']);
  };

  const removeRole = (index) => {
    if (roles.length > 1) {
      setRoles(roles.filter((_, i) => i !== index));
    }
  };

  // Company handlers
  const handleCompanyChange = (index, value) => {
    const newCompanies = [...companies];
    newCompanies[index] = value;
    setCompanies(newCompanies);
  };

  const addCompany = () => {
    setCompanies([...companies, '']);
  };

  const removeCompany = (index) => {
    if (companies.length > 1) {
      setCompanies(companies.filter((_, i) => i !== index));
    }
  };

  // Helper function to create cropped image
  const createCroppedImage = async (imageSrc, croppedAreaPixels) => {
    const image = await new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = reject;
      img.src = imageSrc;
    });

    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    canvas.width = croppedAreaPixels.width;
    canvas.height = croppedAreaPixels.height;

    ctx.drawImage(
      image,
      croppedAreaPixels.x,
      croppedAreaPixels.y,
      croppedAreaPixels.width,
      croppedAreaPixels.height,
      0,
      0,
      croppedAreaPixels.width,
      croppedAreaPixels.height
    );

    return new Promise((resolve) => {
      canvas.toBlob((blob) => {
        resolve(blob);
      }, 'image/jpeg', 0.95);
    });
  };

  const onCropComplete = useCallback((croppedArea, croppedAreaPixels) => {
    setCroppedAreaPixels(croppedAreaPixels);
  }, []);

  const handleCropSave = async () => {
    try {
      const croppedBlob = await createCroppedImage(imageToCrop, croppedAreaPixels);
      const croppedFile = new File([croppedBlob], 'profile.jpg', { type: 'image/jpeg' });

      // Set the cropped image as the profile pic
      const reader = new FileReader();
      reader.onload = (e) => {
        setProfilePicUrl(e.target.result);
      };
      reader.readAsDataURL(croppedFile);
      setUploadedProfilePic(croppedFile);

      // Close the crop modal
      setShowCropModal(false);
      setImageToCrop(null);
      setCrop({ x: 0, y: 0 });
      setZoom(1);
      setCroppedAreaPixels(null);
    } catch (error) {
      console.error('Error cropping image:', error);
      setMessage({ type: 'error', text: 'Failed to crop image' });
    }
  };

  const handleCropCancel = () => {
    setShowCropModal(false);
    setImageToCrop(null);
    setCrop({ x: 0, y: 0 });
    setZoom(1);
    setCroppedAreaPixels(null);
  };

  const handleProfilePicUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      setMessage({ type: 'error', text: 'Please select a valid image file' });
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setMessage({ type: 'error', text: 'Image size must be less than 5MB' });
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      setImageToCrop(e.target.result);
      setShowCropModal(true);
    };
    reader.readAsDataURL(file);
  };

  const handleSave = async () => {
    if (!formData.fullName || !formData.major || !formData.graduationYear) {
      setMessage({ type: 'error', text: 'Please fill in all required fields (Name, Major, Graduation Year)' });
      return;
    }

    setSaving(true);
    try {
      // Upload profile picture first if one was selected
      let imageUploadSuccess = true;
      if (uploadedProfilePic) {
        try {
          const imageResult = await profileAPI.uploadProfileImage(uploadedProfilePic);
          if (imageResult.success) {
            // Update the profile pic URL in the UI
            setProfilePicUrl(imageResult.image_url);
          } else {
            imageUploadSuccess = false;
            setMessage({ type: 'error', text: imageResult.error || 'Failed to upload profile picture' });
          }
        } catch (imageError) {
          console.error('Error uploading profile image:', imageError);
          imageUploadSuccess = false;
          setMessage({ type: 'error', text: 'Failed to upload profile picture' });
        }
      }

      // Only continue with profile update if image upload succeeded (or no image was uploaded)
      if (!imageUploadSuccess) {
        setSaving(false);
        return;
      }

      const careerInterests = formData.careerInterests
        ? formData.careerInterests.split(',').map(i => i.trim()).filter(i => i)
        : [];

      // Filter out empty entries from roles and companies
      const validRoles = roles.filter(r => r && r.trim());
      const validCompanies = companies.filter(c => c && c.trim());

      const profileData = {
        full_name: formData.fullName,
        personal_email: formData.personalEmail,
        phone: formData.phone,
        major: formData.major,
        graduation_year: parseInt(formData.graduationYear),
        // Store as separate arrays
        roles: validRoles,
        companies: validCompanies,
        // Also keep current_company/current_title for backward compatibility
        current_company: validCompanies[0] || '',
        current_title: validRoles[0] || '',
        location: formData.location,
        linkedin_url: formData.linkedinUrl,
        bio: formData.bio,
        career_interests: careerInterests,
        email_template: formData.emailTemplate || null
      };

      const result = await profileAPI.update(profileData);

      if (result.success) {
        setOriginalProfile(result.profile);
        setMessage({ type: 'success', text: 'Profile updated successfully!' });

        // Update user in context
        const updatedUser = { ...user, profile: result.profile };
        updateUser(updatedUser);

        setUploadedProfilePic(null);

        // Auto-hide message after 5s
        setTimeout(() => setMessage({ type: '', text: '' }), 5000);
      } else {
        setMessage({ type: 'error', text: result.error || 'Failed to save profile' });
      }
    } catch (error) {
      console.error('Error saving profile:', error);
      setMessage({ type: 'error', text: 'Failed to save profile' });
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    if (originalProfile) {
      populateForm(originalProfile);
      setUploadedProfilePic(null);
      setMessage({ type: '', text: '' });
    }
  };

  const handleDeleteAccount = async () => {
    if (deleteConfirmText !== 'DELETE') {
      setMessage({ type: 'error', text: 'Please type DELETE to confirm' });
      return;
    }

    setDeleting(true);
    try {
      const result = await profileAPI.deleteAccount();
      if (result.success) {
        // Clear all local auth state
        logout();
        // Navigate to landing page after deletion
        setTimeout(() => {
          navigate('/landing', { replace: true });
        }, 100);
      } else {
        setMessage({ type: 'error', text: result.error || 'Failed to delete account' });
        setDeleting(false);
        setShowDeleteModal(false);
        setDeleteConfirmText('');
      }
    } catch (error) {
      console.error('Error deleting account:', error);
      setMessage({ type: 'error', text: 'Failed to delete account' });
      setDeleting(false);
      setShowDeleteModal(false);
      setDeleteConfirmText('');
    }
  };

  const getInitials = (name) => {
    if (!name) return 'U';
    const parts = name.trim().split(' ');
    if (parts.length === 1) return parts[0].charAt(0).toUpperCase();
    return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
  };

  const getIndustries = () => {
    if (!formData.careerInterests) return [];
    return formData.careerInterests.split(',').map(i => i.trim()).filter(i => i).slice(0, 3);
  };

  // Helper functions for card preview (matching main page card display)
  const getRoleDisplay = () => {
    const validRoles = roles.filter(r => r && r.trim());
    if (validRoles.length === 0) return 'Add your roles';
    // Show role progression with arrow for multiple roles
    return validRoles.slice(0, 2).join(' → ');
  };

  const getCompanyDisplay = () => {
    const validCompanies = companies.filter(c => c && c.trim());
    if (validCompanies.length === 0) return 'Add your companies';
    // Show companies separated by bullet
    return validCompanies.slice(0, 3).join(' • ');
  };

  const getInfoText = () => {
    const items = [];
    if (formData.major) items.push(formData.major);
    if (formData.graduationYear) items.push(`Class of ${formData.graduationYear}`);
    if (formData.location) items.push(formData.location);
    return items.length > 0 ? items.join(' • ') : 'Add your info';
  };

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div>Loading profile...</div>
      </div>
    );
  }

  return (
    <div className="profile-page">
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
          {user?.profile?.is_director && (
            <a href="/admin" className="nav-link" onClick={(e) => { e.preventDefault(); navigate('/admin'); }}>Admin</a>
          )}
          <ProfileDropdown />
        </div>
      </nav>

      {/* Page Header */}
      <header className="page-header">
        <div className="header-content">
          <div className="header-text">
            <span className="header-label">MANAGE</span>
            <h1 className="header-title">Your Profile</h1>
            <div className="header-divider"></div>
            <p className="header-subtitle">Update your information and see how your card appears to other members</p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="profile-main">
        <div className="profile-content">
          {/* Profile Editor */}
          <div className="profile-editor">
            {/* Messages */}
            {message.text && (
              <div className={`message-box message-${message.type} show`}>
                {message.text}
              </div>
            )}

            {/* Profile Picture */}
            <div className="profile-pic-section">
              <div className="profile-pic-preview">
                {profilePicUrl ? (
                  <img src={profilePicUrl} alt="Profile" />
                ) : (
                  <span>{getInitials(formData.fullName)}</span>
                )}
              </div>
              <div className="profile-pic-upload">
                <label className="form-label">Profile Picture</label>
                <input type="file" id="profilePicInput" accept="image/*" style={{ display: 'none' }} onChange={handleProfilePicUpload} />
                <button type="button" className="upload-btn" onClick={() => document.getElementById('profilePicInput').click()}>
                  Upload Photo
                </button>
              </div>
            </div>

            {/* Basic Information */}
            <div className="form-section">
              <h3 className="section-title">Basic Information</h3>
              <div className="form-grid">
                <div className="form-group full-width">
                  <label htmlFor="fullName" className="form-label">Full Name *</label>
                  <input type="text" name="fullName" className="form-input" placeholder="John Doe" value={formData.fullName} onChange={handleInputChange} required />
                </div>
                <div className="form-group">
                  <label htmlFor="personalEmail" className="form-label">Personal Email</label>
                  <input type="email" name="personalEmail" className="form-input" placeholder="john@example.com" value={formData.personalEmail} onChange={handleInputChange} />
                </div>
                <div className="form-group">
                  <label htmlFor="phone" className="form-label">Phone</label>
                  <input type="tel" name="phone" className="form-input" placeholder="(555) 123-4567" value={formData.phone} onChange={handleInputChange} />
                </div>
              </div>
            </div>

            {/* Academic Information */}
            <div className="form-section">
              <h3 className="section-title">Academic</h3>
              <div className="form-grid">
                <div className="form-group">
                  <label htmlFor="major" className="form-label">Major *</label>
                  <input type="text" name="major" className="form-input" placeholder="Computer Science" value={formData.major} onChange={handleInputChange} required />
                </div>
                <div className="form-group">
                  <label htmlFor="graduationYear" className="form-label">Graduation Year *</label>
                  <input type="number" name="graduationYear" className="form-input" placeholder="2025" min="1950" max="2030" value={formData.graduationYear} onChange={handleInputChange} required />
                </div>
              </div>
            </div>

            {/* Career - Roles */}
            <div className="form-section">
              <div className="section-header-row">
                <h3 className="section-title">Roles / Job Titles</h3>
                <button type="button" className="add-item-btn" onClick={addRole}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <line x1="12" y1="5" x2="12" y2="19"></line>
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                  </svg>
                  Add Role
                </button>
              </div>
              <p className="section-description">Add your job titles, starting with the most recent</p>

              <div className="items-list">
                {roles.map((role, index) => (
                  <div key={index} className="item-row">
                    <div className="item-number">{index === 0 ? 'Current' : index + 1}</div>
                    <input
                      type="text"
                      className="form-input item-input"
                      placeholder="e.g., Software Engineer, Product Manager"
                      value={role}
                      onChange={(e) => handleRoleChange(index, e.target.value)}
                    />
                    {roles.length > 1 && (
                      <button
                        type="button"
                        className="remove-item-btn"
                        onClick={() => removeRole(index)}
                        title="Remove role"
                      >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <line x1="18" y1="6" x2="6" y2="18"></line>
                          <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Career - Companies */}
            <div className="form-section">
              <div className="section-header-row">
                <h3 className="section-title">Companies</h3>
                <button type="button" className="add-item-btn" onClick={addCompany}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <line x1="12" y1="5" x2="12" y2="19"></line>
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                  </svg>
                  Add Company
                </button>
              </div>
              <p className="section-description">Add companies you've worked at</p>

              <div className="items-list">
                {companies.map((company, index) => (
                  <div key={index} className="item-row">
                    <div className="item-number">{index === 0 ? 'Current' : index + 1}</div>
                    <input
                      type="text"
                      className="form-input item-input"
                      placeholder="e.g., Google, Amazon, Stripe"
                      value={company}
                      onChange={(e) => handleCompanyChange(index, e.target.value)}
                    />
                    {companies.length > 1 && (
                      <button
                        type="button"
                        className="remove-item-btn"
                        onClick={() => removeCompany(index)}
                        title="Remove company"
                      >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <line x1="18" y1="6" x2="6" y2="18"></line>
                          <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Additional Info */}
            <div className="form-section">
              <h3 className="section-title">Additional Info</h3>
              <div className="form-grid">
                <div className="form-group">
                  <label htmlFor="location" className="form-label">Location</label>
                  <input type="text" name="location" className="form-input" placeholder="San Francisco, CA" value={formData.location} onChange={handleInputChange} />
                </div>
                <div className="form-group">
                  <label htmlFor="linkedinUrl" className="form-label">LinkedIn URL</label>
                  <input type="url" name="linkedinUrl" className="form-input" placeholder="https://linkedin.com/in/johndoe" value={formData.linkedinUrl} onChange={handleInputChange} />
                </div>
                <div className="form-group full-width">
                  <label htmlFor="bio" className="form-label">Bio</label>
                  <textarea name="bio" className="form-textarea" placeholder="Tell us about yourself, your interests, and what you're looking for..." value={formData.bio} onChange={handleInputChange}></textarea>
                </div>
              </div>
            </div>

            {/* Career Interests */}
            <div className="form-section">
              <h3 className="section-title">Career Interests</h3>
              <div className="form-group">
                <label htmlFor="careerInterests" className="form-label">Industries (comma-separated)</label>
                <input type="text" name="careerInterests" className="form-input" placeholder="Technology, Finance, Healthcare" value={formData.careerInterests} onChange={handleInputChange} />
              </div>
            </div>

            {/* Email Template */}
            <div className="form-section">
              <h3 className="section-title">AI Email Template</h3>
              <p className="section-description">
                Customize the AI-generated networking emails. Leave blank to use the default template.
                Use placeholders like {'{alumni_name}'}, {'{your_name}'}, {'{company}'}, {'{role}'} in your template.
              </p>
              <div className="form-group">
                <label htmlFor="emailTemplate" className="form-label">Custom Email Template (optional)</label>
                <textarea
                  name="emailTemplate"
                  className="form-textarea email-template-textarea"
                  placeholder="Hi {alumni_name},&#10;&#10;I'm {your_name}, a fellow Purdue THINK member reaching out because...&#10;&#10;[The AI will fill in the rest based on your profiles]"
                  value={formData.emailTemplate}
                  onChange={handleInputChange}
                ></textarea>
              </div>
            </div>

            {/* Actions */}
            <div className="profile-actions">
              <button type="button" className="btn-cancel" onClick={handleCancel}>Cancel</button>
              <button type="button" className="btn-save" onClick={handleSave} disabled={saving}>
                {saving ? (
                  <>
                    <span className="loading-spinner"></span>Saving...
                  </>
                ) : (
                  'Save Changes'
                )}
              </button>
            </div>

            {/* Danger Zone */}
            <div className="danger-zone">
              <h3 className="danger-title">Danger Zone</h3>
              <p className="danger-description">
                Once you delete your account, there is no going back. Please be certain.
              </p>
              <button
                type="button"
                className="btn-delete-account"
                onClick={() => setShowDeleteModal(true)}
              >
                Delete Account
              </button>
            </div>
          </div>

          {/* Live Preview */}
          <div className="profile-preview">
            <div className="preview-card">
              <h3 className="preview-title">Card Preview</h3>
              <p className="preview-subtitle">This is how your profile appears to other members</p>

              <div className="alumni-card-preview">
                <div className="preview-image-section">
                  {profilePicUrl ? (
                    <img src={profilePicUrl} alt="Preview" className="preview-image" />
                  ) : (
                    <div className="preview-image-fallback">
                      <img src="/assets/Copy of P Logo for dark background (1).png" alt="PurdueTHINK Logo" />
                    </div>
                  )}
                  {/* Gradient overlay */}
                  <div className="preview-image-gradient"></div>
                </div>
                <div className="preview-body">
                  <h3 className="preview-name">{formData.fullName || 'Your Name'}</h3>
                  <p className="preview-role">{getRoleDisplay()}</p>
                  <p className="preview-company">{getCompanyDisplay()}</p>
                  <p className="preview-info">{getInfoText()}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Image Crop Modal */}
      {showCropModal && (
        <div className="modal-overlay">
          <div className="crop-modal">
            <h2 className="modal-title">Adjust Your Photo</h2>
            <p className="modal-description">Drag to reposition and use the slider to zoom</p>

            <div className="crop-container">
              <Cropper
                image={imageToCrop}
                crop={crop}
                zoom={zoom}
                aspect={1}
                cropShape="round"
                showGrid={false}
                onCropChange={setCrop}
                onZoomChange={setZoom}
                onCropComplete={onCropComplete}
              />
            </div>

            <div className="crop-controls">
              <div className="zoom-control">
                <label className="zoom-label">Zoom</label>
                <input
                  type="range"
                  min={1}
                  max={3}
                  step={0.1}
                  value={zoom}
                  onChange={(e) => setZoom(parseFloat(e.target.value))}
                  className="zoom-slider"
                />
              </div>
            </div>

            <div className="modal-actions">
              <button
                type="button"
                className="btn-modal-cancel"
                onClick={handleCropCancel}
              >
                Cancel
              </button>
              <button
                type="button"
                className="btn-modal-save"
                onClick={handleCropSave}
              >
                Save Photo
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Account Modal */}
      {showDeleteModal && (
        <div className="modal-overlay">
          <div className="delete-modal">
            <div className="modal-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 6h18M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
                <line x1="10" y1="11" x2="10" y2="17"></line>
                <line x1="14" y1="11" x2="14" y2="17"></line>
              </svg>
            </div>
            <h2 className="modal-title">Delete Account</h2>
            <p className="modal-description">
              This action cannot be undone. This will permanently delete your account and remove all your data from our servers.
            </p>
            <div className="modal-confirm-section">
              <label className="confirm-label">
                Type <strong>DELETE</strong> to confirm:
              </label>
              <input
                type="text"
                className="confirm-input"
                value={deleteConfirmText}
                onChange={(e) => setDeleteConfirmText(e.target.value)}
                placeholder="DELETE"
              />
            </div>
            <div className="modal-actions">
              <button
                type="button"
                className="btn-modal-cancel"
                onClick={() => {
                  setShowDeleteModal(false);
                  setDeleteConfirmText('');
                }}
              >
                Cancel
              </button>
              <button
                type="button"
                className="btn-modal-delete"
                onClick={handleDeleteAccount}
                disabled={deleting || deleteConfirmText !== 'DELETE'}
              >
                {deleting ? (
                  <>
                    <span className="loading-spinner"></span>Deleting...
                  </>
                ) : (
                  'Delete Account'
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        /* Import Playfair Display for headings */
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');

        /* ===== PAGE CONTAINER ===== */
        .profile-page {
          min-height: 100vh;
          width: 100%;
          background: linear-gradient(135deg, #030305 0%, #08080f 50%, #050508 100%);
          position: relative;
          overflow-x: hidden;
        }

        /* ===== BACKGROUND LIGHT RAYS ===== */
        .page-background {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          pointer-events: none;
          overflow: hidden;
          z-index: 0;
        }

        .light-ray {
          position: absolute;
          background: linear-gradient(180deg, rgba(64, 117, 201, 0.08) 0%, transparent 100%);
          transform-origin: top left;
        }

        .ray-1 {
          width: 600px;
          height: 150%;
          top: -20%;
          left: -10%;
          transform: rotate(25deg);
        }

        .ray-2 {
          width: 400px;
          height: 120%;
          top: -10%;
          left: 5%;
          transform: rotate(35deg);
          opacity: 0.5;
        }

        /* Navigation styles come from people.css */

        /* ===== PAGE HEADER ===== */
        .page-header {
          padding: 140px 60px 40px;
          position: relative;
          z-index: 10;
        }

        .header-content {
          max-width: 1400px;
          margin: 0 auto;
        }

        .header-text {
          flex: 1;
        }

        .header-label {
          font-family: 'Inter', sans-serif;
          font-size: 12px;
          font-weight: 500;
          letter-spacing: 0.3em;
          color: #C4BFC0;
          display: block;
          margin-bottom: 12px;
        }

        .header-title {
          font-family: 'Playfair Display', serif;
          font-size: 56px;
          font-weight: 400;
          color: #ffffff;
          line-height: 1;
          margin: 0 0 20px 0;
        }

        .header-divider {
          width: 40px;
          height: 2px;
          background: #C4BFC0;
          margin-bottom: 16px;
        }

        .header-subtitle {
          font-family: 'Inter', sans-serif;
          font-size: 15px;
          font-weight: 300;
          color: #C4BFC0;
          line-height: 1.6;
          margin: 0;
        }

        /* ===== MAIN CONTENT ===== */
        .profile-main {
          padding: 0 60px 80px;
          position: relative;
          z-index: 10;
          max-width: 1520px;
          margin: 0 auto;
        }

        .profile-content {
          display: grid;
          grid-template-columns: 1fr 380px;
          gap: 32px;
        }

        .profile-editor {
          background: rgba(255, 255, 255, 0.02);
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-radius: 16px;
          padding: 32px;
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
        }

        .form-section {
          margin-bottom: 40px;
        }

        .section-header-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 20px;
        }

        .section-title {
          font-family: 'Inter', sans-serif;
          font-size: 11px;
          font-weight: 600;
          letter-spacing: 0.15em;
          text-transform: uppercase;
          color: #C4BFC0;
          margin-bottom: 20px;
          padding-bottom: 12px;
          border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .section-header-row .section-title {
          border-bottom: none;
          padding-bottom: 0;
          margin-bottom: 0;
        }

        .section-description {
          font-family: 'Inter', sans-serif;
          font-size: 14px;
          font-weight: 300;
          color: #C4BFC0;
          margin-bottom: 20px;
          line-height: 1.6;
        }

        .add-item-btn {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 10px 18px;
          background: rgba(64, 117, 201, 0.15);
          border: 1px solid rgba(64, 117, 201, 0.3);
          border-radius: 4px;
          color: #4075C9;
          font-family: 'Inter', sans-serif;
          font-size: 13px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .add-item-btn:hover {
          background: rgba(64, 117, 201, 0.25);
          border-color: #4075C9;
          color: #ffffff;
        }

        .items-list {
          display: flex;
          flex-direction: column;
          gap: 16px;
          margin-top: 16px;
        }

        .item-row {
          display: flex;
          align-items: center;
          gap: 16px;
        }

        .item-number {
          min-width: 70px;
          font-family: 'Inter', sans-serif;
          font-size: 12px;
          font-weight: 500;
          color: rgba(196, 191, 192, 0.7);
        }

        .item-input {
          flex: 1;
        }

        .remove-item-btn {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 36px;
          height: 36px;
          padding: 0;
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid rgba(239, 68, 68, 0.2);
          border-radius: 4px;
          color: #fca5a5;
          cursor: pointer;
          transition: all 0.3s ease;
          flex-shrink: 0;
        }

        .remove-item-btn:hover {
          background: rgba(239, 68, 68, 0.2);
          border-color: rgba(239, 68, 68, 0.4);
        }

        .form-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
        }

        .form-group {
          margin-bottom: 20px;
        }

        .form-group.full-width {
          grid-column: 1 / -1;
        }

        .form-label {
          display: block;
          font-family: 'Inter', sans-serif;
          font-size: 13px;
          font-weight: 500;
          color: #C4BFC0;
          margin-bottom: 10px;
        }

        .form-input, .form-textarea {
          width: 100%;
          padding: 12px 16px;
          font-size: 14px;
          font-family: 'Inter', sans-serif;
          background: rgba(255, 255, 255, 0.03);
          border: 1px solid rgba(196, 191, 192, 0.2);
          border-radius: 4px;
          color: #ffffff;
          transition: all 0.3s ease;
          outline: none;
          line-height: 1.5;
        }

        .form-textarea {
          resize: vertical;
          min-height: 120px;
        }

        .email-template-textarea {
          min-height: 160px;
          font-family: 'Inter', sans-serif;
          line-height: 1.7;
        }

        .form-input:focus, .form-textarea:focus {
          border-color: #4075C9;
          background: rgba(64, 117, 201, 0.05);
          box-shadow: 0 0 0 3px rgba(64, 117, 201, 0.1);
        }

        .form-input::placeholder, .form-textarea::placeholder {
          color: rgba(196, 191, 192, 0.5);
        }

        .profile-pic-section {
          display: flex;
          align-items: center;
          gap: 24px;
          margin-bottom: 40px;
          padding-bottom: 32px;
          border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }

        .profile-pic-preview {
          width: 100px;
          height: 100px;
          border-radius: 50%;
          background: linear-gradient(135deg, #4075C9 0%, #2a5699 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          font-family: 'Inter', sans-serif;
          font-size: 40px;
          font-weight: 600;
          color: white;
          overflow: hidden;
          border: 2px solid rgba(255, 255, 255, 0.15);
        }

        .profile-pic-preview img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .profile-pic-upload {
          flex: 1;
        }

        .upload-btn {
          background: transparent;
          color: #C4BFC0;
          border: 1px solid rgba(196, 191, 192, 0.3);
          padding: 12px 24px;
          border-radius: 4px;
          font-family: 'Inter', sans-serif;
          font-weight: 500;
          font-size: 14px;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .upload-btn:hover {
          background: rgba(64, 117, 201, 0.1);
          border-color: #4075C9;
          color: #ffffff;
        }

        .profile-actions {
          display: flex;
          gap: 16px;
          margin-top: 40px;
          padding-top: 32px;
          border-top: 1px solid rgba(255, 255, 255, 0.08);
        }

        .btn-save {
          flex: 1;
          background: rgba(64, 117, 201, 0.15);
          color: #ffffff;
          font-family: 'Inter', sans-serif;
          font-weight: 500;
          font-size: 14px;
          padding: 14px 32px;
          border-radius: 4px;
          border: 1px solid #4075C9;
          cursor: pointer;
          transition: all 0.3s ease;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
        }

        .btn-save:hover:not(:disabled) {
          background: rgba(64, 117, 201, 0.25);
          box-shadow: 0 4px 20px rgba(64, 117, 201, 0.2);
        }

        .btn-save:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .btn-cancel {
          background: transparent;
          color: #C4BFC0;
          border: 1px solid rgba(196, 191, 192, 0.2);
          padding: 14px 32px;
          border-radius: 4px;
          font-family: 'Inter', sans-serif;
          font-weight: 500;
          font-size: 14px;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .btn-cancel:hover {
          border-color: rgba(196, 191, 192, 0.4);
          color: #ffffff;
        }

        /* ===== PREVIEW CARD ===== */
        .profile-preview {
          position: sticky;
          top: 100px;
          height: fit-content;
        }

        .preview-card {
          background: rgba(255, 255, 255, 0.02);
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-radius: 16px;
          padding: 24px;
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
        }

        .preview-title {
          font-family: 'Inter', sans-serif;
          font-size: 10px;
          font-weight: 600;
          letter-spacing: 0.1em;
          text-transform: uppercase;
          color: #4075C9;
          margin-bottom: 4px;
        }

        .preview-subtitle {
          font-family: 'Inter', sans-serif;
          font-size: 14px;
          font-weight: 400;
          color: rgba(196, 191, 192, 0.8);
          margin-bottom: 20px;
          line-height: 1.5;
        }

        /* Alumni Card Preview - Matching Main Page Style */
        .alumni-card-preview {
          background: rgba(255, 255, 255, 0.02);
          backdrop-filter: blur(20px) saturate(120%);
          -webkit-backdrop-filter: blur(20px) saturate(120%);
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-radius: 16px;
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
          overflow: hidden;
          display: flex;
          flex-direction: column;
          height: 380px;
        }

        .preview-image-section {
          position: relative;
          height: 65%;
          width: 100%;
          background: #000000;
          overflow: hidden;
        }

        .preview-image {
          width: 100%;
          height: 100%;
          object-fit: cover;
          display: block;
        }

        .preview-image-fallback {
          width: 100%;
          height: 100%;
          background: #000000;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .preview-image-fallback img {
          max-width: 50%;
          max-height: 50%;
          object-fit: contain;
          opacity: 0.3;
        }

        .preview-image-gradient {
          position: absolute;
          bottom: 0;
          left: 0;
          right: 0;
          height: 50%;
          background: linear-gradient(
            to bottom,
            transparent 0%,
            rgba(0, 0, 0, 0.4) 30%,
            rgba(0, 0, 0, 0.8) 70%,
            #000000 100%
          );
          pointer-events: none;
          z-index: 1;
        }

        .preview-body {
          flex: 1;
          width: 100%;
          padding: 20px;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          flex-direction: column;
          gap: 6px;
          justify-content: flex-start;
          position: relative;
          z-index: 2;
        }

        .preview-name {
          font-family: 'Playfair Display', serif;
          font-size: 20px;
          font-weight: 500;
          color: #ffffff;
          margin: 0;
          line-height: 1.2;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .preview-role {
          font-family: 'Inter', sans-serif;
          font-size: 14px;
          font-weight: 500;
          color: rgba(255, 255, 255, 0.9);
          margin: 0;
          line-height: 1.4;
          overflow: hidden;
          text-overflow: ellipsis;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
        }

        .preview-company {
          font-family: 'Inter', sans-serif;
          font-size: 13px;
          font-weight: 400;
          color: rgba(255, 255, 255, 0.7);
          margin: 0;
          line-height: 1.4;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .preview-info {
          font-family: 'Inter', sans-serif;
          font-size: 12px;
          font-weight: 400;
          color: rgba(196, 191, 192, 0.7);
          margin: 4px 0 0 0;
          line-height: 1.5;
        }

        /* ===== MESSAGES ===== */
        .message-box {
          padding: 12px 16px;
          border-radius: 4px;
          font-family: 'Inter', sans-serif;
          font-size: 14px;
          margin-bottom: 20px;
        }

        .message-success {
          background: rgba(34, 197, 94, 0.1);
          border: 1px solid rgba(34, 197, 94, 0.3);
          color: #86efac;
        }

        .message-error {
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid rgba(239, 68, 68, 0.3);
          color: #fca5a5;
        }

        .loading-spinner {
          display: inline-block;
          width: 16px;
          height: 16px;
          border: 2px solid rgba(255, 255, 255, 0.3);
          border-top-color: #ffffff;
          border-radius: 50%;
          animation: spin 0.6s linear infinite;
          margin-right: 8px;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        /* ===== DANGER ZONE ===== */
        .danger-zone {
          margin-top: 56px;
          padding: 28px;
          border: 1px solid rgba(239, 68, 68, 0.3);
          border-radius: 16px;
          background: rgba(239, 68, 68, 0.05);
        }

        .danger-title {
          font-family: 'Inter', sans-serif;
          font-size: 11px;
          font-weight: 600;
          letter-spacing: 0.15em;
          text-transform: uppercase;
          color: #fca5a5;
          margin-bottom: 12px;
        }

        .danger-description {
          font-family: 'Inter', sans-serif;
          font-size: 14px;
          font-weight: 400;
          color: #C4BFC0;
          margin-bottom: 20px;
          line-height: 1.6;
        }

        .btn-delete-account {
          background: rgba(239, 68, 68, 0.1);
          color: #fca5a5;
          border: 1px solid rgba(239, 68, 68, 0.3);
          padding: 12px 24px;
          border-radius: 4px;
          font-family: 'Inter', sans-serif;
          font-weight: 500;
          font-size: 14px;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .btn-delete-account:hover {
          background: rgba(239, 68, 68, 0.2);
          border-color: rgba(239, 68, 68, 0.5);
          color: #f87171;
        }

        /* ===== CROP MODAL ===== */
        .crop-modal {
          background: linear-gradient(135deg, #0a0a12 0%, #08080f 100%);
          border: 1px solid rgba(64, 117, 201, 0.3);
          border-radius: 16px;
          padding: 32px;
          max-width: 600px;
          width: 100%;
          text-align: center;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        }

        .crop-container {
          position: relative;
          width: 100%;
          height: 400px;
          background: #000000;
          border-radius: 8px;
          overflow: hidden;
          margin: 24px 0;
        }

        .crop-controls {
          margin-bottom: 24px;
        }

        .zoom-control {
          display: flex;
          flex-direction: column;
          gap: 12px;
          align-items: stretch;
        }

        .zoom-label {
          font-family: 'Inter', sans-serif;
          font-size: 13px;
          font-weight: 500;
          color: #C4BFC0;
          text-align: left;
        }

        .zoom-slider {
          width: 100%;
          height: 6px;
          border-radius: 3px;
          background: rgba(255, 255, 255, 0.1);
          outline: none;
          -webkit-appearance: none;
          appearance: none;
        }

        .zoom-slider::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          width: 18px;
          height: 18px;
          border-radius: 50%;
          background: #4075C9;
          cursor: pointer;
          border: 2px solid #ffffff;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }

        .zoom-slider::-moz-range-thumb {
          width: 18px;
          height: 18px;
          border-radius: 50%;
          background: #4075C9;
          cursor: pointer;
          border: 2px solid #ffffff;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }

        .btn-modal-save {
          flex: 1;
          background: rgba(64, 117, 201, 0.15);
          color: #ffffff;
          border: 1px solid #4075C9;
          padding: 14px 24px;
          border-radius: 4px;
          font-family: 'Inter', sans-serif;
          font-weight: 500;
          font-size: 14px;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .btn-modal-save:hover {
          background: rgba(64, 117, 201, 0.25);
          border-color: rgba(64, 117, 201, 0.6);
        }

        /* ===== DELETE MODAL ===== */
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.8);
          backdrop-filter: blur(4px);
          -webkit-backdrop-filter: blur(4px);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          padding: 1rem;
        }

        .delete-modal {
          background: linear-gradient(135deg, #0a0a12 0%, #08080f 100%);
          border: 1px solid rgba(239, 68, 68, 0.3);
          border-radius: 16px;
          padding: 32px;
          max-width: 440px;
          width: 100%;
          text-align: center;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        }

        .modal-icon {
          width: 72px;
          height: 72px;
          margin: 0 auto 20px;
          background: rgba(239, 68, 68, 0.1);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #f87171;
        }

        .modal-title {
          font-family: 'Playfair Display', serif;
          font-size: 28px;
          font-weight: 500;
          color: #ffffff;
          margin-bottom: 12px;
        }

        .modal-description {
          font-family: 'Inter', sans-serif;
          font-size: 14px;
          font-weight: 300;
          color: #C4BFC0;
          margin-bottom: 24px;
          line-height: 1.6;
        }

        .modal-confirm-section {
          text-align: left;
          margin-bottom: 24px;
        }

        .confirm-label {
          display: block;
          font-family: 'Inter', sans-serif;
          font-size: 14px;
          color: #C4BFC0;
          margin-bottom: 8px;
        }

        .confirm-label strong {
          color: #f87171;
        }

        .confirm-input {
          width: 100%;
          padding: 10px 14px;
          font-size: 13px;
          font-family: 'Inter', sans-serif;
          background: rgba(255, 255, 255, 0.03);
          border: 1px solid rgba(196, 191, 192, 0.2);
          border-radius: 4px;
          color: #ffffff;
          transition: all 0.3s ease;
          outline: none;
        }

        .confirm-input:focus {
          border-color: rgba(239, 68, 68, 0.5);
          background: rgba(239, 68, 68, 0.05);
          box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
        }

        .modal-actions {
          display: flex;
          gap: 12px;
        }

        .btn-modal-cancel {
          flex: 1;
          background: transparent;
          color: #C4BFC0;
          border: 1px solid rgba(196, 191, 192, 0.2);
          padding: 14px 24px;
          border-radius: 4px;
          font-family: 'Inter', sans-serif;
          font-weight: 500;
          font-size: 14px;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .btn-modal-cancel:hover {
          border-color: rgba(196, 191, 192, 0.4);
          color: #ffffff;
        }

        .btn-modal-delete {
          flex: 1;
          background: rgba(239, 68, 68, 0.15);
          color: #fca5a5;
          border: 1px solid rgba(239, 68, 68, 0.3);
          padding: 14px 24px;
          border-radius: 4px;
          font-family: 'Inter', sans-serif;
          font-weight: 500;
          font-size: 14px;
          cursor: pointer;
          transition: all 0.3s ease;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
        }

        .btn-modal-delete:hover:not(:disabled) {
          background: rgba(239, 68, 68, 0.25);
          border-color: rgba(239, 68, 68, 0.5);
          color: #f87171;
        }

        .btn-modal-delete:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        /* ===== RESPONSIVE ===== */
        @media (max-width: 1200px) {
          .page-header {
            padding: 120px 40px 32px;
          }

          .header-title {
            font-size: 44px;
          }

          .profile-main {
            padding: 0 40px 60px;
          }
        }

        @media (max-width: 1024px) {
          .profile-content {
            grid-template-columns: 1fr;
          }

          .profile-preview {
            display: none;
          }
        }

        @media (max-width: 900px) {
          .page-header {
            padding: 100px 24px 24px;
          }

          .header-title {
            font-size: 36px;
          }

          .profile-main {
            padding: 0 24px 40px;
          }
        }

        @media (max-width: 768px) {
          .form-grid {
            grid-template-columns: 1fr;
          }
        }

        @media (max-width: 600px) {
          .item-row {
            flex-wrap: wrap;
          }
          .item-number {
            min-width: 100%;
            margin-bottom: 4px;
          }
          .item-input {
            flex: 1;
            min-width: calc(100% - 52px);
          }
          .profile-pic-section {
            flex-direction: column;
            text-align: center;
          }
          .profile-pic-upload {
            width: 100%;
          }
        }

        @media (max-width: 576px) {
          .page-header {
            padding: 90px 16px 20px;
          }

          .header-title {
            font-size: 28px;
          }

          .profile-main {
            padding: 0 16px 32px;
          }

          .profile-editor {
            padding: 20px;
          }
        }
      `}</style>
    </div>
  );
};

export default ProfilePage;
