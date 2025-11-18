# PurdueTHINK Alumni Finder - Backend API

Flask REST API for serving PurdueTHINK alumni data with filtering and search capabilities.

## Features

- **REST API**: Clean API endpoints for alumni data
- **Google Drive Integration**: Loads alumni data from Google Drive CSV
- **Filtering**: Support for multiple filter criteria
- **CORS Enabled**: Works with frontend on different ports
- **Fallback Data**: Uses local CSV or seed data if Google Drive is unavailable

## Tech Stack

- Python 3.8+
- Flask 3.0.0
- Flask-CORS 4.0.0
- Pandas 2.1.4
- Requests 2.31.0

## Installation

1. **Create a virtual environment**:
   ```bash
   cd backend
   python -m venv venv
   ```

2. **Activate virtual environment**:
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - Windows:
     ```bash
     venv\Scripts\activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The backend can load alumni data from three sources (in order of priority):

1. **Google Drive** (primary)
2. **Local CSV file** (`../data/alumni.csv`)
3. **Seed data** (fallback)

### Google Drive Setup

1. Upload your alumni CSV to Google Drive
2. Share the file (Anyone with link can view)
3. Get the file ID from the share link:
   - Share link: `https://drive.google.com/file/d/FILE_ID_HERE/view`
   - File ID: `FILE_ID_HERE`
4. Update `GOOGLE_DRIVE_FILE_ID` in `app.py`:
   ```python
   GOOGLE_DRIVE_FILE_ID = "your-file-id-here"
   ```

### CSV Format

The backend supports two CSV formats:

#### LinkedIn-enriched format (recommended):
- `Name`: Full name
- `Personal Gmail`: Email address
- `Grad Yr`: Graduation year
- `Major`: College major
- `linkedinProfileUrl` or `Linkedin`: LinkedIn profile URL
- `linkedinJobTitle` or `linkedinHeadline`: Job title
- `companyName`: Current company
- `previousCompanyName`: Previous company (optional)
- `companyIndustry`: Industry
- `location` or `linkedinJobLocation`: Location
- `professionalEmail`: Work email (optional)
- `linkedinProfileImageUrl`: Profile image URL (optional)

#### Legacy format:
- `name`, `role_title`, `company`, `major`, `grad_year`, `linkedin`, `email`, `phone`

## Running the Server

1. **Start the Flask development server**:
   ```bash
   python app.py
   ```

2. **Server will run on**:
   ```
   http://localhost:5000
   ```

## API Endpoints

### GET `/api/health`
Health check endpoint.

**Response**:
```json
{
  "status": "healthy"
}
```

### GET `/api/alumni`
Get all alumni or filtered alumni.

**Query Parameters**:
- `name` (string): Filter by name (case-insensitive partial match)
- `title` (string): Filter by job title (case-insensitive partial match)
- `major` (string): Filter by major (exact match)
- `grad_year` (string): Filter by graduation year (exact match)
- `company` (string): Filter by company (checks all companies in history)
- `industry` (string): Filter by industry (exact match)

**Response**:
```json
{
  "success": true,
  "count": 10,
  "data": [
    {
      "name": "John Doe",
      "role_title": "Software Engineer",
      "company": "Google",
      "major": "Computer Science",
      "grad_year": "2024",
      "linkedin": "https://linkedin.com/in/johndoe",
      "email": "john@example.com",
      "companies_list": ["Google", "Microsoft"],
      "location": "San Francisco, CA",
      "company_industry": "Technology",
      ...
    }
  ]
}
```

### GET `/api/filters`
Get available filter options.

**Response**:
```json
{
  "success": true,
  "filters": {
    "majors": ["Computer Science", "Data Science", ...],
    "years": ["2020", "2021", "2022", ...],
    "companies": ["Google", "Microsoft", ...],
    "industries": ["Technology", "Finance", ...]
  }
}
```

## Data Processing

The backend automatically:
- Removes duplicate entries (based on name + email)
- Removes empty rows
- Normalizes data formats
- Builds company history lists
- Builds school history lists
- Handles missing values gracefully

## Error Handling

All endpoints return proper error responses:

```json
{
  "success": false,
  "error": "Error message here"
}
```

## Development

### Running in Debug Mode

Debug mode is enabled by default in `app.py`:

```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

### Testing the API

Use curl or a tool like Postman:

```bash
# Health check
curl http://localhost:5000/api/health

# Get all alumni
curl http://localhost:5000/api/alumni

# Filter by major
curl "http://localhost:5000/api/alumni?major=Computer%20Science"

# Filter by multiple criteria
curl "http://localhost:5000/api/alumni?major=Computer%20Science&grad_year=2024"

# Get filter options
curl http://localhost:5000/api/filters
```

## Production Deployment

For production:

1. **Disable debug mode**:
   ```python
   app.run(debug=False, host='0.0.0.0', port=5000)
   ```

2. **Use a production WSGI server** (e.g., Gunicorn):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. **Set up environment variables** for sensitive data:
   ```python
   import os
   GOOGLE_DRIVE_FILE_ID = os.getenv('GOOGLE_DRIVE_FILE_ID')
   ```

4. **Configure CORS** for your production domain:
   ```python
   CORS(app, origins=['https://yourdomain.com'])
   ```

## License

© PurdueTHINK 2025
