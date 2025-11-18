# PurdueTHINK Alumni Finder - Setup Guide

Complete setup guide for the PurdueTHINK Alumni Finder web application.

## Project Overview

A modern web application for finding and connecting with PurdueTHINK alumni. Features include:
- Beautiful, responsive design based on PurdueTHINK brand guidelines
- Advanced filtering by name, job title, major, graduation year, company, and industry
- Real-time search and results
- Mobile-friendly interface
- Google Drive data integration

## Architecture

```
┌─────────────────┐
│   Frontend      │  HTML/CSS/JavaScript
│  (Port 8000)    │  - Home page
│                 │  - Alumni finder page
└────────┬────────┘
         │
         │ REST API
         │
┌────────▼────────┐
│   Backend       │  Flask API
│  (Port 5000)    │  - Alumni data endpoint
│                 │  - Filter options endpoint
└────────┬────────┘
         │
         ├── Google Drive CSV (primary)
         ├── Local CSV (fallback)
         └── Seed data (fallback)
```

## Prerequisites

- Python 3.8 or higher
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection (for Google Drive integration)

## Quick Start

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
python app.py
```

The backend should now be running at `http://localhost:5000`

### 2. Frontend Setup

```bash
# Open a new terminal
# Navigate to frontend directory
cd frontend

# Serve the frontend (choose one method):

# Method 1: Python's built-in server
python -m http.server 8000

# Method 2: Node.js http-server
npx http-server -p 8000

# Method 3: Use VS Code Live Server extension
# Right-click index.html -> Open with Live Server
```

The frontend should now be accessible at `http://localhost:8000`

### 3. Access the Application

Open your browser and navigate to:
- **Home page**: `http://localhost:8000/index.html`
- **Alumni finder**: `http://localhost:8000/people.html`

## Configuration

### Google Drive Integration

To connect your own alumni data from Google Drive:

1. **Prepare your CSV file** with these columns:
   - `Name`: Full name
   - `Personal Gmail`: Email address
   - `Grad Yr`: Graduation year
   - `Major`: College major
   - `Linkedin` or `linkedinProfileUrl`: LinkedIn URL
   - `linkedinJobTitle` or `linkedinHeadline`: Job title
   - `companyName`: Current company
   - Additional optional fields: `previousCompanyName`, `companyIndustry`, `location`, `professionalEmail`, `linkedinProfileImageUrl`

2. **Upload to Google Drive**:
   - Upload your CSV to Google Drive
   - Right-click the file → Share
   - Change access to "Anyone with the link can view"
   - Copy the share link

3. **Get the File ID**:
   - From share link: `https://drive.google.com/file/d/FILE_ID_HERE/view`
   - Copy the `FILE_ID_HERE` portion

4. **Update backend configuration**:
   - Open `backend/app.py`
   - Find the line: `GOOGLE_DRIVE_FILE_ID = "1-ZPmzBu6xat2qQxOti2vg7ricaAlzkn_"`
   - Replace with your file ID: `GOOGLE_DRIVE_FILE_ID = "your-file-id"`
   - Restart the backend server

### Using Local CSV

If you prefer to use a local CSV file:

1. Place your CSV file at: `data/alumni.csv`
2. The backend will automatically use it if Google Drive is unavailable
3. No code changes needed

## Project Structure

```
THINKInternalProject/
├── backend/
│   ├── app.py              # Flask API server
│   ├── requirements.txt    # Python dependencies
│   └── README.md          # Backend documentation
├── frontend/
│   ├── index.html         # Home page
│   ├── people.html        # Alumni finder page
│   ├── styles/
│   │   ├── global.css     # Design system & global styles
│   │   ├── home.css       # Home page styles
│   │   └── people.css     # Alumni finder styles
│   ├── scripts/
│   │   ├── main.js        # Common functionality
│   │   └── alumni.js      # Alumni finder logic
│   └── README.md          # Frontend documentation
├── data/
│   └── alumni.csv         # Local alumni data (optional)
├── assets/
│   └── *.png              # Logo and image assets
├── SETUP.md               # This file
└── DESCRIPTION.md         # Design specifications
```

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'flask'`
- **Solution**: Make sure you activated the virtual environment and installed dependencies:
  ```bash
  source venv/bin/activate  # or venv\Scripts\activate on Windows
  pip install -r requirements.txt
  ```

**Problem**: Backend can't connect to Google Drive
- **Solution**:
  - Check your internet connection
  - Verify the file ID is correct
  - Make sure the Google Drive file is shared publicly
  - Check the backend logs for specific error messages

**Problem**: CORS errors in browser console
- **Solution**: Make sure the backend is running and CORS is enabled (it is by default in `app.py`)

### Frontend Issues

**Problem**: Alumni data not loading
- **Solution**:
  - Verify backend is running (`http://localhost:5000/api/health` should return `{"status": "healthy"}`)
  - Check browser console for errors
  - Verify API URL in `frontend/scripts/alumni.js` matches your backend URL

**Problem**: Images/logos not showing
- **Solution**: Check that logo files are in the correct location relative to HTML files

**Problem**: Mobile menu not working
- **Solution**:
  - Check browser console for JavaScript errors
  - Ensure `scripts/main.js` is loading properly
  - Try hard refresh (Ctrl+Shift+R or Cmd+Shift+R)

## Development

### Making Changes

**Frontend changes**:
- Edit HTML, CSS, or JS files
- Refresh browser to see changes
- No build step required

**Backend changes**:
- Edit `app.py`
- Restart the Flask server (Ctrl+C then `python app.py`)
- Changes will be reflected immediately

### Adding New Features

1. **New filter**:
   - Add filter UI in `people.html`
   - Add filter logic in `scripts/alumni.js`
   - Update backend if needed

2. **New page**:
   - Create new HTML file in `frontend/`
   - Create corresponding CSS in `frontend/styles/`
   - Add navigation link in header

## Deployment

### Production Checklist

**Backend**:
- [ ] Set `debug=False` in `app.py`
- [ ] Use production WSGI server (Gunicorn)
- [ ] Configure environment variables
- [ ] Set up proper CORS for your domain
- [ ] Use HTTPS

**Frontend**:
- [ ] Update API URL to production backend
- [ ] Minify CSS and JavaScript
- [ ] Optimize images
- [ ] Add proper meta tags for SEO
- [ ] Test on multiple devices and browsers

### Hosting Options

**Backend**:
- Heroku
- DigitalOcean App Platform
- AWS Elastic Beanstalk
- Google Cloud Run
- Railway

**Frontend**:
- Netlify
- Vercel
- GitHub Pages
- Cloudflare Pages
- AWS S3 + CloudFront

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review backend logs in terminal
3. Check browser console for errors
4. Refer to individual README files in `backend/` and `frontend/`

## License

© PurdueTHINK 2025
