from DriveTest.RoadTestService import RoadTestService
from DriveTest import SearchTest
from DriveTest.WebScraper import WebScraper


class Orchestrator:
    def __init__(self, driver_type):

        self.driver_type = driver_type
        self.driver = WebScraper(driver_type)
        self.road_test = RoadTestService()
        self.search_test = SearchTest.Test()

    def google_search(self, keyword):
        self.search_test.set_web_driver(self.driver)
        self.search_test.search(keyword)
        return True

    def continous_google_search(self, keyword):
        self.search_test.set_web_driver(self.driver)
        while True:
            self.search_test.search(keyword)

    def booking_road_test(self, drive_test_candidate):
        self.road_test.set_web_driver(self.driver)
        self.road_test.candidate = drive_test_candidate
        self.road_test.web_address = ""

        self.road_test.start_drive_road_test()

        self.road_test.edit_existing_road_test_step()

        self.road_test.send_licence_info_step()

        if self.road_test.candidate.driver_type == 'NEW_TEST':
            self.road_test.new_road_test_step()
            self.road_test.select_test_class_step()

        elif self.road_test.candidate.driver_type == 'RESCHEDULE':
            self.road_test.reschedule_test_step()
        self.road_test.select_location_step()
        self.road_test.select_available_date_step()
        return self.road_test.select_available_time_step()



