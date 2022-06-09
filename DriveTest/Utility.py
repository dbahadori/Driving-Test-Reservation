import logging
import os
import winsound
import csv
from csv import reader
import sys


from selenium.webdriver.common.by import By


class Logger:
    formatter = logging.Formatter('%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s')

    @staticmethod
    def setup_logger(name, log_file, level=logging.INFO):
        """To setup as many loggers as you want"""

        handler = logging.FileHandler(log_file)
        handler.setFormatter(Logger.formatter)

        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)

        return logger


class Switcher:

    @classmethod
    def element_finding_method(cls, method):
        __switcher = {
            'XPATH': "find_element_by_xpath",
            'By_CSS_ID': "find_element_by_id",
            'By_CSS_CLASS': "find_element_by_class_name",
            'BY_NAME': 'find_element_by_name',
            'BY_LINK': 'find_element_by_link_text',
            'BY_PARTIAL_LINK': 'find_element_by_partial_link_text',
            'BY_HTML_TAG': 'find_element_by_tag_name'
        }
        func = __switcher.get(method, "nothing")
        return func

    @classmethod
    def elements_finding_method(cls, method):
        __switcher = {
            'XPATH': "find_elements_by_xpath",
            'By_CSS_ID': "find_elements_by_id",
            'By_CSS_CLASS': "find_elements_by_class_name",
            'BY_NAME': 'find_elements_by_name',
            'BY_LINK': 'find_elements_by_link_text',
            'BY_PARTIAL_LINK': 'find_elements_by_partial_link_text',
            'BY_HTML_TAG': 'find_elements_by_tag_name'
        }
        func = __switcher.get(method, "nothing")
        return func

    @classmethod
    def element_finding_method_by(cls, method, value):
        __methods = {
            'XPATH': ('xpath', value),
            'By_CSS_ID': (By.ID, value),
            'By_CSS_CLASS': ('class name', value),
            'BY_NAME': ('name', value),
            'BY_LINK': ('link text', value),
            'BY_PARTIAL_LINK': ('partial link text', value),
            'BY_HTML_TAG': ('tag name', value),
            'By_CSS_SELECTOR': ('css selector', value)
        }
        return __methods.get(method, "nothing")


class Alarm:

    @staticmethod
    def play(filename):
        try:
            stop = False
            while not stop:
                stop = True
                os.system("start " + filename + ".mp3")
        except FileNotFoundError:
            print("Wrong file or file path")


class FileManager:

    # read csv file as a list
    @staticmethod
    def get_csv_params(file_path, separator):
        with open(file_path + '.csv', 'r') as read_file:
            # pass the file object to reader() to get the reader object
            params = read_file.read().replace('\n', '').split(separator)
        return params

    @staticmethod
    def insert_csv_params(file_path, new_params, separate):
        params = FileManager.get_csv_params(file_path, separate)
        for new_param in new_params:
            if new_param not in params:
                params.append(new_param)
        with open(file_path + '.csv', mode='w') as write_file:
            params_writer = csv.writer(write_file, delimiter=separate)
            params_writer.writerow(params)

    def resource_path(relative):
        # print(os.environ)
        application_path = os.path.abspath(".")
        if getattr(sys, 'frozen', False):
            # If the application is run as a bundle, the pyInstaller bootloader
            # extends the sys module by a flag frozen=True and sets the app
            # path into variable _MEIPASS'.
            application_path = sys._MEIPASS
        # print(application_path)
        return os.path.join(application_path, relative)
