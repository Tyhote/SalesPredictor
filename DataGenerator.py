# Local Imports
import pandas as pd

# Builtin Imports
import datetime


class DataGenerator:
    MAX_ROWS = 2000000
    MIN_ROWS = 100
    def __init__(self, rows, timestamp=None):
        if timestamp is None:
            # Setting timestamp to current time if none given
            self.begin = datetime.datetime.now()
        else:
            # Checking if within 1970-2038 (Epochalypse)
            if not isinstance(timestamp, int) or not (-1 < timestamp < 2145938400):
                # Set to current time
                self.begin = datetime.datetime.now()
            else:
                # All checks succeeded, so use the timestamp value
                self.begin = datetime.datetime.fromtimestamp(timestamp)

        # Check if rows arg is inbounds, compress to min or max if not
        if rows < DataGenerator.MIN_ROWS:
            self.rows = DataGenerator.MIN_ROWS
        elif rows > DataGenerator.MAX_ROWS:
            self.rows = DataGenerator.MAX_ROWS

        # Now is where the real fun begins
        #
