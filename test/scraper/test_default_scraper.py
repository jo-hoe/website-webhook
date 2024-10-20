
import pytest
from app.scraper.default_scraper import DefaultScraper


@pytest.mark.integration_test
def test_scraper():
    scraper = DefaultScraper()
    result = scraper.scrape(
        "https://pypi.org/project/cloudscraper/", "//h1[@class='package-header__name']/text()")

    assert "cloudscraper" in result, "scraper failed"



@pytest.mark.integration_test
def test_get_rss_feed():
    test_rss_url = "http://feeds.bbci.co.uk/news/world/rss.xml"
    
    scraper = DefaultScraper()
    result = scraper.scrape(
        test_rss_url, "(//item/guid/text())[1]")

    assert "www.bbc.com" in result, "scraper failed"