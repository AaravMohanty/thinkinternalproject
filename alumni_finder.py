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
/* Page polish */
.block-container { padding-top: 2rem; padding-bottom: 2rem; }

/* Card grid */
.card-grid {
  display: grid;
  grid-template-columns: repeat(1, minmax(0, 1fr));
  gap: 16px;
}
@media (min-width: 720px) {
  .card-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (min-width: 1100px) {
  .card-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}

/* Card */
.card {
  border: 1px solid #d1d5db;
  border-radius: 12px;
  padding: 20px;
  background: #ffffff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: transform .15s ease, box-shadow .15s ease;
}
.card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.12);
  border-color: #9ca3af;
}
.card-header {
  display: flex; align-items: center; gap: 14px; margin-bottom: 12px;
}
.avatar {
  width: 48px; height: 48px; border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8); 
  color: #ffffff; 
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; letter-spacing: 0.5px; font-size: 16px;
}
.name { 
  font-size: 20px; 
  font-weight: 700; 
  margin: 0; 
  color: #111827;
  line-height: 1.2;
}
.role { 
  margin: 0; 
  color: #4b5563; 
  font-size: 15px;
  font-weight: 500;
}
.meta {
  display: flex; gap: 8px; flex-wrap: wrap; margin: 12px 0 8px 0; 
  color: #6b7280; font-size: 13px;
}
.meta .pill {
  border: 1px solid #d1d5db; 
  padding: 4px 12px; 
  border-radius: 20px; 
  background: #f9fafb;
  color: #374151;
  font-weight: 500;
}
.links {
  display: flex; gap: 16px; flex-wrap: wrap; margin-top: 12px; 
  font-size: 14px;
}
.links a { 
  text-decoration: none; 
  color: #3b82f6;
  font-weight: 500;
  padding: 6px 12px;
  border-radius: 6px;
  background: #eff6ff;
  border: 1px solid #dbeafe;
  transition: all 0.2s ease;
}
.links a:hover { 
  background: #dbeafe;
  color: #1d4ed8;
  text-decoration: none;
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
        links.append(f'📞 {phone}')

    return f"""
    <div class="card">
      <div class="card-header">
        <div class="avatar">{initials}</div>
        <div>
          <p class="name">{row['name']}</p>
          <p class="role"><strong>{role}</strong> @ {company}</p>
        </div>
      </div>
      <div class="meta">
        <span class="pill">Major: {major}</span>
        <span class="pill">Grad Year: {gy}</span>
      </div>
      <div class="links">{'&nbsp;&nbsp;•&nbsp;&nbsp;'.join(links)}</div>
    </div>
    """


def filter_controls(df: pd.DataFrame) -> Tuple[str, List[str], List[str], List[str]]:
    with st.sidebar:
        st.title("🔎 Filters")
        st.caption("Use any combination. Leave blank to show all.")
        q_title = st.text_input("Job title contains", placeholder="e.g., software, analyst")
        majors = sorted([m for m in df["major"].unique() if m])
        sel_majors = st.multiselect("Major", majors)

        years = sorted({str(y) for y in df["grad_year"].tolist() if str(y).strip()})
        sel_years = st.multiselect("Graduation year", years)

        companies = sorted([c for c in df["company"].unique() if c])
        sel_companies = st.multiselect("Companies worked at", companies)

        st.markdown("---")
        st.caption("Sorting")
        sort_field_map = {
            "Name": "name",
            "Company": "company",
            "Job Title": "role_title",
            "Graduation Year": "grad_year_int",  # numeric sort
            "Major": "major",
        }
        sort_by_label = st.selectbox("Sort by", list(sort_field_map.keys()), index=0)
        ascending = st.toggle("Ascending", value=True)
        # Store chosen mapping for main page to use
        st.session_state["_sort_col"] = sort_field_map[sort_by_label]
        st.session_state["_sort_asc"] = ascending

        st.markdown("---")
        if st.button("Reset filters"):
            st.experimental_rerun()

    return q_title, sel_majors, sel_years, sel_companies


def row_matches(row: pd.Series, q_title: str, sel_majors: List[str], sel_years: List[str], sel_companies: List[str]) -> bool:
    ok_title = True
    if q_title.strip():
        ok_title = q_title.lower() in row.get("role_title", "").lower()
    ok_major = (not sel_majors) or (row.get("major", "") in set(sel_majors))
    ok_year = (not sel_years) or (str(row.get("grad_year", "")) in set(sel_years))
    ok_company = (not sel_companies) or (row.get("company", "") in set(sel_companies))
    return ok_title and ok_major and ok_year and ok_company


# ----------------------------
# App
# ----------------------------
def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🤝", layout="wide")
    st.title(APP_TITLE)
    st.caption("Filter alumni by job title, major, graduation year, and companies worked at.")
    st.markdown(CARD_CSS, unsafe_allow_html=True)

    df = load_alumni()
    q_title, sel_majors, sel_years, sel_companies = filter_controls(df)

    filtered = df[df.apply(lambda r: row_matches(r, q_title, sel_majors, sel_years, sel_companies), axis=1)].copy()

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
