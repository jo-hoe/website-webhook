import cloudscraper
from lxml import etree

from app.scraper.scraper import Scraper


class DefaultScraper(Scraper):

    def scrape(self, url: str, xpath: str) -> str:
        # request to webpage
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url)
        if not response.ok:
            raise Exception(f"could not read {url} status: {
                response.status_code}")

        encoded_response = response.text.encode('utf-8')

        # xpath parsing
        tree = None
        # check if response is pure xml text
        if response.headers['content-type'] and "text/xml" in response.headers['content-type']:
            tree = etree.XML(encoded_response)
        else:
            tree = etree.HTML(encoded_response)

        return self._find_element_in_tree(tree, xpath)
