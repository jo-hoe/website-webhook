from app.scraper.default_scraper import DefaultScraper
from app.scraper.javascript_scraper import JavaScriptScraper
from app.scraper.scraper import Scraper


class ScraperFactory():

    @staticmethod
    def get_scraper(enabled_javascript: bool) -> Scraper:
        if enabled_javascript:
            return JavaScriptScraper()
        else:
            return DefaultScraper()
