from DriveTest.WebScraper import WebScraper
from DriveTest.TimeManager import TimeManager
from DriveTest.DriveTestCandidate import DriveTestCandidate
from selenium.webdriver.common.by import By

import time


class RoadTestService:
    def __init__(self, web_driver=None, web_address=None,
                 candidate=DriveTestCandidate()):

        self.scraper = web_driver
        self.web_address = web_address
        self.candidate = candidate

    def set_web_driver(self, web_driver):
        self.scraper = web_driver

    def get_drive_test_home_page(self):
        return self.scraper.get_page(self.web_address)

    def start_drive_road_test(self):
        self.scraper.get_page(self.web_address)
        # click drive road test button
        return self.scraper.click_element(focused_element_locator="//*[@class='btn btn-primary btn-main' and"
                                                                  " contains(text(), 'Book a Road test')]")

    def edit_existing_road_test_step(self):
        # click edit an existing road test
        return self.scraper.click_element(focused_element_locator="//a[contains(text(), 'Edit an Existing Road Test')]",
                                          waiting_element_locator=(By.ID, "emailAddress"))

    def send_licence_info_step(self):
        time.sleep(2)
        licence_element = self.scraper.set_text(value=self.candidate.licence_number,
                              focused_element_locator="//input[@type='text' and @id='licenceNumber']", setting_method="JAVA_SCRIPT")
        time.sleep(2)
        expiry_element = self.scraper.set_text(value=self.candidate.licence_expiry,
                              focused_element_locator="//input[@type='text' and @id='licenceExpiryDate']", setting_method="JAVA_SCRIPT")
        time.sleep(2)
        licence_element.click()
        expiry_element.click()
        licence_element.click()
        time.sleep(2)
        self.scraper.submit_form(form_name="driverInfo")

    def new_road_test_step(self):
        return self.scraper.click_element(focused_element_locator="//*[contains(text(),"
                                                                  "'Book a New Road Test')]",
                                          waiting_element_locator=(By.XPATH, "//*[contains(text(),"
                                                                             "'You have no booked road"
                                                                             " tests at this time')]"))

    def reschedule_test_step(self):
        self.scraper.click_element(focused_element_locator="//button[contains(text(), 'Reschedule')]")
        popup_element = self.scraper.click_element(focused_element_locator="//div[@class='form-group lic-submit']/button[@title='reschedule']")
        return popup_element

    def select_test_class_step(self):
        # select class of road test
        self.scraper.click_element(focused_element_locator="//input[@type='radio' "
                                                           "and @value='" + self.candidate.road_test_class + "']",
                                   waiting_element_locator=(By.XPATH, "//input[@type='radio' and "
                                                                      "@value='" + self.candidate.road_test_class + "']"),
                                   clicking_method="JAVA_SCRIPT")
        result = self.scraper.submit_form(form_name='driverInfo')
        return result

    def select_location_step(self):
        self.scraper.click_element(focused_element_locator="//a[@title='" + self.candidate.location + "']")
        result = self.scraper.submit_form(form_name="locationInfo")
        return result

    def select_available_date_step(self):
        date_selectable_class = "date-link"
        date_selected_class = "date-link selected"
        selected_day = None
        selected_month = None
        is_date_selected = False
        is_day_acceptable = False
        max_next_month = TimeManager.next_acceptable_month_count(self.candidate.interval_day)
        next_month_count = 1
        previous_month_count = max_next_month
        result = None
        # selectable_date_elements = []
        # calendar_month = 0
        while not is_date_selected:
            selectable_date_elements = self.scraper.find_elements(focused_element_locator="//a[@class='"
                                                                                          + date_selectable_class + "']",
                                                                  waiting_element_locator=(By.XPATH, "//div[@class="
                                                                                                     "'calendar-body']"),
                                                                  waiting_time=20)
            calendar_month = self.scraper.find_element(focused_element_locator="//*[@class='calendar-header']/h3")
            if len(selectable_date_elements) > 0:
                print("there is some dates available to select")
                for date_element in selectable_date_elements:
                    candidate_day = int(date_element.get_attribute("title"))
                    print("candidate day is :", candidate_day)
                    if next_month_count == 1:
                        if candidate_day >= TimeManager.today:
                            is_day_acceptable = True
                    elif next_month_count == max_next_month:
                        if candidate_day <= TimeManager.max_acceptable_day(self.candidate.interval_day):
                            is_day_acceptable = True
                    else:
                        is_day_acceptable = True
                    if is_day_acceptable and WebScraper.element_class_checker(date_element,
                                                                              date_selectable_class):
                        self.scraper.click_by_java_script(element=date_element)
                        if WebScraper.element_class_checker(date_element, date_selected_class):
                            selected_day = candidate_day
                            selected_month = calendar_month.text
                            is_date_selected = True
                            print("one date is selected : " + str(selected_month) + " " + str(selected_day))
                            break

            else:
                if next_month_count <= max_next_month:
                    self.nex_month_step()
                    next_month_count += 1

                elif previous_month_count >= 1:
                    self.previous_month_step()
                    previous_month_count -= 1
                else:
                    next_month_count = 1
                    previous_month_count = max_next_month
            if not is_date_selected:
                print("waiting to load data of another month...")
                time.sleep(1)
        if is_date_selected:
            result = self.scraper.submit_form(form_name="driverInfo")
        else:
            print("date is not selected")
        return is_date_selected, result

    def select_available_time_step(self):
        time_selectable_class = "timeslot_label ng-binding"
        time_selected_class = "timeslot_label ng-binding active"
        selected_time = None
        is_time_selected = False
        result = None
        selectable_time_elements = self.scraper.find_elements(focused_element_locator="//label[@class='"
                                                                                      + time_selectable_class + "']")
        if len(selectable_time_elements) > 0:
            print("there is some times available to select")
            available_times = [t.get_attribute("for") for t in selectable_time_elements]
            print("available times are :", available_times)
            for time_element in selectable_time_elements:
                candidate_time = time_element.get_attribute("for")
                print("candidate time is :", candidate_time)
                if self.scraper.element_class_checker(time_element, time_selectable_class):
                    self.scraper.click_by_java_script(element=time_element)
                    if self.scraper.element_class_checker(time_element, time_selected_class):
                        selected_time = candidate_time
                        is_time_selected = True
                        print("one time is selected : " + str(selected_time))
                        break
        else:
            print("there are not any available times ")
        if is_time_selected:
            result = self.scraper.submit_form(form_id="timeslot-form")
        return is_time_selected

    def nex_month_step(self):
        # go to the next month to find an available date
        print("clicking on next month...")
        self.scraper.click_element(focused_element_locator="//*[@class='calendar-header']/a[@title='next month']",
                                   clicking_method="JAVA_SCRIPT")

    def previous_month_step(self):
        # go to the previous month to find an available date
        print("clicking on previous month...")
        self.scraper.click_element(focused_element_locator="//*[@class='calendar-header']/a[@title='previous month']",
                                   clicking_method="JAVA_SCRIPT")