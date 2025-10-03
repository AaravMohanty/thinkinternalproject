"""
PurdueTHINK — Internal Networking Tool (Streamlit)
--------------------------------------------------
Single-file demo app you can run with:
    streamlit run app.py

Notes
- This is a lightweight prototype that persists to local CSV files.
- Replace CSV with your org's DB (e.g., Supabase/Firestore) for production.
- Authentication here is minimal and for demo only.
"""

from __future__ import annotations
import os
import textwrap
from datetime import datetime
from typing import List, Optional

import pandas as pd
import streamlit as st

APP_TITLE = "PurdueTHINK — Internal Networking"
DATA_DIR = "data"
USERS_CSV = os.path.join(DATA_DIR, "users.csv")
REQUESTS_CSV = os.path.join(DATA_DIR, "coffee_requests.csv")

# ----------------------------
# Bootstrap / seed data
# ----------------------------
def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def seed_users_csv():
    if not os.path.exists(USERS_CSV):
        df = pd.DataFrame(
            [
                {
                    "email": "amohanty@purdue.edu",
                    "name": "Aarav Mohanty",
                    "year": "2027",
                    "major": "CS",
                    "skills": "Python, ML, Data Engineering, Streamlit",
                    "interests": "Quant, AI Agents, Consulting",
                    "projects": "BoilerQuant, Kihara Lab PPO, CMS Challenge",
                    "bio": "AI/ML + product-minded SWE, active in PurdueTHINK.",
                    "linkedin": "https://www.linkedin.com/in/aarav-mohanty",
                    "slack": "@aarav",
                    "calendly": "",
                    "seeking_roles": "SWE, Quant Dev",
                    "offering_help": "Interview prep, Python, ML",
                    "tags": "AI, Quant, Consulting",
                    "last_updated": datetime.now().isoformat(timespec="seconds"),
                },
                {
                    "email": "jane.doe@purdue.edu",
                    "name": "Jane Doe",
                    "year": "2026",
                    "major": "IE",
                    "skills": "Product, Excel, Python",
                    "interests": "Ops, PM, Analytics",
                    "projects": "THINK Pro Bono Ops Sprint",
                    "bio": "Process optimization nerd. Love coffee chats.",
                    "linkedin": "https://www.linkedin.com/in/janedoe",
                    "slack": "@jane",
                    "calendly": "https://calendly.com/jane-doe/coffee",
                    "seeking_roles": "Product Analyst, PM Intern",
                    "offering_help": "Resume review, case interviews",
                    "tags": "PM, Ops",
                    "last_updated": datetime.now().isoformat(timespec="seconds"),
                },
            ]
        )
        df.to_csv(USERS_CSV, index=False)


def seed_requests_csv():
    if not os.path.exists(REQUESTS_CSV):
        df = pd.DataFrame(
            columns=[
                "created_at",
                "from_email",
                "to_email",
                "message",
                "status",
            ]
        )
        df.to_csv(REQUESTS_CSV, index=False)


# ----------------------------
# Data Access
# ----------------------------
@st.cache_data(show_spinner=False)
def load_users() -> pd.DataFrame:
    ensure_data_dir()
    seed_users_csv()
    df = pd.read_csv(USERS_CSV)
    for col in [
        "skills",
        "interests",
        "projects",
        "tags",
        "seeking_roles",
        "offering_help",
    ]:
        df[col] = df[col].fillna("")
    return df


def save_users(df: pd.DataFrame) -> None:
    ensure_data_dir()
    df.to_csv(USERS_CSV, index=False)
    load_users.clear()  # invalidate cache


@st.cache_data(show_spinner=False)
def load_requests() -> pd.DataFrame:
    ensure_data_dir()
    seed_requests_csv()
    return pd.read_csv(REQUESTS_CSV)


def save_requests(df: pd.DataFrame) -> None:
    ensure_data_dir()
    df.to_csv(REQUESTS_CSV, index=False)
    load_requests.clear()


# ----------------------------
# Helpers
# ----------------------------
TAG_SEP = ","


def to_list(s: str) -> List[str]:
    if not isinstance(s, str) or not s.strip():
        return []
    return [x.strip() for x in s.split(TAG_SEP) if x.strip()]


def to_str(items: List[str]) -> str:
    return TAG_SEP.join(sorted({x.strip() for x in items if x.strip()}))


# ----------------------------
# Auth (demo only)
# ----------------------------
KEY_USER = "user_email"


def login_ui():
    st.header("Sign in")
    st.caption("Demo auth — just your Purdue email. Use the seeded users or add yourself.")
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Purdue email", placeholder="you@purdue.edu").strip().lower()
        submitted = st.form_submit_button("Enter")
    if submitted:
        if email and email.endswith("@purdue.edu"):
            st.session_state[KEY_USER] = email
            st.success("Signed in!")
            st.rerun()
        else:
            st.error("Please use a valid Purdue email.")


def current_user(df_users: pd.DataFrame) -> Optional[pd.Series]:
    email = st.session_state.get(KEY_USER)
    if not email:
        return None
    match = df_users[df_users["email"].str.lower() == email]
    if match.empty:
        # Create a skeleton profile
        blank = {
            "email": email,
            "name": "",
            "year": "",
            "major": "",
            "skills": "",
            "interests": "",
            "projects": "",
            "bio": "",
            "linkedin": "",
            "slack": "",
            "calendly": "",
            "seeking_roles": "",
            "offering_help": "",
            "tags": "",
            "last_updated": datetime.now().isoformat(timespec="seconds"),
        }
        df_users = pd.concat([df_users, pd.DataFrame([blank])], ignore_index=True)
        save_users(df_users)
        match = df_users[df_users["email"].str.lower() == email]
    return match.iloc[0]


# ----------------------------
# UI Components
# ----------------------------
CARD_CSS = """
<style>
.user-card {border: 1px solid #eee; padding: 1rem; border-radius: 14px; margin-bottom: 0.75rem;}
.user-card h4 {margin: 0 0 .25rem 0;}
.badge {display: inline-block; padding: 2px 8px; border-radius: 999px; border: 1px solid #ddd; margin-right: 6px; margin-bottom: 6px; font-size: 12px;}
.small-dim {color: #666; font-size: 12px;}
</style>
"""


def profile_card(row: pd.Series, enable_actions: bool = True):
    skills = to_list(row.skills)
    interests = to_list(row.interests)
    tags = to_list(row.tags)

    st.markdown(CARD_CSS, unsafe_allow_html=True)
    with st.container(border=False):
        st.markdown('<div class="user-card">', unsafe_allow_html=True)
        cols = st.columns([0.70, 0.30])
        with cols[0]:
            st.markdown(f"<h4>{row.get('name') or row.email}</h4>", unsafe_allow_html=True)
            st.caption(f"{row.major or '—'} · Class of {row.year or '—'}")
            if row.bio:
                st.write(row.bio)
            if skills:
                st.markdown("**Skills**: " + " ".join([f"<span class='badge'>{s}</span>" for s in skills]), unsafe_allow_html=True)
            if interests:
                st.markdown("**Interests**: " + " ".join([f"<span class='badge'>{s}</span>" for s in interests]), unsafe_allow_html=True)
            if row.projects:
                st.markdown(f"**Projects**: {row.projects}")
            if tags:
                st.markdown("**Tags**: " + " ".join([f"<span class='badge'>{t}</span>" for t in tags]), unsafe_allow_html=True)
            st.markdown(f"<span class='small-dim'>Last updated: {row.last_updated}</span>", unsafe_allow_html=True)
        with cols[1]:
            if row.linkedin:
                st.link_button("LinkedIn", row.linkedin)
            if row.slack:
                st.button(f"Slack: {row.slack}", disabled=True)
            if row.calendly:
                st.link_button("Book coffee", row.calendly)
            if enable_actions:
                st.session_state.setdefault("_coffee_msg", "Hey! Would love to connect and learn about your work at PurdueTHINK.")
                with st.popover("Request coffee chat"):
                    msg = st.text_area("Intro message", key=f"msg_{row.email}", value=st.session_state["_coffee_msg"], height=80)
                    if st.button("Send request", key=f"send_{row.email}"):
                        df_req = load_requests()
                        df_req.loc[len(df_req)] = {
                            "created_at": datetime.now().isoformat(timespec="seconds"),
                            "from_email": st.session_state.get(KEY_USER),
                            "to_email": row.email,
                            "message": msg,
                            "status": "pending",
                        }
                        save_requests(df_req)
                        st.success("Request logged! (Demo) — Receiver can see it in Coffee Chats.")
        st.markdown("</div>", unsafe_allow_html=True)


def directory_page(df_users: pd.DataFrame, me: Optional[pd.Series]):
    st.subheader("People Directory")
    st.caption("Filter by skills/interests/year/major to find collaborators and mentors.")

    # Filters
    cols = st.columns(4)
    with cols[0]:
        q = st.text_input("Search name/email/keywords")
    with cols[1]:
        years = sorted(df_users["year"].dropna().astype(str).unique().tolist())
        f_year = st.multiselect("Grad year", years)
    with cols[2]:
        majors = sorted(df_users["major"].dropna().astype(str).unique().tolist())
        f_major = st.multiselect("Major", majors)
    with cols[3]:
        f_tag = st.text_input("Filter tag (comma‑sep)")

    # Apply filters
    def matches(row: pd.Series) -> bool:
        hay = " ".join(
            [
                str(row.get("name", "")),
                str(row.get("email", "")),
                str(row.get("skills", "")),
                str(row.get("interests", "")),
                str(row.get("projects", "")),
                str(row.get("tags", "")),
            ]
        ).lower()
        ok_q = (not q) or (q.lower() in hay)
        ok_year = (not f_year) or (str(row.get("year")) in set(map(str, f_year)))
        ok_major = (not f_major) or (str(row.get("major")) in set(map(str, f_major)))
        ok_tag = True
        if f_tag.strip():
            wanted = {t.strip().lower() for t in f_tag.split(TAG_SEP) if t.strip()}
            have = {t.lower() for t in to_list(row.get("tags", ""))}
            ok_tag = bool(wanted & have)
        return ok_q and ok_year and ok_major and ok_tag

    filtered = df_users[df_users.apply(matches, axis=1)].copy()
    # Show count & sort
    st.write(f"Showing **{len(filtered)}** of {len(df_users)} members")
    sort_key = st.selectbox("Sort by", ["name", "major", "year"], index=0)
    filtered = filtered.sort_values(by=sort_key, na_position="last")

    # Render cards
    for _, r in filtered.iterrows():
        profile_card(r, enable_actions=bool(me is not None and me.email != r.email))


def my_profile_page(df_users: pd.DataFrame, me: pd.Series):
    st.subheader("My Profile")
    st.caption("Keep this updated so others can find you.")

    idx = df_users.index[df_users["email"].str.lower() == me.email.lower()][0]

    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name", value=me.get("name", ""))
            year = st.text_input("Graduation Year", value=str(me.get("year", "")))
            major = st.text_input("Major", value=me.get("major", ""))
            linkedin = st.text_input("LinkedIn URL", value=me.get("linkedin", ""))
        with col2:
            slack = st.text_input("Slack handle", value=me.get("slack", ""), placeholder="@your-handle")
            calendly = st.text_input("Calendly (optional)", value=me.get("calendly", ""))
            seeking = st.text_input("Seeking roles (comma‑sep)", value=me.get("seeking_roles", ""))
            offering = st.text_input("Offering help (comma‑sep)", value=me.get("offering_help", ""))
        bio = st.text_area("Short bio", value=me.get("bio", ""), height=120)
        skills = st.text_input("Skills (comma‑sep)", value=me.get("skills", ""))
        interests = st.text_input("Interests (comma‑sep)", value=me.get("interests", ""))
        projects = st.text_input("Projects (brief; comma‑sep)", value=me.get("projects", ""))
        tags = st.text_input("Tags (comma‑sep)", value=me.get("tags", ""), placeholder="e.g., AI, PM, Consulting")

        save_btn = st.form_submit_button("Save changes")

    if save_btn:
        df_users.loc[idx, "name"] = name
        df_users.loc[idx, "year"] = year
        df_users.loc[idx, "major"] = major
        df_users.loc[idx, "linkedin"] = linkedin
        df_users.loc[idx, "slack"] = slack
        df_users.loc[idx, "calendly"] = calendly
        df_users.loc[idx, "seeking_roles"] = seeking
        df_users.loc[idx, "offering_help"] = offering
        df_users.loc[idx, "bio"] = bio
        df_users.loc[idx, "skills"] = skills
        df_users.loc[idx, "interests"] = interests
        df_users.loc[idx, "projects"] = projects
        df_users.loc[idx, "tags"] = tags
        df_users.loc[idx, "last_updated"] = datetime.now().isoformat(timespec="seconds")
        save_users(df_users)
        st.success("Profile updated!")
        st.rerun()

    st.divider()
    st.markdown("### Preview")
    profile_card(df_users.loc[idx], enable_actions=False)


def suggestions_block(df_users: pd.DataFrame, me: pd.Series):
    st.subheader("Suggested connections")
    mine = set(to_list(me.skills)) | set(to_list(me.interests)) | set(to_list(me.tags))
    if not mine:
        st.info("Add skills/interests/tags to your profile to get suggestions.")
        return

    def overlap_score(r: pd.Series) -> int:
        theirs = set(to_list(r.skills)) | set(to_list(r.interests)) | set(to_list(r.tags))
        return len(mine & theirs)

    candidates = (
        df_users[df_users["email"].str.lower() != me.email.lower()]
        .copy()
    )
    candidates["score"] = candidates.apply(overlap_score, axis=1)
    top = candidates[candidates["score"] > 0].sort_values("score", ascending=False).head(5)
    if top.empty:
        st.write("No close matches yet — try adding more tags or broaden filters in the directory.")
        return
    for _, r in top.iterrows():
        profile_card(r)


def coffee_chats_page(df_users: pd.DataFrame, me: pd.Series):
    st.subheader("Coffee Chats")
    st.caption("View incoming/outgoing requests. (Demo logger; replace with email/Slack notifications in prod.)")

    df_req = load_requests()
    mine_in = df_req[df_req["to_email"].str.lower() == me.email.lower()].copy()
    mine_out = df_req[df_req["from_email"].str.lower() == me.email.lower()].copy()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Incoming requests**")
        if mine_in.empty:
            st.write("No incoming requests yet.")
        else:
            for i, row in mine_in.sort_values("created_at", ascending=False).iterrows():
                with st.container(border=True):
                    sender = row["from_email"]
                    st.write(f"From: {sender}")
                    st.write(row["message"])
                    st.caption(f"Sent: {row['created_at']}")
                    cols = st.columns(3)
                    if st.button("Accept", key=f"acc_{i}"):
                        df_req.loc[i, "status"] = "accepted"
                        save_requests(df_req)
                        st.success("Accepted — DM them on Slack or share your Calendly.")
                    if st.button("Decline", key=f"dec_{i}"):
                        df_req.loc[i, "status"] = "declined"
                        save_requests(df_req)
                        st.info("Declined.")
                    cols[2].write(f"Status: **{row['status']}**")

    with col2:
        st.markdown("**Outgoing requests**")
        if mine_out.empty:
            st.write("No outgoing requests yet.")
        else:
            for _, row in mine_out.sort_values("created_at", ascending=False).iterrows():
                with st.container(border=True):
                    st.write(f"To: {row['to_email']}")
                    st.write(row["message"])
                    st.caption(f"Sent: {row['created_at']}")
                    st.write(f"Status: **{row['status']}**")


def admin_page():
    st.subheader("Admin / Data Export")
    st.caption("Quick views of raw data (CSV persisted locally in ./data)")

    users = load_users()
    st.markdown("**Users**")
    st.dataframe(users, use_container_width=True, hide_index=True)

    reqs = load_requests()
    st.markdown("**Coffee Requests**")
    st.dataframe(reqs, use_container_width=True, hide_index=True)

    st.download_button(
        "Download users.csv",
        users.to_csv(index=False).encode("utf-8"),
        file_name="users.csv",
        mime="text/csv",
    )
    st.download_button(
        "Download coffee_requests.csv",
        reqs.to_csv(index=False).encode("utf-8"),
        file_name="coffee_requests.csv",
        mime="text/csv",
    )


# ----------------------------
# App Shell
# ----------------------------
def sidebar(me: Optional[pd.Series]):
    with st.sidebar:
        st.title("🤝 PurdueTHINK")
        if me is not None:
            st.write(f"Signed in as:\n**{me.get('name') or me.email}**")
            if st.button("Sign out"):
                st.session_state.pop(KEY_USER, None)
                st.rerun()
        else:
            st.write("Not signed in")
        st.markdown("---")
        page = st.radio(
            "Navigate",
            ["Dashboard", "Directory", "My Profile", "Coffee Chats", "Admin"],
            index=0,
        )
        return page


def dashboard_page(df_users: pd.DataFrame, me: Optional[pd.Series]):
    st.subheader("Dashboard")
    st.caption("At-a-glance suggestions and quick links.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Quick Actions")
        st.link_button("Browse Directory", "#people-directory")
        st.link_button("Edit My Profile", "#my-profile")
        st.link_button("Coffee Chats", "#coffee-chats")

    with col2:
        st.markdown("### Tips")
        st.write("• Add a Calendly link to make scheduling easy.")
        st.write("• Use clear tags (e.g., 'AI, PM, Consulting') so others can find you.")

    st.divider()
    if me is not None:
        suggestions_block(df_users, me)
    else:
        st.info("Sign in to see personalized suggestions.")


def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🤝", layout="wide")
    st.title(APP_TITLE)

    ensure_data_dir()
    seed_users_csv()
    seed_requests_csv()

    users = load_users()

    if KEY_USER not in st.session_state:
        login_ui()
        return

    me = current_user(users)
    page = sidebar(me)

    # Anchors for quick links on dashboard
    st.markdown('<a name="people-directory"></a>', unsafe_allow_html=True)

    if page == "Dashboard":
        dashboard_page(users, me)
    elif page == "Directory":
        directory_page(users, me)
    elif page == "My Profile":
        st.markdown('<a name="my-profile"></a>', unsafe_allow_html=True)
        my_profile_page(users, me)
    elif page == "Coffee Chats":
        st.markdown('<a name="coffee-chats"></a>', unsafe_allow_html=True)
        coffee_chats_page(users, me)
    elif page == "Admin":
        admin_page()


if __name__ == "__main__":
    main()
