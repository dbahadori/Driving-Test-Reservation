from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.opera import OperaDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.microsoft import IEDriverManager
import logging
import time
from DriveTest.Utility import Switcher


class BadMethod(Exception):
    pass



class WebScraper:
    technical_logger = logging.getLogger('Technical')
    business_logger = logging.getLogger('Business')

    def __init__(self, driver_path, driver_type="CHROME"):

        if driver_type.upper() == "CHROME":
            chrome_opt = webdriver.ChromeOptions()
            chrome_opt.headless = False
            self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_opt)

        elif driver_type.upper() == "IE":
            ie_opt = webdriver.IeOptions()
            ie_opt.ignore_zoom_level = True
            self.driver = webdriver.Ie(IEDriverManager().install(), options=ie_opt)

        elif driver_type.upper() == "FIREFOX":
            fire_opt = webdriver.FirefoxOptions()
            fire_opt.ignore_zoom_level = True
            fire_opt.headless = False
            self.driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=fire_opt)

        elif driver_type.upper() == "EDGE":
            self.driver = webdriver.Edge(EdgeChromiumDriverManager().install())

        elif driver_type.upper() == "EDGE_LEGACY":
            self.driver = webdriver.Edge(EdgeChromiumDriverManager().install())

        elif driver_type.upper() == "OPERA":
            self.driver = webdriver.Opera(executable_path=OperaDriverManager().install())

    def quit_driver(self):
        self.driver.quit()

    def get_page(self, address):
        return self.driver.get(address)

    def find_elements(self, focused_element_locator, waiting_element_locator=None, waiting_time=20,
                     focused_locating_method='XPATH', log_description=None):
        try:
            self.check_waiting_locator(focused_element_locator=focused_element_locator,
                                       focused_locating_method=focused_locating_method,
                                       waiting_element_locator=waiting_element_locator,
                                       waiting_time=waiting_time)

            find_element_method = Switcher.elements_finding_method(focused_locating_method)
            func = getattr(self.driver, find_element_method)
            focused_elements = func(focused_element_locator)
        except Exception as be:
            WebScraper.technical_logger.error("Exception occurred", exc_info=True)
        else:
            if log_description is None:
                log_description = 'the element ' + focused_element_locator + ' is found'
            WebScraper.technical_logger.info(log_description)
            return focused_elements

    def find_element(self, focused_element_locator, waiting_element_locator=None, waiting_time=20,
                     focused_locating_method='XPATH', log_description=None):
        try:
            self.check_waiting_locator(focused_element_locator=focused_element_locator,
                                       focused_locating_method=focused_locating_method,
                                       waiting_element_locator=waiting_element_locator,
                                       waiting_time=waiting_time)

            find_element_method = Switcher.element_finding_method(focused_locating_method)
            func = getattr(self.driver, find_element_method)
            focused_element = func(focused_element_locator)
        except Exception as be:
            WebScraper.technical_logger.error("Exception occurred", exc_info=True)
        else:
            if log_description is None:
                log_description = 'the element ' + focused_element_locator + ' is found'
            WebScraper.technical_logger.info(log_description)
            return focused_element

    def click_element(self, focused_element_locator, waiting_element_locator=None, waiting_time=20,
                      focused_locating_method='XPATH', clicking_method='SELENIUM', log_description=None):
        try:
            time.sleep(5)
            focused_element = self.find_element(focused_element_locator, waiting_element_locator, waiting_time,
                                                focused_locating_method, log_description)

            if clicking_method.lower() == 'SELENIUM'.lower():
                focused_element.click()
            elif clicking_method.lower() == 'JAVA_SCRIPT'.lower():
                self.click_by_java_script(focused_element, log_description)
            else:
                raise BadMethod("bad setting method for " + focused_element_locator + "element")
        except BadMethod as bsm:
            log_description = bsm
            WebScraper.technical_logger.error(log_description)
        except BaseException as be:
            log_description = be
            WebScraper.technical_logger.error(log_description)
        else:
            if log_description is None:
                log_description = "the element " + focused_element_locator + " is clicked"
                WebScraper.technical_logger.info(log_description)
                return focused_element

    def submit_form(self, form_name=None, form_id=None, submit_method='SELENIUM', log_description=None):
        try:
            if form_id is not None:
                form = self.find_element(focused_element_locator="//form[@id='" + form_id + "']",
                                          waiting_element_locator=(By.XPATH, "//form[@id='" + form_id + "']"))
            elif form_name is not None:
                form = self.find_element(focused_element_locator="//form[@name='" + form_name + "']",
                                          waiting_element_locator=(By.XPATH, "//form[@name='" + form_name + "']"))
            else:
                raise BadMethod("id or name for form is not specified ")

            if submit_method.lower() == 'SELENIUM'.lower():
                time.sleep(5)
                form.submit()
            elif submit_method.lower() == 'JAVA_SCRIPT'.lower():
                # not implemented
                raise BadMethod("JAVA_SCRIPT method for form submit is not implemented")
            else:
                raise BadMethod("bad submit method for " + form + " element")
        except BadMethod as bsm:
            log_description = bsm
            WebScraper.technical_logger.error(log_description)
        except BaseException as be:
            log_description = be
            WebScraper.technical_logger.error(log_description)
        else:
            if log_description is None:
                log_description = "the form with id = " + form.get_attribute('name') + " is submitted"
                WebScraper.technical_logger.info(log_description)
                return form

    def set_text(self, value, focused_element_locator, waiting_element_locator=None, waiting_time=10,
                 focused_locating_method='XPATH', setting_method='SELENIUM', log_description=None):
        try:
            focused_element = self.find_element(focused_element_locator, waiting_element_locator, waiting_time,
                                                focused_locating_method, log_description)
            if setting_method.lower() == 'SELENIUM'.lower():
                focused_element.text = value
            else:
                if setting_method.lower() == 'JAVA_SCRIPT'.lower():
                    focused_element = self.set_value_by_java_script(focused_element, value, log_description)
                    #time.sleep(5)
                    #focused_element.click()
                else:
                    raise BadMethod("bad setting method for " + focused_element + " element")
        except BadMethod as bsm:
            log_description = bsm
            WebScraper.technical_logger.error(log_description)
        except BaseException as be:
            log_description = be
            WebScraper.technical_logger.error(log_description)
        else:
            if log_description is None:
                log_description = "the text of " + focused_element_locator + " element set as " + value
                WebScraper.technical_logger.info(log_description)
            return focused_element

    @staticmethod
    def element_class_checker(element, checker_class):
        element_class = element.get_attribute("class")
        if element_class == checker_class:
            return True
        else:
            return False

    def click_by_java_script(self, element, log_description=None):
        self.driver.execute_script("arguments[0].click();", element)
        if log_description is None:
            log_description = 'the element is clicked'
        return element

    def set_value_by_java_script(self, element, value, log_description=None):
        self.driver.execute_script("arguments[0].value='" + value + "';", element)
        if log_description is None:
            log_description = 'the value of  element is set to ' + value
        return element

    def check_waiting_locator(self, focused_element_locator, focused_locating_method, waiting_element_locator, waiting_time):
        if waiting_element_locator is not None:
            return WebDriverWait(self.driver, waiting_time).until(
                EC.presence_of_element_located(waiting_element_locator)
            )
        else:
            waite_element_method = Switcher.element_finding_method_by(focused_locating_method,
                                                                      focused_element_locator)
            return WebDriverWait(self.driver, waiting_time).until(
                EC.presence_of_element_located(waite_element_method)
            )