import logging
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

        if tree is None:
            raise Exception(f"could not parse '{url}'")
        result = tree.xpath(xpath)
        if len(result) == 0:
            raise Exception(f"did not find '{xpath}' in '{url}'")
        elif len(result) > 1:
            logging.info(f"found more than one '{xpath}' in '{
                         url}' returning first one")

        return str(result[0]).strip()
