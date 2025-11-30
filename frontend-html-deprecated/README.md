# PurdueTHINK Alumni Finder - Frontend

Modern, responsive frontend for the PurdueTHINK Alumni Finder application built with HTML, CSS, and JavaScript.

## Features

- **Responsive Design**: Mobile-first design that works on all devices
- **Alumni Search**: Search and filter alumni by name, job title, major, graduation year, company, and industry
- **Real-time Filtering**: Instant results as you type and select filters
- **Modern UI**: Dark theme with gradient cards and smooth animations
- **Accessible**: WCAG AA compliant with proper focus states and keyboard navigation

## Tech Stack

- HTML5
- CSS3 (Custom Properties, Grid, Flexbox)
- Vanilla JavaScript (ES6+)
- Poppins Font (Google Fonts)

## Design System

The frontend follows the PurdueTHINK design specification:

### Colors
- Primary Blue: `#17D4D4`
- Black: `#000000`
- White: `#FFFFFF`
- Text with opacity for hierarchy

### Typography
- Font Family: Poppins (Regular, Medium, SemiBold, Bold, Black)
- Responsive font sizing using `clamp()`

### Components
- 16px border radius for buttons and cards
- Consistent spacing using CSS variables
- Standard shadow: `0 6px 16px rgba(0, 0, 0, 0.18)`

## Project Structure

```
frontend/
├── index.html          # Home page
├── people.html         # Alumni finder page
├── styles/
│   ├── global.css     # Global styles and design system
│   ├── home.css       # Home page specific styles
│   └── people.css     # Alumni finder specific styles
├── scripts/
│   ├── main.js        # Common functionality (menu, accordion)
│   └── alumni.js      # Alumni finder logic
└── README.md          # This file
```

## Running Locally

1. **Start the backend server** (see backend README)

2. **Serve the frontend**:
   - Option 1: Use Python's built-in server:
     ```bash
     cd frontend
     python -m http.server 8000
     ```
   - Option 2: Use Node.js `http-server`:
     ```bash
     cd frontend
     npx http-server -p 8000
     ```
   - Option 3: Use VS Code Live Server extension

3. **Open in browser**:
   ```
   http://localhost:8000
   ```

## API Configuration

The frontend expects the backend API to be running at `http://localhost:5001`. To change this:

1. Open `frontend/scripts/alumni.js`
2. Update the `API_BASE_URL` constant:
   ```javascript
   const API_BASE_URL = 'http://your-backend-url:port/api';
   ```

## Pages

### Home Page (`index.html`)
- Hero section with PurdueTHINK branding
- "Who We Are" section with team image
- Mission & Values with accordion
- Learn More section
- Footer with social links

### People Page (`people.html`)
- Alumni search and filter interface
- Dynamic alumni cards grid
- Multi-select filters for:
  - Major
  - Graduation Year
  - Company
  - Industry
- Search by name or job title
- Sorting options
- Mobile-friendly filters sidebar

## Browser Support

- Chrome (last 2 versions)
- Firefox (last 2 versions)
- Safari (last 2 versions)
- Edge (last 2 versions)

## Customization

### Changing Colors

Edit CSS variables in `styles/global.css`:

```css
:root {
  --color-primary: #17D4D4;
  --color-black: #000000;
  --color-white: #FFFFFF;
  /* ... */
}
```

### Updating Content

- Home page content: Edit `index.html`
- Alumni finder: Data comes from backend API
- Footer links: Edit footer section in both HTML files

## Performance

- CSS and JS files are separated for better caching
- Images should be optimized before deployment
- Consider using a CDN for production

## Accessibility

- Semantic HTML5 elements
- ARIA labels for icon buttons
- Focus visible states for keyboard navigation
- Color contrast meets WCAG AA standards

## Deployment

For production deployment:

1. **Update API URL** in `scripts/alumni.js`
2. **Optimize assets**:
   - Minify CSS and JS
   - Compress images
   - Use appropriate image formats (WebP)
3. **Add meta tags** for SEO
4. **Configure CORS** on backend for your domain

## License

© PurdueTHINK 2025
