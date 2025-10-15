# PurdueTHINK Alumni Finder

A Streamlit application for managing and searching alumni networks with advanced filtering capabilities.

## 🚨 Security Notice

**IMPORTANT**: This repository contains template files only. **DO NOT** commit real personal data to GitHub.

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd THINKInternalProject
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your data files** (REQUIRED)
   - Copy `data/users_template.csv` to `data/users.csv` and add your user data
   - Copy `data/alumni_template.csv` to `data/alumni.csv` and add your alumni data  
   - Copy `data/coffee_requests_template.csv` to `data/coffee_requests.csv` if needed

4. **Run the application**
   ```bash
   streamlit run alumni_finder.py
   ```

### Data Privacy

- ✅ **DO**: Use the template files as starting points
- ✅ **DO**: Add your real data to the local CSV files
- ❌ **DON'T**: Commit real personal information to GitHub
- ❌ **DON'T**: Push sensitive data like emails, names, or contact info

The `.gitignore` file is configured to prevent accidental commits of sensitive data.

### Features

- Advanced filtering by name, job title, major, graduation year, and company
- Professional profile cards with contact information
- Export filtered results to CSV
- Responsive design with dark theme
- LinkedIn profile integration