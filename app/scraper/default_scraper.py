import cloudscraper
from lxml import etree
import gc

from app.scraper.scraper import Scraper


class DefaultScraper(Scraper):
    
    def __init__(self):
        """Initialize with a reusable scraper session to prevent memory leaks from repeated session creation."""
        super().__init__()
        self._scraper = cloudscraper.create_scraper()

    def scrape(self, url: str, xpath: str) -> str:
        tree = None
        result = None
        response = None

        try:
            # Use reusable scraper instance instead of creating new one each time
            response = self._scraper.get(url)
            if not response.ok:
                raise Exception(f"could not read {url} status: {response.status_code}")

            encoded_response = response.text.encode('utf-8')

            # Check content type before closing response
            is_xml = response.headers.get(
                'content-type') and "text/xml" in response.headers.get('content-type', '')

            # xpath parsing
            if is_xml:
                tree = etree.XML(encoded_response)
            else:
                tree = etree.HTML(encoded_response)

            result = self._find_element_in_tree(tree, xpath)

        finally:
            # Explicitly clean up resources in correct order
            if response is not None:
                response.close()
                del response
            
            if tree is not None:
                tree.clear()
                del tree
            
            # Force garbage collection after each scrape to prevent buildup
            gc.collect()

        return result
    
    def __del__(self):
        """Cleanup the scraper session when the object is destroyed."""
        if hasattr(self, '_scraper') and self._scraper is not None:
            try:
                self._scraper.close()
            except:
                pass
