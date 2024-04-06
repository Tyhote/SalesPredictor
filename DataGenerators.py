# Local Imports
import pandas as pd

# Builtin Imports
import datetime
from enum import Enum


class DataGeneratorType(Enum):
    SALES = 1
    PRODUCTS = 2
    CUSTOMER = 3

# DataGenerator class, needs a __generatortype__


class DataGenerators:

    @staticmethod
    def compress_int(number, min_n, max_n):
        if isinstance(number,int):
            if number < min_n:
                return min_n
            elif number > max_n:
                return max_n
            else:
                return number
        else:
            return (min_n + max_n)/2
    class CustomerGenerator:
        __generatortype__ = DataGeneratorType.CUSTOMER
        MAX_ROWS = 2000
        MIN_ROWS = 10

    class ProductsGenerator:
        __generatortype__ = DataGeneratorType.PRODUCTS
        MAX_ROWS = 20000
        MIN_ROWS = 10

        def __init__(self, rows: int, max_price: float, min_price: float):
            pass

    class SalesGenerator:
        __generatortype__ = DataGeneratorType.SALES
        MAX_ROWS = 2000000
        MIN_ROWS = 100

        def __init__(self, rows, timestamp=None):

            def read_template(name):
                file = open(name, "r")
                columns = file.readline().strip().split(",")
                file.close()
                return columns

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
            if rows < DataGenerators.MIN_ROWS:
                self.rows = DataGenerators.MIN_ROWS
            elif rows > DataGenerators.MAX_ROWS:
                self.rows = DataGenerators.MAX_ROWS

            # Checking type and calling the appropriate function
            template = []
            match self.GEN_TYPE:

                case DataGenerators.DataGeneratorType.SALES:
                    template = read_template("RetailSalesGeneratorTemplate.csv")

                case DataGenerators.DataGeneratorType.PRODUCTS:
                    template = read_template("RetailProductsGeneratorTemplate.csv")

            # Create a DataFrame based on the columns given by the template
            data = pd.DataFrame(columns=template)
