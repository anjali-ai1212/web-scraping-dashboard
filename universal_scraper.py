import requests
import re
from bs4 import BeautifulSoup

def scrape_website(url):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=15)

    soup = BeautifulSoup(response.text, "lxml")

    title = soup.title.text.strip() if soup.title else "No Title"

    meta = soup.find("meta", attrs={"name": "description"})

    description = meta.get("content").strip() if meta and meta.get("content") else "No Description"

    # Links
    links = [a["href"] for a in soup.find_all("a", href=True)]

    # Images
    images = [img.get("src") for img in soup.find_all("img", src=True)]

    # Headings
    headings = []

    for tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
        for h in soup.find_all(tag):
            text = h.get_text(strip=True)
            if text:
                headings.append(text)

    # Emails
    emails = list(set(re.findall(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        response.text
    )))

    # Phone Numbers
    phones = list(set(re.findall(
        r"\+?\d[\d\s\-()]{7,}\d",
        response.text
    )))

    return {
        "title": title,
        "description": description,
        "total_links": len(links),
        "links": links,

        "total_images": len(images),
        "images": images,

        "total_headings": len(headings),
        "headings": headings,

        "total_emails": len(emails),
        "emails": emails,

        "total_phones": len(phones),
        "phones": phones
    }