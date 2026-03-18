import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import feedparser

EMAIL_SENDER = "sundayadewole1997@gmail.com"
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
EMAIL_RECIPIENT = "sundayadewole1997@gmail.com"

KEYWORDS = [
    '".NET MAUI" remote',
    'Xamarin remote',
    '"MAUI developer" remote',
    '"Xamarin developer" remote',
    'C# mobile AI remote',
    '"AI mobile developer" C# remote'
]

RSS_URL = "https://www.indeed.com/rss?q={query}&l=Remote"


def fetch_jobs():
    jobs = []
    cutoff = datetime.utcnow() - timedelta(hours=24)

    for kw in KEYWORDS:
        url = RSS_URL.format(query=kw.replace(" ", "+"))
        feed = feedparser.parse(url)

        for entry in feed.entries:
            published = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6])

            if published and published < cutoff:
                continue

            jobs.append({
                "title": entry.title,
                "company": getattr(entry, "author", "Unknown"),
                "link": entry.link,
                "published": published.strftime("%Y-%m-%d %H:%M") if published else "N/A",
            })

    # Remove duplicates
    unique = {j["link"]: j for j in jobs}
    return list(unique.values())


def send_email(jobs):
    if not jobs:
        print("No jobs found.")
        return

    subject = f"MAUI/Xamarin Remote Jobs — {datetime.now().date()}"

    body = "\n\n".join(
        f"{j['title']}\nCompany: {j['company']}\nPublished: {j['published']}\nApply: {j['link']}"
        for j in jobs
    )

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECIPIENT

    with smtplib.SMTP("smtp.gmail.com", 587) as s:
        s.starttls()
        s.login(EMAIL_SENDER, EMAIL_PASSWORD)
        s.send_message(msg)

    print("Email sent:", len(jobs), "jobs")


if __name__ == "__main__":
    jobs = fetch_jobs()
    send_email(jobs)
