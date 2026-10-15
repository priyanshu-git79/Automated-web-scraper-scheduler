
import csv
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from threading import Lock

from flask import (
    Flask, render_template, redirect, url_for,
    flash, send_file
)
from apscheduler.schedulers.background import BackgroundScheduler

from scraper import scrape_website, CSV_FILE

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_FILE = DATA_DIR / "scraper_history.db"

app = Flask(__name__)
app.secret_key = "replace-with-a-random-secret-before-deployment"

logging.basicConfig(level=logging.INFO)

status = {
    "last_run": "Not run yet",
    "message": "Waiting for the first scrape"
}

scrape_lock = Lock()


def get_db_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Create the persistent scraping history table."""
    with get_db_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS scraping_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_time TEXT NOT NULL,
                result TEXT NOT NULL,
                quotes_found INTEGER NOT NULL DEFAULT 0,
                records_added INTEGER NOT NULL DEFAULT 0,
                message TEXT NOT NULL
            )
        """)


def save_history(result, quotes_found=0, records_added=0, message=""):
    with get_db_connection() as connection:
        connection.execute("""
            INSERT INTO scraping_history
                (run_time, result, quotes_found, records_added, message)
            VALUES (?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            result,
            quotes_found,
            records_added,
            message
        ))


def get_history(limit=20):
    with get_db_connection() as connection:
        rows = connection.execute("""
            SELECT * FROM scraping_history
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

    return [dict(row) for row in rows]


def read_records():
    """Read the current quote CSV."""
    if not CSV_FILE.exists():
        return []

    with CSV_FILE.open(
        "r", newline="", encoding="utf-8-sig"
    ) as file:
        return list(csv.DictReader(file))


def run_scrape():
    """Run scraping and save the result to SQLite history."""
    if not scrape_lock.acquire(blocking=False):
        return {
            "result": "Skipped",
            "message": "Another scraping task is already running."
        }

    try:
        result = scrape_website()

        message = (
            f"Success: found {result['found']} quotes and "
            f"added {result['added']} new records."
        )

        status["last_run"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        status["message"] = message

        save_history(
            "Success",
            result["found"],
            result["added"],
            message
        )

        logging.info(message)

        return {"result": "Success", "message": message}

    except Exception as error:
        message = f"Scraping failed: {error}"

        status["last_run"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        status["message"] = message

        save_history("Failed", message=message)
        logging.exception("Scraping failed")

        return {"result": "Failed", "message": message}

    finally:
        scrape_lock.release()


@app.route("/")
def index():
    return render_template(
        "index.html",
        records=read_records(),
        status=status,
        history=get_history()
    )


@app.route("/run", methods=["POST"])
def run_now():
    result = run_scrape()
    flash(result["message"])
    return redirect(url_for("index"))


@app.route("/download")
def download_csv():
    if not CSV_FILE.exists():
        flash("No CSV file exists yet. Run the scraper first.")
        return redirect(url_for("index"))

    return send_file(
        CSV_FILE,
        as_attachment=True,
        download_name="quotes.csv",
        mimetype="text/csv"
    )


initialize_database()

scheduler = BackgroundScheduler()
scheduler.add_job(
    run_scrape,
    trigger="interval",
    minutes=10,
    id="website_scraper",
    max_instances=1,
    coalesce=True
)


if __name__ == "__main__":
    scheduler.start()

    try:
        app.run(debug=False, use_reloader=False)
    finally:
        scheduler.shutdown(wait=False)
