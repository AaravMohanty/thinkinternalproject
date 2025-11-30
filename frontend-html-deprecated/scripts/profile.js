/**
 * Profile Editor Script
 * Handles profile editing, live preview updates, and profile picture upload
 */

// API Configuration
const API_BASE_URL = 'http://localhost:5001';

// State
let originalProfile = null;
let uploadedProfilePic = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
  // Initialize auth - this validates/refreshes the session
  const user = await Auth.init();

  if (!user) {
    // Session invalid or refresh failed - redirect to login
    window.location.href = 'login.html';
    return;
  }

  // Initialize profile dropdown in navbar
  initProfileDropdown();

  // Load user profile
  await loadProfile();

  // Set up event listeners
  setupEventListeners();

  // Initialize preview
  updatePreview();

  // Update nav avatar after profile loads
  const userData = Auth.getUserData();
  if (userData) {
    updateNavAvatar(userData);
  }
});

/**
 * Load user profile from API
 */
async function loadProfile() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/profile`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${Auth.getToken()}`,
        'Content-Type': 'application/json'
      }
    });

    const data = await response.json();

    if (response.ok && data.success) {
      originalProfile = data.profile;
      populateForm(data.profile);
    } else {
      showError('Failed to load profile: ' + (data.error || 'Unknown error'));
    }
  } catch (error) {
    console.error('Error loading profile:', error);
    showError('Failed to load profile. Please try again.');
  }
}

/**
 * Populate form with profile data
 */
function populateForm(profile) {
  // Basic Information
  document.getElementById('fullName').value = profile.full_name || '';
  document.getElementById('personalEmail').value = profile.personal_email || '';
  document.getElementById('phone').value = profile.phone || '';

  // Academic
  document.getElementById('major').value = profile.major || '';
  document.getElementById('graduationYear').value = profile.graduation_year || '';

  // Professional
  document.getElementById('currentCompany').value = profile.current_company || '';
  document.getElementById('currentTitle').value = profile.current_title || '';
  document.getElementById('location').value = profile.location || '';
  document.getElementById('linkedinUrl').value = profile.linkedin_url || '';
  document.getElementById('bio').value = profile.bio || '';

  // Career Interests
  if (profile.career_interests && Array.isArray(profile.career_interests)) {
    document.getElementById('careerInterests').value = profile.career_interests.join(', ');
  } else if (typeof profile.career_interests === 'string') {
    document.getElementById('careerInterests').value = profile.career_interests;
  }

  // Profile Picture
  if (profile.profile_image_url) {
    setProfilePicture(profile.profile_image_url);
  } else {
    // Show initials
    const initials = getInitials(profile.full_name || '');
    document.getElementById('profileInitials').textContent = initials;
    document.getElementById('previewInitials').textContent = initials;
  }
}

/**
 * Set up event listeners
 */
function setupEventListeners() {
  // Real-time preview updates for all form inputs
  const formInputs = [
    'fullName', 'currentCompany', 'currentTitle', 'major',
    'graduationYear', 'location', 'careerInterests'
  ];

  formInputs.forEach(inputId => {
    const input = document.getElementById(inputId);
    if (input) {
      input.addEventListener('input', updatePreview);
    }
  });

  // Profile picture upload
  document.getElementById('profilePicInput').addEventListener('change', handleProfilePicUpload);

  // Save button
  document.getElementById('saveBtn').addEventListener('click', saveProfile);

  // Cancel button
  document.getElementById('cancelBtn').addEventListener('click', cancelEdit);

  // Logout button
  document.getElementById('logoutBtn').addEventListener('click', (e) => {
    e.preventDefault();
    Auth.logout();
  });

  // Check if user is director and show admin link
  checkAdminAccess();
}

/**
 * Update live preview card
 */
function updatePreview() {
  const fullName = document.getElementById('fullName').value || 'Your Name';
  const currentTitle = document.getElementById('currentTitle').value;
  const currentCompany = document.getElementById('currentCompany').value;
  const major = document.getElementById('major').value || 'Your Major';
  const graduationYear = document.getElementById('graduationYear').value || '2025';
  const location = document.getElementById('location').value;
  const careerInterests = document.getElementById('careerInterests').value;

  // Update name
  document.getElementById('previewName').textContent = fullName;

  // Update title/company
  let titleText = '';
  if (currentTitle && currentCompany) {
    titleText = `${currentTitle} at ${currentCompany}`;
  } else if (currentTitle) {
    titleText = currentTitle;
  } else if (currentCompany) {
    titleText = currentCompany;
  } else {
    titleText = 'Add your title and company';
  }
  document.getElementById('previewTitle').textContent = titleText;

  // Update major
  document.getElementById('previewMajor').textContent = major;

  // Update grad year
  document.getElementById('previewGradYear').textContent = `Class of ${graduationYear}`;

  // Update location
  const locationRow = document.getElementById('previewLocationRow');
  if (location) {
    document.getElementById('previewLocation').textContent = location;
    locationRow.style.display = 'flex';
  } else {
    locationRow.style.display = 'none';
  }

  // Update industries
  const industriesContainer = document.getElementById('previewIndustries');
  industriesContainer.innerHTML = '';

  if (careerInterests) {
    const industries = careerInterests.split(',').map(i => i.trim()).filter(i => i);
    industries.slice(0, 3).forEach(industry => {
      const tag = document.createElement('span');
      tag.className = 'industry-tag';
      tag.textContent = industry;
      industriesContainer.appendChild(tag);
    });
  }

  // Update initials if no profile pic
  const profilePicImg = document.getElementById('profilePicImg');
  if (!profilePicImg.style.display || profilePicImg.style.display === 'none') {
    const initials = getInitials(fullName);
    document.getElementById('profileInitials').textContent = initials;
    document.getElementById('previewInitials').textContent = initials;
  }
}

/**
 * Handle profile picture upload
 */
async function handleProfilePicUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  // Validate file type
  if (!file.type.startsWith('image/')) {
    showError('Please select a valid image file');
    return;
  }

  // Validate file size (max 5MB)
  if (file.size > 5 * 1024 * 1024) {
    showError('Image size must be less than 5MB');
    return;
  }

  // Preview the image
  const reader = new FileReader();
  reader.onload = (e) => {
    setProfilePicture(e.target.result);
  };
  reader.readAsDataURL(file);

  // Store the file for upload on save
  uploadedProfilePic = file;
}

/**
 * Set profile picture preview
 */
function setProfilePicture(imageUrl) {
  // Main profile picture
  const profilePicImg = document.getElementById('profilePicImg');
  const profileInitials = document.getElementById('profileInitials');

  profilePicImg.src = imageUrl;
  profilePicImg.style.display = 'block';
  profileInitials.style.display = 'none';

  // Preview card avatar
  const previewAvatarImg = document.getElementById('previewAvatarImg');
  const previewInitials = document.getElementById('previewInitials');

  previewAvatarImg.src = imageUrl;
  previewAvatarImg.style.display = 'block';
  previewInitials.style.display = 'none';
}

/**
 * Get initials from full name
 */
function getInitials(name) {
  if (!name) return 'U';
  const parts = name.trim().split(' ');
  if (parts.length === 1) {
    return parts[0].charAt(0).toUpperCase();
  }
  return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
}

/**
 * Save profile changes
 */
async function saveProfile() {
  const saveBtn = document.getElementById('saveBtn');

  // Validate required fields
  const fullName = document.getElementById('fullName').value.trim();
  const major = document.getElementById('major').value.trim();
  const graduationYear = document.getElementById('graduationYear').value.trim();

  if (!fullName || !major || !graduationYear) {
    showError('Please fill in all required fields (Name, Major, Graduation Year)');
    return;
  }

  // Disable save button
  saveBtn.disabled = true;
  saveBtn.innerHTML = '<span class="loading-spinner"></span>Saving...';

  try {
    // Prepare profile data
    const careerInterestsValue = document.getElementById('careerInterests').value;
    const careerInterests = careerInterestsValue
      ? careerInterestsValue.split(',').map(i => i.trim()).filter(i => i)
      : [];

    const profileData = {
      full_name: fullName,
      personal_email: document.getElementById('personalEmail').value.trim(),
      phone: document.getElementById('phone').value.trim(),
      major: major,
      graduation_year: parseInt(graduationYear),
      current_company: document.getElementById('currentCompany').value.trim(),
      current_title: document.getElementById('currentTitle').value.trim(),
      location: document.getElementById('location').value.trim(),
      linkedin_url: document.getElementById('linkedinUrl').value.trim(),
      bio: document.getElementById('bio').value.trim(),
      career_interests: careerInterests
    };

    // TODO: Upload profile picture to Supabase Storage if changed
    // For now, we'll skip this and handle it in a future iteration

    // Update profile via API
    const response = await fetch(`${API_BASE_URL}/api/profile`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${Auth.getToken()}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(profileData)
    });

    const data = await response.json();

    if (response.ok && data.success) {
      originalProfile = data.profile;
      showSuccess('Profile updated successfully!');

      // Update user data in localStorage
      const userData = Auth.getUserData();
      if (userData) {
        userData.full_name = fullName;
        userData.profile_image_url = data.profile.profile_image_url;
        Auth.setUserData(userData);
      }

      // Clear uploaded pic state
      uploadedProfilePic = null;
    } else {
      showError('Failed to save profile: ' + (data.error || 'Unknown error'));
    }
  } catch (error) {
    console.error('Error saving profile:', error);
    showError('Failed to save profile. Please try again.');
  } finally {
    // Re-enable save button
    saveBtn.disabled = false;
    saveBtn.textContent = 'Save Changes';
  }
}

/**
 * Cancel edit and restore original values
 */
function cancelEdit() {
  if (originalProfile) {
    populateForm(originalProfile);
    updatePreview();
    uploadedProfilePic = null;
    hideMessages();
  }
}

/**
 * Show success message
 */
function showSuccess(message) {
  hideMessages();
  const successBox = document.getElementById('successMessage');
  successBox.textContent = message;
  successBox.classList.add('show');

  // Auto-hide after 5 seconds
  setTimeout(() => {
    successBox.classList.remove('show');
  }, 5000);
}

/**
 * Show error message
 */
function showError(message) {
  hideMessages();
  const errorBox = document.getElementById('errorMessage');
  errorBox.textContent = message;
  errorBox.classList.add('show');

  // Auto-hide after 8 seconds
  setTimeout(() => {
    errorBox.classList.remove('show');
  }, 8000);
}

/**
 * Hide all messages
 */
function hideMessages() {
  document.getElementById('successMessage').classList.remove('show');
  document.getElementById('errorMessage').classList.remove('show');
}

/**
 * Check if user has admin access
 */
async function checkAdminAccess() {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/session`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${Auth.getToken()}`
      }
    });

    const data = await response.json();

    if (response.ok && data.success && data.user) {
      // Show admin link if user is director
      if (data.user.is_director) {
        const adminLink = document.getElementById('adminLink');
        if (adminLink) {
          adminLink.style.display = 'flex';
          adminLink.href = 'admin.html';
        }
      }
    }
  } catch (error) {
    console.error('Error checking admin access:', error);
  }
}

/**
 * Initialize the profile dropdown in navbar
 */
function initProfileDropdown() {
  const profileDropdown = document.getElementById('profileDropdown');
  const profileAvatarBtn = document.getElementById('profileAvatarBtn');

  if (!profileDropdown || !profileAvatarBtn) return;

  // Update avatar with user data
  const userData = Auth.getUserData();
  if (userData) {
    updateNavAvatar(userData);
  }

  // Toggle dropdown on click
  profileAvatarBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    profileDropdown.classList.toggle('open');
  });

  // Close dropdown when clicking outside
  document.addEventListener('click', (e) => {
    if (!profileDropdown.contains(e.target)) {
      profileDropdown.classList.remove('open');
    }
  });

  // Close dropdown on escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      profileDropdown.classList.remove('open');
    }
  });
}

/**
 * Update navbar avatar with user data
 */
function updateNavAvatar(userData) {
  const avatarImg = document.getElementById('navProfileAvatarImg');
  const avatarInitials = document.getElementById('navProfileAvatarInitials');

  if (!avatarImg || !avatarInitials) return;

  if (userData.profile_image_url) {
    avatarImg.src = userData.profile_image_url;
    avatarImg.style.display = 'block';
    avatarInitials.style.display = 'none';
  } else {
    const name = userData.full_name || userData.profile?.full_name || 'User';
    const initials = name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
    avatarInitials.textContent = initials || 'U';
    avatarImg.style.display = 'none';
    avatarInitials.style.display = 'flex';
  }
}
