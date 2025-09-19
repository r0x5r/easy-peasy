import streamlit as st
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="Remote Cyber Security Jobs", layout="wide")
st.title("🌐 Remote Cyber Security Jobs Aggregator")
st.write(
    "Fetches the latest remote, easy-apply cyber security jobs (Penetration Tester, Ethical Hacker, Security Analyst, etc.) from multiple sources."
)

KEYWORDS = [
    "penetration tester", "ethical hacker", "cyber security analyst",
    "security analyst", "soc analyst", "security engineer", "threat hunter",
    "red team", "blue team", "security researcher"
]

def fetch_remoteok():
    url = "https://remoteok.com/api"
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if resp.status_code == 200:
        jobs = resp.json()
        return jobs[1:]  # metadata is first element
    return []

def fetch_infosec():
    url = "https://infosec-jobs.com/api/jobs/"
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.json().get("results", [])
    return []

def is_recent(date_str, days=3):
    try:
        post_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
        return (datetime.utcnow() - post_date).days <= days
    except Exception:
        return False

def filter_jobs(jobs, keywords, source):
    filtered = []
    for job in jobs:
        if source == "remoteok":
            text = (job.get("position", "") + " " + " ".join(job.get("tags", []))).lower()
            date_str = job.get("date", "") or job.get("posted_at", "") or job.get("created_at", "")
            if is_recent(date_str) and any(k in text for k in keywords):
                filtered.append({
                    "title": job.get("position"),
                    "company": job.get("company"),
                    "location": job.get("location", "Remote/Worldwide"),
                    "tags": ", ".join(job.get("tags", [])),
                    "date": date_str[:10],
                    "apply_url": job.get("url"),
                    "source": "Remote OK"
                })
        elif source == "infosec":
            text = (job.get("title", "") + " " + " ".join(job.get("tags", []))).lower()
            date_str = job.get("published_at", "")
            if is_recent(date_str) and any(k in text for k in keywords):
                filtered.append({
                    "title": job.get("title"),
                    "company": job.get("company"),
                    "location": job.get("location", "Remote/Worldwide"),
                    "tags": ", ".join(job.get("tags", [])),
                    "date": date_str[:10],
                    "apply_url": job.get("url"),
                    "source": "InfoSec Jobs"
                })
    return filtered

st.info("Fetching jobs...")

jobs_remoteok = fetch_remoteok()
jobs_infosec = fetch_infosec()

filtered_jobs = filter_jobs(jobs_remoteok, KEYWORDS, "remoteok") + filter_jobs(jobs_infosec, KEYWORDS, "infosec")
filtered_jobs = sorted(filtered_jobs, key=lambda x: x["date"], reverse=True)

if filtered_jobs:
    st.success(f"Found {len(filtered_jobs)} new remote cyber security jobs from multiple sources!")
    for job in filtered_jobs:
        with st.expander(f"{job['title']} at {job['company']} [{job['source']}]"):
            st.write(f"**Company:** {job['company']}")
            st.write(f"**Position:** {job['title']}")
            st.write(f"**Location:** {job['location']}")
            st.write(f"**Tags:** {job['tags']}")
            st.write(f"**Date Posted:** {job['date']}")
            st.markdown(f"[Apply Here]({job['apply_url']})")
else:
    st.warning("No new remote cyber security jobs found in the past 3 days. Please check back later!")

st.caption("Powered by Remote OK and InfoSec Jobs APIs. For more, visit Indeed, LinkedIn, or Dice for manual search and alerts.")
