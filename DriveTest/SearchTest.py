from selenium.webdriver.common.by import By

from DriveTest.WebScraper import WebScraper


class Test:
    def __init__(self, web_driver=None):
        self.scraper = web_driver

    def set_web_driver(self, web_driver):
        self.scraper = web_driver
    def search(self, search):
        self.scraper.get_page("http://www.google.com/")
        # googling search keyword
        element = self.scraper.set_text(value=search, focused_element_locator='q', setting_method='JAVA_SCRIPT',
                                        focused_locating_method='BY_NAME')
        element.submit()


        # get result from google search and return it as array
        result = self.scraper.find_elements(focused_element_locator="//*[@id='rso']//h3/span",
                                            waiting_element_locator=(By.ID, "res"))
        return result
