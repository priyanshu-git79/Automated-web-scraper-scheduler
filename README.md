
# Automated Web Scraper with Scheduler

A Python-based web scraping application that collects quotes from a
practice website, saves the results in CSV format, and runs scraping
tasks automatically using a background scheduler.

## Features

- Extracts quotes, authors, and tags from HTML pages.
- Saves collected data to a CSV file.
- Avoids duplicate quotes across repeated runs.
- Provides a Flask web dashboard.
- Supports manual scraping through a dashboard button.
- Runs scraping automatically at scheduled intervals.
- Stores scraping history in an SQLite database.
- Allows users to download the collected CSV file.
- Includes automated tests using pytest.

## Technologies Used

- Python
- Flask
- Requests
- BeautifulSoup4
- APScheduler
- SQLite
- CSV
- pytest
- HTML and CSS

## Project Structure

```text
Project 1/
├── app.py
├── scraper.py
├── requirements.txt
├── README.md
├── data/
│   ├── quotes.csv
│   └── scraper_history.db
├── templates/
│   └── index.html
├── static/
│   └── style.css
└── tests/
    └── test_app.py
```

## Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd YOUR_PROJECT_FOLDER
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the scraper

```bash
python scraper.py
```

### 5. Start the web application

```bash
python app.py
```

Open http://127.0.0.1:5000/ in your browser.

## Running Tests

```bash
python -m pytest -v
```

## Data Storage

- CSV: Stores collected quotes, authors, tags, source URLs,
  and scrape timestamps.
- SQLite: Stores scraping run history, status, and record counts.

## Scheduler

The application runs a scraping job every 10 minutes while the
Flask application is running.

The scheduler is intended for local development. For continuous
production scheduling, deploy the application with a persistent
background worker or a dedicated scheduler.

## Learning Outcomes

This project demonstrates:

- HTTP requests and HTML parsing.
- Data extraction and CSV handling.
- Flask routing and template rendering.
- Background task scheduling.
- SQLite database operations.
- Error handling and automated testing.

## Limitations

- The scraper currently targets a practice website.
- Website HTML changes may require selector updates.
- The scheduler stops when the application stops.
- The application is a learning prototype and is not configured
  for public production deployment.

## Future Improvements

- Support configurable websites and schedules.
- Add search and pagination to the dashboard.
- Add a CSV export history.
- Store detailed logs and improve error notifications.
- Deploy the application to a suitable hosting platform.

## Author

Your Name

Student Project | Internship Portfolio
