/*
 * PurdueTHINK Alumni Finder JavaScript
 * Handles data fetching, filtering, and rendering
 */

const API_BASE_URL = 'http://localhost:5001/api';

let allAlumni = [];
let filteredAlumni = [];
let filterOptions = {
  majors: [],
  years: [],
  companies: [],
  industries: []
};

// DOM Elements
const alumniGrid = document.getElementById('alumniGrid');
const loadingSpinner = document.getElementById('loadingSpinner');
const noResults = document.getElementById('noResults');
const resultsCount = document.getElementById('resultsCount');
const filtersSidebar = document.getElementById('filtersSidebar');
const toggleFiltersBtn = document.getElementById('toggleFilters');

// Filter inputs
const searchNameInput = document.getElementById('searchName');
const searchTitleInput = document.getElementById('searchTitle');
const filterMajorSelect = document.getElementById('filterMajor');
const filterYearSelect = document.getElementById('filterYear');
const filterCompanySelect = document.getElementById('filterCompany');
const filterIndustrySelect = document.getElementById('filterIndustry');
const sortBySelect = document.getElementById('sortBy');
const sortAscendingCheckbox = document.getElementById('sortAscending');
const resetFiltersBtn = document.getElementById('resetFilters');

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
  await loadFilterOptions();
  await loadAlumni();
  setupEventListeners();
});

// Load filter options from API
async function loadFilterOptions() {
  try {
    const response = await fetch(`${API_BASE_URL}/filters`);
    const data = await response.json();

    if (data.success) {
      filterOptions = data.filters;
      populateFilterSelects();
    }
  } catch (error) {
    console.error('Error loading filter options:', error);
  }
}

// Populate filter select elements
function populateFilterSelects() {
  // Populate majors
  filterMajorSelect.innerHTML = filterOptions.majors
    .map(major => `<option value="${major}">${major}</option>`)
    .join('');

  // Populate years
  filterYearSelect.innerHTML = filterOptions.years
    .map(year => `<option value="${year}">${year}</option>`)
    .join('');

  // Populate companies
  filterCompanySelect.innerHTML = filterOptions.companies
    .map(company => `<option value="${company}">${company}</option>`)
    .join('');

  // Populate industries
  filterIndustrySelect.innerHTML = filterOptions.industries
    .map(industry => `<option value="${industry}">${industry}</option>`)
    .join('');

  // Setup search functionality for dropdowns
  setupFilterSearch();
}

// Setup search functionality for filter dropdowns
function setupFilterSearch() {
  const searchMajor = document.getElementById('searchMajor');
  const searchYear = document.getElementById('searchYear');
  const searchCompany = document.getElementById('searchCompany');
  const searchIndustry = document.getElementById('searchIndustry');

  if (searchMajor) {
    searchMajor.addEventListener('input', (e) => {
      filterSelectOptions(filterMajorSelect, e.target.value, filterOptions.majors);
    });
  }

  if (searchYear) {
    searchYear.addEventListener('input', (e) => {
      filterSelectOptions(filterYearSelect, e.target.value, filterOptions.years);
    });
  }

  if (searchCompany) {
    searchCompany.addEventListener('input', (e) => {
      filterSelectOptions(filterCompanySelect, e.target.value, filterOptions.companies);
    });
  }

  if (searchIndustry) {
    searchIndustry.addEventListener('input', (e) => {
      filterSelectOptions(filterIndustrySelect, e.target.value, filterOptions.industries);
    });
  }
}

// Filter options in a select element based on search query
function filterSelectOptions(selectElement, query, allOptions) {
  const lowerQuery = query.toLowerCase().trim();
  const selectedValues = Array.from(selectElement.selectedOptions).map(opt => opt.value);

  // If query is empty, show all options
  const filteredOptions = lowerQuery === ''
    ? allOptions
    : allOptions.filter(option => option.toString().toLowerCase().includes(lowerQuery));

  selectElement.innerHTML = filteredOptions
    .map(option => {
      const isSelected = selectedValues.includes(option);
      return `<option value="${option}" ${isSelected ? 'selected' : ''}>${option}</option>`;
    })
    .join('');

  // Show "No results" message if no options found
  if (filteredOptions.length === 0) {
    selectElement.innerHTML = '<option disabled>No results found</option>';
  }
}

// Load all alumni data
async function loadAlumni() {
  try {
    showLoading(true);

    const response = await fetch(`${API_BASE_URL}/alumni`);
    const data = await response.json();

    if (data.success) {
      allAlumni = data.data;
      applyFilters();
    } else {
      showError('Failed to load alumni data');
    }
  } catch (error) {
    console.error('Error loading alumni:', error);
    showError('Failed to connect to server. Make sure the backend is running.');
  } finally {
    showLoading(false);
  }
}

// Setup event listeners
function setupEventListeners() {
  // Filter inputs
  searchNameInput?.addEventListener('input', debounce(applyFilters, 300));
  searchTitleInput?.addEventListener('input', debounce(applyFilters, 300));
  filterMajorSelect?.addEventListener('change', applyFilters);
  filterYearSelect?.addEventListener('change', applyFilters);
  filterCompanySelect?.addEventListener('change', applyFilters);
  filterIndustrySelect?.addEventListener('change', applyFilters);
  sortBySelect?.addEventListener('change', applyFilters);
  sortAscendingCheckbox?.addEventListener('change', applyFilters);

  // Reset filters button
  resetFiltersBtn?.addEventListener('click', resetFilters);

  // Toggle filters sidebar on mobile
  toggleFiltersBtn?.addEventListener('click', () => {
    filtersSidebar?.classList.toggle('active');
  });

  // Close filters when clicking outside on mobile
  document.addEventListener('click', (e) => {
    if (window.innerWidth < 1024 &&
        filtersSidebar?.classList.contains('active') &&
        !filtersSidebar.contains(e.target) &&
        !toggleFiltersBtn.contains(e.target)) {
      filtersSidebar?.classList.remove('active');
    }
  });
}

// Apply all filters
function applyFilters() {
  const nameQuery = searchNameInput?.value.toLowerCase() || '';
  const titleQuery = searchTitleInput?.value.toLowerCase() || '';
  const selectedMajors = getSelectedOptions(filterMajorSelect);
  const selectedYears = getSelectedOptions(filterYearSelect);
  const selectedCompanies = getSelectedOptions(filterCompanySelect);
  const selectedIndustries = getSelectedOptions(filterIndustrySelect);

  filteredAlumni = allAlumni.filter(alumni => {
    // Name filter
    if (nameQuery && !alumni.name.toLowerCase().includes(nameQuery)) {
      return false;
    }

    // Title filter
    if (titleQuery) {
      const titleMatch = alumni.role_title.toLowerCase().includes(titleQuery) ||
                        alumni.headline?.toLowerCase().includes(titleQuery);
      if (!titleMatch) return false;
    }

    // Major filter
    if (selectedMajors.length > 0 && !selectedMajors.includes(alumni.major)) {
      return false;
    }

    // Year filter
    if (selectedYears.length > 0 && !selectedYears.includes(alumni.grad_year)) {
      return false;
    }

    // Company filter
    if (selectedCompanies.length > 0) {
      const hasCompany = alumni.companies_list?.some(c => selectedCompanies.includes(c));
      if (!hasCompany) return false;
    }

    // Industry filter
    if (selectedIndustries.length > 0 && !selectedIndustries.includes(alumni.company_industry)) {
      return false;
    }

    return true;
  });

  // Apply sorting
  sortAlumni();

  // Render results
  renderAlumni();
}

// Sort alumni based on selected criteria
function sortAlumni() {
  const sortBy = sortBySelect?.value || 'name';
  const ascending = sortAscendingCheckbox?.checked ?? true;

  filteredAlumni.sort((a, b) => {
    let aValue = a[sortBy] || '';
    let bValue = b[sortBy] || '';

    // Handle numeric sorting for grad_year
    if (sortBy === 'grad_year') {
      aValue = parseInt(aValue) || 0;
      bValue = parseInt(bValue) || 0;
    } else {
      aValue = aValue.toString().toLowerCase();
      bValue = bValue.toString().toLowerCase();
    }

    if (aValue < bValue) return ascending ? -1 : 1;
    if (aValue > bValue) return ascending ? 1 : -1;
    return 0;
  });
}

// Render alumni cards
function renderAlumni() {
  if (!alumniGrid) return;

  // Update results count
  if (resultsCount) {
    resultsCount.textContent = `Showing ${filteredAlumni.length} of ${allAlumni.length} alumni`;
  }

  // Show/hide no results message
  if (filteredAlumni.length === 0) {
    alumniGrid.innerHTML = '';
    noResults.style.display = 'block';
    return;
  }

  noResults.style.display = 'none';


  // Render cards
  alumniGrid.innerHTML = filteredAlumni.map(alumni => createAlumniCard(alumni)).join('');
}

// Create alumni card HTML
function createAlumniCard(alumni) {
  const profileImage = alumni.profile_image_url || '';
  const linkedinImage = alumni.linkedin_image_url || alumni.linkedinProfileImageUrl || '';
  const fallbackLogo = 'assets/Copy of P Logo for dark background (1).png';

  // Check image type:
  // 1. Supabase URL (full https:// URL from Supabase Storage)
  // 2. Local asset (starts with /assets/)
  // 3. Local cached filename (hash.jpg format)
  // 4. LinkedIn URL (for proxy fallback)
  const isSupabaseUrl = profileImage && String(profileImage).startsWith('https://') &&
                        String(profileImage).includes('supabase');
  const isLocalAsset = profileImage && String(profileImage).startsWith('/assets/');
  const isLocalCachedFile = profileImage && String(profileImage).trim() &&
                            !String(profileImage).startsWith('http') &&
                            !String(profileImage).startsWith('/assets/') &&
                            profileImage !== 'nan' && profileImage !== 'null';
  const isLinkedInUrl = !isSupabaseUrl && !isLocalAsset && !isLocalCachedFile && linkedinImage &&
                        String(linkedinImage).startsWith('http') &&
                        linkedinImage !== 'nan' && linkedinImage !== 'null';

  // Build image HTML
  let imageHTML;
  if (isSupabaseUrl) {
    // Supabase Storage URL - use directly
    imageHTML = `<img src="${profileImage}" alt="${alumni.name}" class="card-image" onerror="this.onerror=null; this.style.display='none'; var fallback=document.createElement('div'); fallback.className='card-image-fallback'; fallback.innerHTML='<img src=\\'${fallbackLogo}\\' alt=\\'PurdueTHINK Logo\\' />'; this.parentElement.insertBefore(fallback, this);">`;
  } else if (isLocalAsset) {
    const localPath = profileImage.substring(1); // Remove leading slash
    imageHTML = `<img src="${localPath}" alt="${alumni.name}" class="card-image" onerror="this.onerror=null; this.style.display='none'; var fallback=document.createElement('div'); fallback.className='card-image-fallback'; fallback.innerHTML='<img src=\\'${fallbackLogo}\\' alt=\\'PurdueTHINK Logo\\' />'; this.parentElement.insertBefore(fallback, this);">`;
  } else if (isLocalCachedFile) {
    // Legacy local cache - use cached-image endpoint
    const cachedImageUrl = `${API_BASE_URL}/cached-image/${profileImage}`;
    imageHTML = `<img src="${cachedImageUrl}" alt="${alumni.name}" class="card-image" onerror="this.onerror=null; this.style.display='none'; var fallback=document.createElement('div'); fallback.className='card-image-fallback'; fallback.innerHTML='<img src=\\'${fallbackLogo}\\' alt=\\'PurdueTHINK Logo\\' />'; this.parentElement.insertBefore(fallback, this);">`;
  } else if (isLinkedInUrl) {
    const proxiedImage = `${API_BASE_URL}/proxy-image?url=${encodeURIComponent(linkedinImage)}`;
    imageHTML = `<img src="${proxiedImage}" alt="${alumni.name}" class="card-image" onerror="this.onerror=null; this.style.display='none'; var fallback=document.createElement('div'); fallback.className='card-image-fallback'; fallback.innerHTML='<img src=\\'${fallbackLogo}\\' alt=\\'PurdueTHINK Logo\\' />'; this.parentElement.insertBefore(fallback, this);">`;
  } else {
    imageHTML = `<div class="card-image-fallback"><img src="${fallbackLogo}" alt="PurdueTHINK Logo" /></div>`;
  }

  // Build company display
  let companyDisplay = alumni.company || 'N/A';
  if (alumni.companies_list && alumni.companies_list.length > 1) {
    companyDisplay = alumni.companies_list.join(' • ');
  } else if (alumni.companies_list && alumni.companies_list.length === 1) {
    companyDisplay = alumni.companies_list[0];
  }

  // Build simple info text
  const infoItems = [];
  if (alumni.major) infoItems.push(alumni.major);
  if (alumni.grad_year) infoItems.push(`Class of ${alumni.grad_year}`);
  if (alumni.location) infoItems.push(alumni.location);
  const infoText = infoItems.join(' • ');

  // Build contact icons - check multiple possible fields
  // Helper to safely get string value
  const safeString = (val) => {
    if (val === null || val === undefined) return '';
    const str = String(val);
    if (str === 'nan' || str === 'null' || str === 'None' || str === 'none' || str.trim() === '') return '';
    return str;
  };

  const linkedinUrl = safeString(alumni.linkedin) || safeString(alumni.Linkedin) || safeString(alumni.linkedinProfileUrl);
  const emailAddress = safeString(alumni.professional_email) || safeString(alumni.professionalEmail) || safeString(alumni.email) || safeString(alumni['Personal Gmail']);

  const hasLinkedin = linkedinUrl !== '';
  const hasEmail = emailAddress !== '';


  let contactIconsHTML = '';
  if (hasLinkedin || hasEmail) {
    contactIconsHTML = '<div class="card-contact-icons">';
    if (hasLinkedin) {
      contactIconsHTML += `
        <a href="${linkedinUrl}" target="_blank" rel="noopener noreferrer" class="contact-icon linkedin-icon" title="LinkedIn Profile" onclick="event.stopPropagation()">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
          </svg>
        </a>
      `;
    }
    if (hasEmail) {
      contactIconsHTML += `
        <a href="mailto:${emailAddress}" class="contact-icon email-icon" title="Email" onclick="event.stopPropagation()">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
            <polyline points="22,6 12,13 2,6"></polyline>
          </svg>
        </a>
      `;
    }
    contactIconsHTML += '</div>';
  }

  return `
    <div class="alumni-card">
      <div class="card-image-section">
        ${imageHTML}
        ${contactIconsHTML}
      </div>
      <div class="card-body">
        <h3 class="card-name">${alumni.name}</h3>
        <p class="card-role">${alumni.role_title || alumni.headline || 'N/A'}</p>
        <p class="card-company">${companyDisplay}</p>
        ${infoText ? `<p class="card-info">${infoText}</p>` : ''}
      </div>
    </div>
  `;
}

// Get initials from name
function getInitials(name) {
  if (!name) return '?';
  const parts = name.split(' ').filter(p => p);
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase();
  }
  return parts[0][0].toUpperCase();
}

// Get selected options from multi-select
function getSelectedOptions(selectElement) {
  if (!selectElement) return [];
  return Array.from(selectElement.selectedOptions).map(option => option.value);
}

// Reset all filters
function resetFilters() {
  searchNameInput.value = '';
  searchTitleInput.value = '';
  filterMajorSelect.selectedIndex = -1;
  filterYearSelect.selectedIndex = -1;
  filterCompanySelect.selectedIndex = -1;
  filterIndustrySelect.selectedIndex = -1;
  sortBySelect.value = 'name';
  sortAscendingCheckbox.checked = true;

  applyFilters();
}

// Show/hide loading spinner
function showLoading(show) {
  if (loadingSpinner) {
    loadingSpinner.style.display = show ? 'flex' : 'none';
  }
  if (alumniGrid) {
    alumniGrid.style.display = show ? 'none' : 'grid';
  }
}

// Show error message
function showError(message) {
  if (alumniGrid) {
    alumniGrid.innerHTML = `
      <div style="text-align: center; padding: 40px; color: rgba(255, 255, 255, 0.72);">
        <p>${message}</p>
      </div>
    `;
  }
}

// Debounce utility
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}
