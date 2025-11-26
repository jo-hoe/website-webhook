
from lxml import etree

from app.scraper.scraper import Scraper

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC

from selenium_crawler import create_webdriver


class JavaScriptScraper(Scraper):

    DEFAULT_WAIT_TIMEOUT = 10

    def scrape(self, url: str, xpath: str) -> str:
        # selenium cannot resolve non webelements such as texts
        selenium_xpath = xpath.replace("/text()", "")

        webdriver = None
        tree = None
        result = None
        
        try:
            webdriver = create_webdriver()
            webdriver.get(url)
            self.wait_for_element(webdriver, selenium_xpath)
            source = webdriver.page_source
            
            # xpath parsing
            tree = etree.HTML(source, parser=None)
            result = self._find_element_in_tree(tree, xpath)
            
        finally:
            # Explicitly clean up resources
            if tree is not None:
                tree.clear()
                del tree
            
            if webdriver is not None:
                webdriver.quit()
                del webdriver
        
        return result

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
