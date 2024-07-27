
from app.scraper import Scraper


def test_scraper():
    result = Scraper(
        "https://pypi.org/project/cloudscraper/", "//h1[@class='package-header__name']/text()")

    assert "cloudscraper" in result, "scraper failed"
