
import pytest
from app.scraper.javascript_scraper import JavaScriptScraper


@pytest.mark.integration_test
def test_scraper():
    scraper = JavaScriptScraper()
    result = scraper.scrape(
        "https://pypi.org/project/selenium/", "//h1[@class='package-header__name']/text()")

    assert "selenium" in result, "scraper failed"


@pytest.mark.integration_test
def test_get_rss_feed():
    test_rss_url = "http://feeds.bbci.co.uk/news/world/rss.xml"

    scraper = JavaScriptScraper()
    result = scraper.scrape(
        test_rss_url, "(//item/guid/text())[1]")

    assert "www.bbc.com" in result, "scraper failed"
