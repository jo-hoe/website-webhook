
import abc


class Scraper(abc.ABC):

    @abc.abstractmethod
    def scrape(self, url: str, xpath: str) -> str:
        pass
