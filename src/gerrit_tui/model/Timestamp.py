from datetime import datetime
from dateutil import tz


class Timestamp:
    def __init__(self, ts):
        self.__ts = datetime.strptime(ts[0:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal())

    @property
    def native(self):
        return self.__ts

    @property
    def str(self):
        return self.__ts.strftime("%Y-%m-%d %H:%M")
