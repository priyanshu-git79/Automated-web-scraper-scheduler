
import csv
from pathlib import Path
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

# Website used for learning web scraping
URL = "https://quotes.toscrape.com/"

# Save the CSV inside the project's data folder
DATA_DIR = Path(__file__).parent / "data"
CSV_FILE = DATA_DIR / "quotes.csv"

FIELDS = ["quote", "author", "tags", "source_url", "scraped_at"]


def scrape_website():
    """Collect quotes from the demo website and save them to CSV."""

    DATA_DIR.mkdir(exist_ok=True)

    print("Connecting to website...")

    response = requests.get(
        URL,
        timeout=20,
        headers={"User-Agent": "StudentWebScraper/1.0"}
    )
    response.raise_for_status()

    print("Website connected. Extracting information...")

    soup = BeautifulSoup(response.text, "html.parser")
    records = []

    for item in soup.select("div.quote"):
        quote = item.select_one("span.text")
        author = item.select_one("small.author")

        if quote is None or author is None:
            continue

        tags = [
            tag.get_text(strip=True)
            for tag in item.select(".tags .tag")
        ]

        records.append({
            "quote": quote.get_text(strip=True),
            "author": author.get_text(strip=True),
            "tags": ", ".join(tags),
            "source_url": URL,
            "scraped_at": datetime.now(
                timezone.utc
            ).isoformat(timespec="seconds")
        })

    if not records:
        raise RuntimeError(
            "No quotes found. The website structure may have changed."
        )

    # Read existing quotes to avoid duplicates
    existing_quotes = set()

    if CSV_FILE.exists():
        with CSV_FILE.open(
            "r", newline="", encoding="utf-8-sig"
        ) as file:
            for row in csv.DictReader(file):
                existing_quotes.add(row["quote"])

    new_records = [
        record for record in records
        if record["quote"] not in existing_quotes
    ]

    file_exists = CSV_FILE.exists() and CSV_FILE.stat().st_size > 0

    with CSV_FILE.open(
        "a", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)

        if not file_exists:
            writer.writeheader()

        writer.writerows(new_records)

    print(f"Quotes found: {len(records)}")
    print(f"New quotes saved: {len(new_records)}")
    print(f"CSV location: {CSV_FILE.resolve()}")

    
    return {
        "found": len(records),
        "added": len(new_records)
    }



if __name__ == "__main__":
    scrape_website()
