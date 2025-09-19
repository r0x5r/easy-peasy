# MIT License
#
# Copyright (c) 2025 xAI
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import requests
from bs4 import BeautifulSoup
import time
import webbrowser
import json  # For saving seen jobs persistently

# Configuration - Customize these
KEYWORDS = "software engineer"  # Replace with your job keywords, e.g., "data scientist"
LOCATION = "United States"  # Replace with your location, e.g., "San Francisco"
POLL_INTERVAL = 60  # Seconds between checks (e.g., 60 for every minute)
SEEN_FILE = "seen_jobs.json"  # File to store seen job URLs

# Base URL for LinkedIn job search API (guest mode, no login needed)
BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?"
# Add filters for recent jobs (last 24 hours: r86400 seconds; adjust as needed, e.g., r3600 for last hour)
PARAMS = f"keywords={KEYWORDS.replace(' ', '%20')}&location={LOCATION.replace(' ', '%20')}&f_TPR=r86400&start="

# Load seen jobs from file if exists
try:
    with open(SEEN_FILE, 'r') as f:
        seen_jobs = set(json.load(f))
except FileNotFoundError:
    seen_jobs = set()

def save_seen_jobs():
    with open(SEEN_FILE, 'w') as f:
        json.dump(list(seen_jobs), f)

print(f"Monitoring new {KEYWORDS} jobs in {LOCATION}. Press Ctrl+C to stop.")

while True:
    new_jobs_found = False
    page = 0
    while page < 100:  # Limit to first 4 pages (100 jobs) to avoid rate limiting
        url = BASE_URL + PARAMS + str(page)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            jobs = soup.find_all('div', class_='base-card')
            if not jobs:
                break  # No more jobs on this page
            
            for job in jobs:
                job_link_tag = job.find('a', class_='base-card__full-link')
                if not job_link_tag:
                    continue
                job_link = job_link_tag['href']
                
                if job_link not in seen_jobs:
                    seen_jobs.add(job_link)
                    new_jobs_found = True
                    
                    # Extract details
                    job_title = job.find('h3', class_='base-search-card__title').text.strip() if job.find('h3', class_='base-search-card__title') else "N/A"
                    job_company = job.find('h4', class_='base-search-card__subtitle').text.strip() if job.find('h4', class_='base-search-card__subtitle') else "N/A"
                    job_location = job.find('span', class_='job-search-card__location').text.strip() if job.find('span', class_='job-search-card__location') else "N/A"
                    
                    print(f"\nNew Job Found!")
                    print(f"Title: {job_title}")
                    print(f"Company: {job_company}")
                    print(f"Location: {job_location}")
                    print(f"Link: {job_link}")
                    
                    # Automatically open the job in your default browser for quick application
                    webbrowser.open(job_link)
            
            page += 25  # LinkedIn paginates by 25 jobs
        except Exception as e:
            print(f"Error fetching page: {e}")
            break
    
    if new_jobs_found:
        save_seen_jobs()
    
    print(f"No new jobs found this cycle. Checking again in {POLL_INTERVAL} seconds...")
    time.sleep(POLL_INTERVAL)
