# Local Imports
import pandas as pd

# Builtin Imports
import datetime
import numpy as np
from enum import Enum

class DataGeneratorType(Enum):
    SALES = 1
    PRODUCTS = 2
    CUSTOMER = 3


# DataGenerator class, needs a __generatortype__


class DataGenerators:

    @staticmethod
    def read_template(name):
        file = open(name, "r")
        columns = file.readline().strip().split(",")
        file.close()
        return columns

    @staticmethod
    def compress_int(number, min_n, max_n):
        if isinstance(number, int):
            if number < min_n:
                return min_n
            elif number > max_n:
                return max_n
            else:
                return number
        else:
            return (min_n + max_n) / 2

    class CustomerGenerator:
        __generatortype__ = DataGeneratorType.CUSTOMER
        MAX_ROWS = 2000
        MIN_ROWS = 10
        MAX_SPENDING_CASH = 2000
        MIN_SPENDING_CASH = 5

        def __init__(self, number, avg_cash, min_cash, max_cash, average_experience, perc_low, perc_avg, perc_high):
            # Make the requested number of customers valid
            number = DataGenerators.compress_int(number, DataGenerators.CustomerGenerator.MIN_ROWS,
                                                 DataGenerators.CustomerGenerator.MAX_ROWS)
            # As well as the customer's buying power
            if not min_cash < avg_cash < max_cash:
                raise ValueError
            min_cash = DataGenerators.compress_int(min_cash, DataGenerators.CustomerGenerator.MIN_ROWS, avg_cash)
            max_cash = DataGenerators.compress_int(max_cash, avg_cash, DataGenerators.CustomerGenerator.MAX_ROWS)
            # Make the dataframe
            template = DataGenerators.read_template("RetailCustomersGeneratorTemplate.csv")
            self.df = pd.DataFrame(columns=template)
            # Get number of each type of customer
            n_low = np.floor(number * perc_low)
            n_avg = np.floor(number * perc_avg)
            n_high = np.floor(number * perc_high)
            # Ensure the total number of customers remains the same
            tot = n_low + n_avg + n_high
            while tot != number:
                if tot < number:
                    n_avg += 1
                else:
                    n_avg -= 1
                tot = n_low + n_avg + n_high

            # Generate that number of customer uuids
            uuids = pd.Series([i for i in range(0, number)])
            # And starting cashes
            low = np.random.normal(loc=min_cash, scale=min_cash/2, size=number).tolist()
            avg = np.random.normal(loc=avg_cash, scale=avg_cash/2, size=number).tolist()
            high = np.random.normal(loc=max_cash, scale=max_cash/2, size=number).tolist()
            cashes = pd.Series(np.append(low, [avg, high]))
            # As well as starting experience level
            experiences = pd.Series(np.random.normal(loc=0.5,scale=0.114, size=number))

            # Then add the values to our DataFrame
            self.df['Customer ID'] = uuids
            self.df['Experience'] = experiences
            self.df['Starting Cash'] = cashes
            self.df['Spending Cash'] = cashes

    class ProductsGenerator:
        __generatortype__ = DataGeneratorType.PRODUCTS
        MAX_ROWS = 20000
        MIN_ROWS = 10

        def __init__(self, rows: int, min_price: float, avg_price: float, max_price: float, perc_low, perc_avg,
                     perc_high):
            pass

    class SalesGenerator:
        __generatortype__ = DataGeneratorType.SALES
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
            if rows < DataGenerators.SalesGenerator.MIN_ROWS:
                self.rows = DataGenerators.SalesGenerator.MIN_ROWS
            elif rows > DataGenerators.SalesGenerator.MAX_ROWS:
                self.rows = DataGenerators.SalesGenerator.MAX_ROWS

            # Read the template from file
            template = DataGenerators.read_template("RetailSalesGeneratorTemplate.csv")
            # Create a DataFrame based on the columns given by the template
            data = pd.DataFrame(columns=template)
