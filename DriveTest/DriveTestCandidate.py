

class DriveTestCandidate:

    def __init__(self, name="name", family="family", interval_day=15, licence_number=None, licence_expiry=None,
                 location=None, driver_type='NEW_TEST', road_test_class='G'):
        self._licence_number = licence_number
        self._licence_expiry = licence_expiry
        self.name = name
        self.family = family
        self.interval_day = interval_day
        self.location = location
        self.driver_type = driver_type
        self.road_test_class = road_test_class
        
    @property
    def licence_number(self):
        return self._licence_number

    @licence_number.setter
    def licence_number(self, new_licence_number):
        self._licence_number = new_licence_number

    @property
    def licence_expiry(self):
        return self._licence_expiry

    @licence_expiry.setter
    def licence_expiry(self, new_licence_expiry):
        self._licence_expiry = new_licence_expiry

