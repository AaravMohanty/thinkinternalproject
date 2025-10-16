"""
PurdueTHINK — Alumni Finder (Streamlit, simple & polished UI)
-------------------------------------------------------------
Run:
    pip install streamlit pandas
    streamlit run app.py

- Single-file demo that reads from ./data/alumni.csv
- No auth. Sidebar filters + card grid results.
- Replace the CSV with your real alumni data later.
"""

from __future__ import annotations
import os
from typing import List, Tuple

import pandas as pd
import streamlit as st

APP_TITLE = "PurdueTHINK — Alumni Finder"
DATA_DIR = "data"
ALUMNI_CSV = os.path.join(DATA_DIR, "alumni.csv")

# ----------------------------
# Seed data (no personal info)
# ----------------------------
SEED = [
    {
        "name": "Jordan Kim",
        "role_title": "Software Engineer",
        "company": "Stripe",
        "major": "Computer Science",
        "grad_year": "2024",
        "linkedin": "https://www.linkedin.com/in/jordan-kim",
        "email": "jordan.kim@example.com",
        "phone": "(555) 201-0001",
    },
    {
        "name": "Priya Shah",
        "role_title": "Data Scientist",
        "company": "Capital One",
        "major": "Data Science",
        "grad_year": "2023",
        "linkedin": "https://www.linkedin.com/in/priya-shah",
        "email": "priya.shah@example.com",
        "phone": "(555) 201-0002",
    },
    {
        "name": "Miguel Torres",
        "role_title": "Product Manager",
        "company": "Amazon",
        "major": "Industrial Engineering",
        "grad_year": "2022",
        "linkedin": "https://www.linkedin.com/in/miguel-torres",
        "email": "miguel.torres@example.com",
        "phone": "(555) 201-0003",
    },
    {
        "name": "Emily Zhao",
        "role_title": "Quant Research Analyst",
        "company": "Two Sigma",
        "major": "Mathematics",
        "grad_year": "2021",
        "linkedin": "https://www.linkedin.com/in/emily-zhao",
        "email": "emily.zhao@example.com",
        "phone": "(555) 201-0004",
    },
    {
        "name": "Noah Williams",
        "role_title": "Security Engineer",
        "company": "Cloudflare",
        "major": "Computer Engineering",
        "grad_year": "2020",
        "linkedin": "https://www.linkedin.com/in/noah-williams",
        "email": "noah.williams@example.com",
        "phone": "(555) 201-0005",
    },
    {
        "name": "Sofia Rossi",
        "role_title": "UX Designer",
        "company": "Airbnb",
        "major": "User Experience Design",
        "grad_year": "2024",
        "linkedin": "https://www.linkedin.com/in/sofia-rossi",
        "email": "sofia.rossi@example.com",
        "phone": "(555) 201-0006",
    },
    {
        "name": "Thomas Nguyen",
        "role_title": "Machine Learning Engineer",
        "company": "NVIDIA",
        "major": "Computer Science",
        "grad_year": "2025",
        "linkedin": "https://www.linkedin.com/in/thomas-nguyen",
        "email": "thomas.nguyen@example.com",
        "phone": "(555) 201-0007",
    },
]


# ----------------------------
# Data IO
# ----------------------------
def ensure_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(ALUMNI_CSV):
        pd.DataFrame(SEED).to_csv(ALUMNI_CSV, index=False)


@st.cache_data(show_spinner=False)
def load_alumni() -> pd.DataFrame:
    ensure_data()
    df = pd.read_csv(ALUMNI_CSV)
    cols = ["name", "role_title", "company", "major", "grad_year", "linkedin", "email", "phone"]
    for c in cols:
        if c not in df.columns:
            df[c] = ""
        df[c] = df[c].fillna("").astype(str)
    # Add a normalized grad year for numeric sorting
    def to_int_safe(x):
        try:
            return int(x)
        except Exception:
            return None
    df["grad_year_int"] = df["grad_year"].apply(to_int_safe)
    return df


def mailto(email: str) -> str:
    return f"mailto:{email}" if email else "#"


# ----------------------------
# UI helpers / styling
# ----------------------------
CARD_CSS = """
<style>
/* Modern Sleek Theme */
:root {
  --primary: #6366f1;
  --primary-dark: #4f46e5;
  --secondary: #8b5cf6;
  --accent: #06b6d4;
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
  --dark: #1f2937;
  --light: #f8fafc;
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-300: #d1d5db;
  --gray-400: #9ca3af;
  --gray-500: #6b7280;
  --gray-600: #4b5563;
  --gray-700: #374151;
  --gray-800: #1f2937;
  --gray-900: #111827;
}

/* Global styles */
* {
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

/* Page layout */
.block-container { 
  padding: 0;
  background: transparent;
  max-width: 1600px;
  margin: 0 auto;
}

/* Header styling */
h1 {
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 800;
  font-size: 3rem;
  margin-bottom: 0.5rem;
  text-align: center;
  text-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.caption {
  color: rgba(255,255,255,0.9) !important;
  font-size: 1.2rem;
  margin-bottom: 2rem;
  text-align: center;
  font-weight: 500;
}

/* Results counter */
.stMarkdown p {
  color: #ffffff !important;
  font-weight: 600;
  font-size: 1.1rem;
  margin-bottom: 2rem;
  padding: 1rem 1.5rem;
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.2);
  text-align: center;
}

/* Card grid - modern layout */
.card-grid {
  display: grid;
  grid-template-columns: repeat(1, minmax(0, 1fr));
  gap: 2rem;
  margin-top: 2rem;
  padding: 0 1rem;
}

@media (min-width: 768px) {
  .card-grid { 
    grid-template-columns: repeat(2, minmax(0, 1fr)); 
    gap: 2rem;
  }
}

@media (min-width: 1200px) {
  .card-grid { 
    grid-template-columns: repeat(3, minmax(0, 1fr)); 
    gap: 2rem;
  }
}

/* Modern card design */
.card {
  border: none;
  border-radius: 20px;
  padding: 2rem;
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(20px);
  box-shadow: 
    0 20px 25px -5px rgba(0,0,0,0.1),
    0 10px 10px -5px rgba(0,0,0,0.04),
    0 0 0 1px rgba(255,255,255,0.05);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
  border-radius: 20px 20px 0 0;
}

.card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 
    0 32px 64px -12px rgba(0,0,0,0.25),
    0 0 0 1px rgba(255,255,255,0.1);
}

.card-header {
  display: flex; 
  align-items: center; 
  gap: 1.5rem; 
  margin-bottom: 1.5rem;
}

.avatar {
  width: 64px; 
  height: 64px; 
  border-radius: 16px;
  background: linear-gradient(135deg, #667eea, #764ba2); 
  color: #ffffff; 
  display: flex; 
  align-items: center; 
  justify-content: center;
  font-weight: 700; 
  font-size: 20px;
  flex-shrink: 0;
  box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
  border: 3px solid rgba(255,255,255,0.2);
}

.name { 
  font-size: 1.5rem; 
  font-weight: 700; 
  margin: 0; 
  color: var(--gray-900);
  line-height: 1.2;
}

.role { 
  margin: 0.5rem 0 0 0; 
  color: var(--gray-600); 
  font-size: 1rem;
  font-weight: 600;
}

.company {
  margin: 0.25rem 0 0 0; 
  color: var(--primary); 
  font-size: 0.95rem;
  font-weight: 600;
}

.meta {
  display: flex; 
  gap: 0.75rem; 
  flex-wrap: wrap; 
  margin: 1.5rem 0; 
}

.meta .pill {
  border: none; 
  padding: 0.5rem 1rem; 
  border-radius: 50px; 
  font-weight: 600;
  font-size: 0.85rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s ease;
}

.meta .pill.major {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: #ffffff;
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
}

.meta .pill.year {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  color: #ffffff;
  box-shadow: 0 4px 8px rgba(139, 92, 246, 0.3);
}

.meta .pill:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0,0,0,0.15);
}

.links {
  display: flex; 
  gap: 1rem; 
  flex-wrap: wrap; 
  margin-top: 1.5rem;
}

.links a { 
  text-decoration: none; 
  color: #ffffff;
  font-weight: 600;
  padding: 0.75rem 1.25rem;
  border-radius: 50px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
}

.links a:hover { 
  background: linear-gradient(135deg, #764ba2, #667eea);
  transform: translateY(-3px);
  box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
  text-decoration: none;
  color: #ffffff;
}

.links .phone {
  color: var(--gray-600);
  font-weight: 600;
  padding: 0.75rem 1.25rem;
  background: var(--gray-100);
  border-radius: 50px;
  font-size: 0.9rem;
  border: 1px solid var(--gray-200);
}

/* Sidebar styling */
.sidebar {
  background: rgba(255,255,255,0.1) !important;
  backdrop-filter: blur(20px) !important;
  border-radius: 20px !important;
  margin: 1rem !important;
  padding: 1.5rem !important;
}

.sidebar h1, .sidebar h2, .sidebar h3 {
  color: #ffffff !important;
}

.sidebar .stTextInput > div > div > input {
  background: rgba(255,255,255,0.9) !important;
  border: 1px solid rgba(255,255,255,0.2) !important;
  border-radius: 12px !important;
  padding: 0.75rem 1rem !important;
  font-weight: 500 !important;
}

.sidebar .stSelectbox > div > div > select {
  background: rgba(255,255,255,0.9) !important;
  border: 1px solid rgba(255,255,255,0.2) !important;
  border-radius: 12px !important;
  padding: 0.75rem 1rem !important;
}

.sidebar .stMultiSelect > div > div {
  background: rgba(255,255,255,0.9) !important;
  border: 1px solid rgba(255,255,255,0.2) !important;
  border-radius: 12px !important;
}

.sidebar .stButton > button {
  background: linear-gradient(135deg, #667eea, #764ba2) !important;
  color: #ffffff !important;
  border: none !important;
  border-radius: 12px !important;
  font-weight: 600 !important;
  padding: 0.75rem 1.5rem !important;
  transition: all 0.3s ease !important;
}

.sidebar .stButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3) !important;
}

/* Download button styling */
.stDownloadButton > button {
  background: linear-gradient(135deg, #10b981, #059669) !important;
  color: #ffffff !important;
  border: none !important;
  border-radius: 12px !important;
  font-weight: 600 !important;
  padding: 0.75rem 1.5rem !important;
  transition: all 0.3s ease !important;
}

.stDownloadButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 16px rgba(16, 185, 129, 0.3) !important;
}

/* Info message styling */
.stAlert {
  border-radius: 12px !important;
  border: none !important;
  background: rgba(255,255,255,0.1) !important;
  backdrop-filter: blur(10px) !important;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(255,255,255,0.1);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.3);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(255,255,255,0.5);
}
</style>
"""


def render_card(row: pd.Series) -> str:
    initials = "".join([part[0].upper() for part in row["name"].split()[:2]]) or "A"
    company = row["company"] or "—"
    role = row["role_title"] or "—"
    major = row["major"] or "—"
    gy = row["grad_year"] or "—"
    linkedin = row["linkedin"]
    email = row["email"]
    phone = row["phone"]

    links = []
    if linkedin:
        links.append(f'<a href="{linkedin}" target="_blank">🔗 LinkedIn</a>')
    if email:
        links.append(f'<a href="{mailto(email)}">✉️ Email</a>')
    if phone:
        links.append(f'<span class="phone">📞 {phone}</span>')

    return f"""
    <div class="card">
      <div class="card-header">
        <div class="avatar">{initials}</div>
        <div>
          <p class="name">{row['name']}</p>
          <p class="role">{role}</p>
          <p class="company">{company}</p>
        </div>
      </div>
      <div class="meta">
        <span class="pill major">🎓 {major}</span>
        <span class="pill year">📅 {gy}</span>
      </div>
      <div class="links">{'&nbsp;&nbsp;•&nbsp;&nbsp;'.join(links)}</div>
    </div>
    """


def filter_controls(df: pd.DataFrame) -> Tuple[str, str, List[str], List[str], List[str]]:
    with st.sidebar:
        st.title("🔍 Smart Search")
        st.caption("Find exactly who you're looking for")
        
        # Name search with regex support
        q_name = st.text_input("👤 Search by name", placeholder="e.g., John Smith, ^A.*, .*Smith$", help="Supports regex patterns for advanced searching")
        
        # Job title search
        q_title = st.text_input("💼 Search by job title", placeholder="e.g., engineer, analyst, manager")
        
        majors = sorted([m for m in df["major"].unique() if m])
        sel_majors = st.multiselect("🎓 Filter by major", majors, help="Select one or more majors")

        years = sorted({str(y) for y in df["grad_year"].tolist() if str(y).strip()})
        sel_years = st.multiselect("📅 Filter by graduation year", years, help="Select one or more graduation years")

        companies = sorted([c for c in df["company"].unique() if c])
        sel_companies = st.multiselect("🏢 Filter by company", companies, help="Select one or more companies")

        st.markdown("---")
        st.subheader("⚡ Sort Results")
        sort_field_map = {
            "Name": "name",
            "Company": "company",
            "Job Title": "role_title",
            "Graduation Year": "grad_year_int",  # numeric sort
            "Major": "major",
        }
        sort_by_label = st.selectbox("Sort by", list(sort_field_map.keys()), index=0)
        ascending = st.toggle("Ascending order", value=True)
        # Store chosen mapping for main page to use
        st.session_state["_sort_col"] = sort_field_map[sort_by_label]
        st.session_state["_sort_asc"] = ascending

        st.markdown("---")
        if st.button("🔄 Clear all filters", type="secondary"):
            # Clear all session state related to filters
            for key in list(st.session_state.keys()):
                if key.startswith("_filter_"):
                    del st.session_state[key]
            st.rerun()

    return q_name, q_title, sel_majors, sel_years, sel_companies


def row_matches(row: pd.Series, q_name: str, q_title: str, sel_majors: List[str], sel_years: List[str], sel_companies: List[str]) -> bool:
    import re
    
    # Name search with regex support
    ok_name = True
    if q_name.strip():
        try:
            ok_name = bool(re.search(q_name, row.get("name", ""), re.IGNORECASE))
        except re.error:
            # If regex is invalid, fall back to simple string search
            ok_name = q_name.lower() in row.get("name", "").lower()
    
    # Job title search
    ok_title = True
    if q_title.strip():
        ok_title = q_title.lower() in row.get("role_title", "").lower()
    
    # Other filters
    ok_major = (not sel_majors) or (row.get("major", "") in set(sel_majors))
    ok_year = (not sel_years) or (str(row.get("grad_year", "")) in set(sel_years))
    ok_company = (not sel_companies) or (row.get("company", "") in set(sel_companies))
    
    return ok_name and ok_title and ok_major and ok_year and ok_company


# ----------------------------
# App
# ----------------------------
def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🚀", layout="wide")
    st.title(APP_TITLE)
    st.caption("Discover and connect with PurdueTHINK alumni. Find the perfect contact for your next project or collaboration.")
    st.markdown(CARD_CSS, unsafe_allow_html=True)

    df = load_alumni()
    q_name, q_title, sel_majors, sel_years, sel_companies = filter_controls(df)

    filtered = df[df.apply(lambda r: row_matches(r, q_name, q_title, sel_majors, sel_years, sel_companies), axis=1)].copy()

    # Sorting (handles string columns + numeric grad year via grad_year_int)
    sort_col = st.session_state.get("_sort_col", "name")
    sort_asc = st.session_state.get("_sort_asc", True)

    # If sorting by grad_year_int, None values should go last
    if sort_col == "grad_year_int":
        filtered["_sort_key"] = filtered["grad_year_int"].fillna(-10**9 if sort_asc else 10**9)
        filtered = filtered.sort_values(by="_sort_key", ascending=sort_asc, kind="mergesort").drop(columns=["_sort_key"])
    else:
        filtered = filtered.sort_values(by=sort_col, ascending=sort_asc, na_position="last", kind="mergesort")

    st.write(f"Showing **{len(filtered)}** of {len(df)} alumni")

    # Render as a responsive grid
    st.markdown('<div class="card-grid">', unsafe_allow_html=True)
    if filtered.empty:
        st.info("No results. Try clearing or loosening your filters.")
    else:
        html_cards = [render_card(row) for _, row in filtered.iterrows()]
        st.markdown("\n".join(html_cards), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.download_button(
        "Download current results (CSV)",
        filtered.drop(columns=["grad_year_int"]).to_csv(index=False).encode("utf-8"),
        file_name="alumni_results.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
