import logging
import cloudscraper
from lxml import etree


class Scraper:

    def scrape(self, url: str, xpath: str) -> str:
        # request to webpage
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url)
        if not response.ok:
            raise Exception(f"could not read {url} status: {
                response.status_code}")

        # xpath parsing
        tree = etree.HTML(response.text)
        if tree is None:
            raise Exception(f"could not parse '{url}'")
        result = tree.xpath(xpath)
        if len(result) == 0:
            raise Exception(f"did not find '{xpath}' in '{url}'")
        elif len(result) > 1:
            logging.info(f"found more than one '{xpath}' in '{
                         url}' returning first one")

        return str(result[0]).strip()
