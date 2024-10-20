import os
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

class WebDriverCreator():

    SHARED_MEM_PATH = "/dev/shm"

    @staticmethod
    def create_webdriver(headless: bool = True) -> WebDriver: 
        """
        Creates an interoperable WebDriver. Method assumes 
        a Chrome installation existing on the system.
        ----------
        headless : bool
            If set to True browser will not open and run 
            headless. In case method is run in docker this 
            should be set to True (note, the default is 
            already True).
        """
        options = Options()
        
        # standard way of setting selenium to headless mode is
        # options.headless = True
        # however, this currently performs worse against bot detection
        # therefore we set it like this:
        if headless:
            options.add_argument("--headless=new")
        # avoid unneeded logs on windows systems
        options.add_argument("--log-level=3")
        # https://bugs.chromium.org/p/chromedriver/issues/detail?id=2907#c3
        # '--no-sandbox' is needed to run in linux without root 
        options.add_argument("--no-sandbox")
        # avoid to download images
        options.add_argument('--blink-settings=imagesEnabled=false')
        # waits for document to be in a specific state
        # is default is 'normal' which equals
        # <code>document.readyState == 'complete'</code>
        # more details see W3C https://w3c.github.io/webdriver/#navigation
        options.page_load_strategy = 'eager'
        # Webdriver sometimes breaks due to the limited size of the shared memory in docker.
        # The following lines check the actual size of the shared memory in POSIX systems.
        # If it is to small we will use the "tmp" folder instead.
        # This will have a negative impact on performance.
        # Docker comes with a default size of 64 MB, this however can be changed.
        # (for more details refer to https://datawookie.dev/blog/2021/11/shared-memory-docker/)
        if os.path.exists(WebDriverCreator.SHARED_MEM_PATH):
            file_system_size = os.statvfs("/dev/shm")
            size_in_kb = file_system_size.f_frsize * file_system_size.f_blocks
            # check if size of shared memory is < 512
            if size_in_kb < 512 * (1024 * 1024):
                options.add_argument('--disable-dev-shm-usage')
        # After ChromeDriver 177 a DevToolsActivePorts created on 4533 which 
        # creates issues in Docker. Therefore the port is deactivated.
        # (for more details refer to https://bugs.chromium.org/p/chromedriver/issues/detail?id=4403#c35)
        options.add_argument('--remote-debugging-pipe')
        # Disable the gpu as it is most likely not running attached to the docker container
        options.add_argument("--disable-gpu")
        
        return webdriver.Chrome(options=options, service=WebDriverCreator.create_service())
    
    @staticmethod
    def create_service() -> Service:
        result = Service()

        # check if we are on windows
        if os.name == 'nt':
            # fix to ensure we do not get unnecessary log output like this:
            # "DevTools listening on ws://127.0.0.1:61165/devtools/browser/1cd3c683-bfac-4cb4-89e9-bf0cb3e3c4e9"
            # https://stackoverflow.com/a/71093078
            from subprocess import CREATE_NO_WINDOW
            result.creation_flags = CREATE_NO_WINDOW
        
        return result    
