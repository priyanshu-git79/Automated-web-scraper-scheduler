
import app as scraper_app


def test_homepage_loads():
    client = scraper_app.app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"Automated Web Scraper" in response.data


def test_history_is_saved(monkeypatch):
    # Replace the scraping function with a predictable test result.
    monkeypatch.setattr(
        scraper_app,
        "scrape_website",
        lambda: {"found": 10, "added": 2}
    )

    result = scraper_app.run_scrape()

    assert result["result"] == "Success"
    assert "10 quotes" in result["message"]

    history = scraper_app.get_history()

    assert len(history) > 0
    assert history[0]["result"] == "Success"
    assert history[0]["quotes_found"] == 10
    assert history[0]["records_added"] == 2


def test_csv_download_route():
    client = scraper_app.app.test_client()

    response = client.get("/download")

    # The file exists in the project from the earlier scraper step.
    assert response.status_code == 200
    assert "attachment" in response.headers.get(
        "Content-Disposition", ""
    )


def test_failed_scrape_is_recorded(monkeypatch):
    def raise_error():
        raise RuntimeError("Test connection error")

    monkeypatch.setattr(
        scraper_app, "scrape_website", raise_error
    )

    result = scraper_app.run_scrape()

    assert result["result"] == "Failed"

    history = scraper_app.get_history()
    assert history[0]["result"] == "Failed"
    assert "Test connection error" in history[0]["message"]
