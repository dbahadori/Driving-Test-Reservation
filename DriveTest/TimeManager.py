import time
import datetime


class TimeManager:
    __current_date = datetime.datetime.today()
    today = __current_date.day
    month = __current_date.month
    year = __current_date.year

    @staticmethod
    def next_acceptable_month_count(interval_day):
        if interval_day <= 30:
            return 1
        elif (interval_day % 30) is not 0:
            return int((interval_day / 30) + 1)
        else:
            return int(interval_day / 30)

    @staticmethod
    def max_acceptable_day(interval_day):
        date_delta = TimeManager.__current_date + datetime.timedelta(days=interval_day)
        return date_delta.day
