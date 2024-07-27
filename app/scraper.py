import logging
import cloudscraper
from lxml import etree


class Scraper:

    def scrape(url: str, xpath: str) -> str:
        try:
            scraper = cloudscraper.create_scraper()
            response = scraper.get(url)
            if not response.ok:
                logging.error(f"could not read {url} status: {
                              response.status_code}")
                return None
        except BaseException as error:
            logging.error(f"could not read {url} error: {error}")
            return None

        tree = etree.HTML(response.text)
        if tree is None:
            logging.error(f"could not parse '{url}'")
            return None

        result = tree.xpath(xpath)
        if len(result) == 0:
            logging.error(f"did not find '{xpath}' in '{url}'")
            return None
        elif len(result) > 1:
            logging.info(f"found more than one '{xpath}' in '{
                         url}' returning first one")

        return str(result[0]).strip()
