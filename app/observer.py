import logging
import cloudscraper
from lxml import etree

def observe(url: str, xpath: str) -> str:
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url)
        if response.ok:
            return response.text, response.status_code
    except BaseException as error:
        logging.error(f"could not read {url} error: {error}")
        return ""

    tree = etree.HTML(response.text)
    if tree is None:
        logging.error(f"could not parse '{url}'")
        return ""

    return tree.xpath(xpath)
