
import abc
import logging
from lxml import etree


class Scraper(abc.ABC):

    @abc.abstractmethod
    def scrape(self, url: str, xpath: str) -> str:
        pass

    def _find_element_in_tree(self, tree: etree.Element, xpath: str) -> str:
        if tree is None:
            raise Exception(f"could not parse content")
        found_elements = tree.xpath(xpath)

        if found_elements is None or len(found_elements) == 0:
            raise Exception(f"did not find result for given xpath")
        elif len(found_elements) > 1:
            logging.warning(f"found more than one in item returning first one")

        return str(found_elements[0]).strip()
