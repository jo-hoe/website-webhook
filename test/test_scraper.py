
from app.scraper import scrape


def test_scraper():
    result = scrape(
        "https://pypi.org/project/cloudscraper/", "//h1[@class='package-header__name']/text()")

    assert "cloudscraper" in result, "scraper failed"
