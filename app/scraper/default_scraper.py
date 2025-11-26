import cloudscraper
from lxml import etree

from app.scraper.scraper import Scraper


class DefaultScraper(Scraper):

    def scrape(self, url: str, xpath: str) -> str:
        scraper = None
        tree = None
        result = None
        
        try:
            # request to webpage
            scraper = cloudscraper.create_scraper()
            response = scraper.get(url)
            if not response.ok:
                raise Exception(f"could not read {url} status: {
                    response.status_code}")

            encoded_response = response.text.encode('utf-8')
            
            # Check content type before closing response
            is_xml = response.headers.get('content-type') and "text/xml" in response.headers.get('content-type', '')
            
            # Clear response reference to allow garbage collection
            response.close()
            del response

            # xpath parsing
            if is_xml:
                tree = etree.XML(encoded_response)
            else:
                tree = etree.HTML(encoded_response)

            result = self._find_element_in_tree(tree, xpath)
            
        finally:
            # Explicitly clean up resources
            if tree is not None:
                tree.clear()
                del tree
            
            if scraper is not None:
                scraper.close()
                del scraper
        
        return result
