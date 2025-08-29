import logging
import ast
from datetime import datetime, timedelta
import anatools.lib.context as ctx
from anatools.lib.node import Node

logger = logging.getLogger(__name__)


class Datetime(Node):
    """ """

    def exec(self):
        logger.info("Executing {}".format(self.name))

        year = int(self.inputs["Year"][0]) % 10000
        month = int(self.inputs["Month"][0]) % 13
        day = int(self.inputs["Day"][0]) % 10000
        hour = int(self.inputs["Hour"][0]) % 24
        minute = int(self.inputs["Minute"][0]) % 60

        # Not all months have 31 days and that is the value I let users
        # go up to. So if this month doesn't have enough days then
        # subtract days by 1 and try again.
        failed = True
        while failed:
            try:
                x = datetime(year, month, day, hour, minute, 0)
                x = x.replace(tzinfo=None)
                failed = False
            except:
                day = day - 1

        logger.info("Current date and time: {}".format(x))

        return {"Datetime": x}