from app.scraper.default_scraper import DefaultScraper
from app.scraper.javascript_scraper import JavaScriptScraper
from app.scraper.scraper_factory import ScraperFactory


def test_scraper_factory():
    default_scraper = ScraperFactory().get_scraper(enabled_javascript=False)
    assert isinstance(default_scraper, DefaultScraper)

    javascript_scraper = ScraperFactory().get_scraper(enabled_javascript=True)
    assert isinstance(javascript_scraper, JavaScriptScraper)
