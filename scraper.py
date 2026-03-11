import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Google Sheets connection
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Job Scraper").sheet1

jobs = []

# ------------------- Helper to scrape Indeed -------------------
def scrape_indeed(keyword="data engineer"):
    url = f"https://www.indeed.com/jobs?q={keyword.replace(' ','+')}&l=United+States&fromage=1"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    for job in soup.select(".job_seen_beacon"):
        title = job.select_one("h2").text.strip()
        company = job.select_one(".companyName").text.strip()
        location = job.select_one(".companyLocation").text.strip()
        link = "https://indeed.com" + job.select_one("a")["href"]
        jobs.append([title, company, location, "Indeed", link, datetime.now().strftime("%Y-%m-%d")])

# ------------------- Helper to scrape Dice -------------------
def scrape_dice(keyword="data engineer"):
    url = f"https://www.dice.com/jobs?q={keyword.replace(' ','%20')}&countryCode=US&radius=25&postedDate=1"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    for job in soup.select("a.card-title-link"):
        title = job.text.strip()
        company = job.find_next("div", class_="card-company").text.strip() if job.find_next("div", class_="card-company") else "N/A"
        location = job.find_next("div", class_="card-location").text.strip() if job.find_next("div", class_="card-location") else "N/A"
        link = "https://www.dice.com" + job['href']
        jobs.append([title, company, location, "Dice", link, datetime.now().strftime("%Y-%m-%d")])

# ------------------- Scrape multiple keywords -------------------
keywords = ["data engineer", "ServiceNow developer", "Salesforce developer"]

for keyword in keywords:
    scrape_indeed(keyword)
    scrape_dice(keyword)

# Append jobs to Google Sheet
for row in jobs:
    sheet.append_row(row)

print(f"{len(jobs)} jobs added successfully!")
