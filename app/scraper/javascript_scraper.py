
import logging
from lxml import etree

from app.scraper.scraper import Scraper
from app.scraper.webdrivercreator import WebDriverCreator

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC


class JavaScriptScraper(Scraper):

    DEFAULT_WAIT_TIMEOUT = 10

    def scrape(self, url: str, xpath: str) -> str:
        # selenium cannot resolve non webelements such as texts
        selenium_xpath = xpath.replace("/text()", "")

        webdriver = WebDriverCreator.create_webdriver()
        webdriver.get(url)
        elements = self.wait_for_element(webdriver, selenium_xpath)
        source = webdriver.page_source
        webdriver.close()

        # xpath parsing
        tree = etree.HTML(source)

        if tree is None:
            raise Exception(f"could not parse '{url}'")
        result = tree.xpath(xpath)
        if len(result) == 0:
            raise Exception(f"did not find '{xpath}' in '{url}'")
        elif len(result) > 1:
            logging.info(f"found more than one '{xpath}' in '{
                         url}' returning first one")

        return str(result[0]).strip()

    def wait_for_element(self, webdriver: WebDriver, xpath: str):
        try:
            elements = WebDriverWait(webdriver, self.DEFAULT_WAIT_TIMEOUT).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, xpath))
            )
        except TimeoutException:
            raise Exception(f"could not find '{xpath}' in '{
                            webdriver.current_url}'")

        return elements
