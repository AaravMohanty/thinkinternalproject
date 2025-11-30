/*
 * PurdueTHINK Main JavaScript
 * Common functionality across all pages
 */

// Mobile Menu Toggle
document.addEventListener('DOMContentLoaded', () => {
  const mobileMenuToggle = document.getElementById('mobileMenuToggle');
  const mobileMenu = document.getElementById('mobileMenu');

  if (mobileMenuToggle && mobileMenu) {
    mobileMenuToggle.addEventListener('click', () => {
      mobileMenu.classList.toggle('active');

      // Update button text
      const isActive = mobileMenu.classList.contains('active');
      mobileMenuToggle.textContent = isActive ? '✕' : '☰';
    });

    // Close mobile menu when clicking outside
    document.addEventListener('click', (e) => {
      if (!mobileMenu.contains(e.target) && !mobileMenuToggle.contains(e.target)) {
        mobileMenu.classList.remove('active');
        mobileMenuToggle.textContent = '☰';
      }
    });

    // Close mobile menu when clicking a link
    const mobileNavLinks = mobileMenu.querySelectorAll('.mobile-nav-link');
    mobileNavLinks.forEach(link => {
      link.addEventListener('click', () => {
        mobileMenu.classList.remove('active');
        mobileMenuToggle.textContent = '☰';
      });
    });
  }

  // Accordion functionality
  const accordionHeaders = document.querySelectorAll('.accordion-header');
  accordionHeaders.forEach(header => {
    header.addEventListener('click', () => {
      const item = header.closest('.accordion-item');
      const wasActive = item.classList.contains('active');

      // Close all accordion items
      document.querySelectorAll('.accordion-item').forEach(accordionItem => {
        accordionItem.classList.remove('active');
      });

      // Open clicked item if it wasn't active
      if (!wasActive) {
        item.classList.add('active');
      }
    });
  });

  // Smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const href = this.getAttribute('href');
      if (href === '#') return;

      e.preventDefault();
      const target = document.querySelector(href);
      if (target) {
        const headerOffset = 92; // Header height + spacing
        const elementPosition = target.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth'
        });
      }
    });
  });

  // Add scroll-based header shadow
  const header = document.querySelector('.app-header');
  if (header) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 0) {
        header.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.3)';
      } else {
        header.style.boxShadow = 'none';
      }
    });
  }
});
