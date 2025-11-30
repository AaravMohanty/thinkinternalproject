/**
 * Multi-step Signup Flow
 * Handles account creation, resume upload, and profile completion
 */

let currentStep = 1;
const totalSteps = 3;
let uploadedResume = null;
let userId = null;
let authToken = null;

// DOM Elements
const step1 = document.getElementById('step1');
const step2 = document.getElementById('step2');
const step3 = document.getElementById('step3');
const backBtn = document.getElementById('backBtn');
const nextBtn = document.getElementById('nextBtn');
const errorMessage = document.getElementById('errorMessage');
const successMessage = document.getElementById('successMessage');
const progressLine = document.getElementById('progressLine');
const fileUploadArea = document.getElementById('fileUploadArea');
const resumeFileInput = document.getElementById('resumeFile');
const fileName = document.getElementById('fileName');

// Check if already logged in
if (Auth.isAuthenticated()) {
  window.location.href = 'home.html';
}

// Step Navigation
function updateStepUI() {
  // Update progress steps
  document.querySelectorAll('.step').forEach((step, index) => {
    const stepNum = index + 1;
    step.classList.remove('active', 'completed');

    if (stepNum < currentStep) {
      step.classList.add('completed');
    } else if (stepNum === currentStep) {
      step.classList.add('active');
    }
  });

  // Update progress line
  const progress = ((currentStep - 1) / (totalSteps - 1)) * 100;
  progressLine.style.width = `${progress}%`;

  // Show/hide form sections
  document.querySelectorAll('.form-section').forEach((section) => {
    section.classList.remove('active');
  });

  if (currentStep === 1) {
    step1.classList.add('active');
    backBtn.disabled = true;
    nextBtn.textContent = 'Next';
  } else if (currentStep === 2) {
    step2.classList.add('active');
    backBtn.disabled = false;
    nextBtn.textContent = uploadedResume ? 'Next' : 'Skip Resume Upload';
  } else if (currentStep === 3) {
    step3.classList.add('active');
    backBtn.disabled = true; // Can't go back after account creation
    nextBtn.textContent = 'Complete Signup';
  }
}

// Validation Functions
function validateStep1() {
  const fullName = document.getElementById('fullName').value.trim();
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  const confirmPassword = document.getElementById('confirmPassword').value;
  const referralCode = document.getElementById('referralCode').value.trim();

  if (!fullName) {
    showError('Please enter your full name');
    return false;
  }

  if (!email || !email.includes('@')) {
    showError('Please enter a valid email address');
    return false;
  }

  if (password.length < 8) {
    showError('Password must be at least 8 characters long');
    return false;
  }

  if (password !== confirmPassword) {
    showError('Passwords do not match');
    return false;
  }

  if (!referralCode) {
    showError('Please enter a referral code');
    return false;
  }

  return true;
}

function validateStep3() {
  const major = document.getElementById('major').value.trim();
  const graduationYear = document.getElementById('graduationYear').value;

  if (!major) {
    showError('Please enter your major');
    return false;
  }

  if (!graduationYear || graduationYear < 1950 || graduationYear > 2030) {
    showError('Please enter a valid graduation year');
    return false;
  }

  return true;
}

// API Functions
async function createAccount() {
  const fullName = document.getElementById('fullName').value.trim();
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  const referralCode = document.getElementById('referralCode').value.trim();

  showLoading('Creating account...');

  const result = await Auth.signup({
    email,
    password,
    referralCode,
    fullName,
  });

  if (result.success) {
    // Now login to get the token
    const loginResult = await Auth.login(email, password);

    if (loginResult.success) {
      authToken = Auth.getToken();
      userId = loginResult.user.user_id;
      return true;
    } else {
      // Account created but auto-login failed
      console.error('Auto-login failed:', loginResult.error);
      showError('Account created successfully! Redirecting to login page...');
      setTimeout(() => {
        window.location.href = `login.html?email=${encodeURIComponent(email)}`;
      }, 2000);
      return false;
    }
  } else {
    showError(result.error);
    return false;
  }
}

async function uploadResume() {
  if (!uploadedResume) {
    return true; // Skip if no resume
  }

  showLoading('Uploading and parsing resume...');

  try {
    const formData = new FormData();
    formData.append('resume', uploadedResume);

    const response = await Auth.authenticatedFetch('/api/resume/upload', {
      method: 'POST',
      body: formData,
      headers: {}, // Don't set Content-Type, browser will set it for FormData
    });

    if (response.ok) {
      const data = await response.json();

      // Pre-fill profile fields with parsed data
      if (data.major) document.getElementById('major').value = data.major;
      if (data.graduation_year) document.getElementById('graduationYear').value = data.graduation_year;
      if (data.current_company) document.getElementById('currentCompany').value = data.current_company;
      if (data.current_title) document.getElementById('currentTitle').value = data.current_title;

      return true;
    } else {
      const error = await response.json();
      showError(error.error || 'Failed to upload resume. You can add it later from your profile.');
      return true; // Continue anyway
    }
  } catch (error) {
    console.error('Resume upload error:', error);
    showError('Failed to upload resume. You can add it later from your profile.');
    return true; // Continue anyway
  }
}

async function completeProfile() {
  const major = document.getElementById('major').value.trim();
  const graduationYear = parseInt(document.getElementById('graduationYear').value);
  const currentCompany = document.getElementById('currentCompany').value.trim();
  const currentTitle = document.getElementById('currentTitle').value.trim();
  const linkedinUrl = document.getElementById('linkedinUrl').value.trim();

  showLoading('Completing profile...');

  try {
    const response = await Auth.authenticatedFetch('/api/profile', {
      method: 'PUT',
      body: JSON.stringify({
        major,
        graduation_year: graduationYear,
        current_company: currentCompany || null,
        current_title: currentTitle || null,
        linkedin_url: linkedinUrl || null,
      }),
    });

    if (response.ok) {
      showSuccess('Profile completed successfully! Redirecting...');
      setTimeout(() => {
        window.location.href = 'home.html';
      }, 1500);
      return true;
    } else {
      const error = await response.json();
      showError(error.error || 'Failed to update profile');
      return false;
    }
  } catch (error) {
    console.error('Profile update error:', error);
    showError('Failed to update profile. Please try again.');
    return false;
  }
}

// Button Handlers
nextBtn.addEventListener('click', async () => {
  clearMessages();

  if (currentStep === 1) {
    if (validateStep1()) {
      const success = await createAccount();
      if (success) {
        currentStep++;
        updateStepUI();
      }
    }
  } else if (currentStep === 2) {
    const success = await uploadResume();
    if (success) {
      currentStep++;
      updateStepUI();
    }
  } else if (currentStep === 3) {
    if (validateStep3()) {
      await completeProfile();
    }
  }
});

backBtn.addEventListener('click', () => {
  if (currentStep > 1 && currentStep < 3) {
    clearMessages();
    currentStep--;
    updateStepUI();
  }
});

// File Upload Handlers
fileUploadArea.addEventListener('click', () => {
  resumeFileInput.click();
});

fileUploadArea.addEventListener('dragover', (e) => {
  e.preventDefault();
  fileUploadArea.classList.add('dragover');
});

fileUploadArea.addEventListener('dragleave', () => {
  fileUploadArea.classList.remove('dragover');
});

fileUploadArea.addEventListener('drop', (e) => {
  e.preventDefault();
  fileUploadArea.classList.remove('dragover');

  const files = e.dataTransfer.files;
  if (files.length > 0) {
    handleFileSelect(files[0]);
  }
});

resumeFileInput.addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (file) {
    handleFileSelect(file);
  }
});

function handleFileSelect(file) {
  // Validate file type
  if (file.type !== 'application/pdf') {
    showError('Please upload a PDF file');
    return;
  }

  // Validate file size (max 5MB)
  if (file.size > 5 * 1024 * 1024) {
    showError('File size must be less than 5MB');
    return;
  }

  uploadedResume = file;
  fileName.textContent = `📎 ${file.name}`;
  fileName.classList.add('show');
  nextBtn.textContent = 'Next';
}

// UI Helper Functions
function showError(message) {
  errorMessage.textContent = message;
  errorMessage.classList.add('show');
  successMessage.classList.remove('show');
  nextBtn.disabled = false;
  nextBtn.innerHTML = getNextBtnText();
}

function showSuccess(message) {
  successMessage.textContent = message;
  successMessage.classList.add('show');
  errorMessage.classList.remove('show');
}

function showLoading(message) {
  nextBtn.disabled = true;
  nextBtn.innerHTML = `<span class="loading-spinner"></span>${message}`;
  clearMessages();
}

function clearMessages() {
  errorMessage.classList.remove('show');
  errorMessage.textContent = '';
}

function getNextBtnText() {
  if (currentStep === 1) return 'Next';
  if (currentStep === 2) return uploadedResume ? 'Next' : 'Skip Resume Upload';
  if (currentStep === 3) return 'Complete Signup';
  return 'Next';
}

// Initialize
updateStepUI();
