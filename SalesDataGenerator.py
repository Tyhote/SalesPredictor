# Local Imports
import pandas as pd
import numpy as np

# Builtin Imports
import datetime
from enum import Enum


class DataGeneratorType(Enum):
    SALES = 1
    PRODUCTS = 2
    CUSTOMER = 3
    CATEGORY = 4


# DataGenerator class, needs a __generatortype__

def read_template(name):
    with open(name, "r") as file:
        columns = file.readline().strip().split(",")
        return columns


prod_columns = ["Item ID", "Wholesale Price", "Retail Price", "Num in Inventory", "Total Sold", "Current Discount",
                "Expiration Date", "Category"]
cust_columns = ["Customer ID", "Experience", "Starting Cash", "Spending Cash"]
sale_columns = ["Item(s)", "Wholesale Price(s)", "Retail Price(s)", "Discount(s)", "Number Sold(each)", "Timestamp",
                "Expiration Date(s)"]
category_columns = ["Category ID", "Intensity"]


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
    SCALE = 0.114

    def __init__(self, customers, avg_cash, min_cash, max_cash, average_experience, perc_low, perc_avg, perc_high):
        # Validate the requested price distribution
        if not perc_low + perc_avg + perc_high == 1.0:
            raise ValueError("Invalid Cash Distribution")
        # As well as the customer's buying power
        if not min_cash < avg_cash < max_cash:
            raise ValueError("Invalid Cash Ranges")
        # Make the requested number of customers valid
        customers = compress_int(customers, CustomerGenerator.MIN_ROWS, CustomerGenerator.MAX_ROWS)
        # As well as the range of starting cash values
        min_cash = compress_int(min_cash, CustomerGenerator.MIN_ROWS, avg_cash)
        max_cash = compress_int(max_cash, avg_cash, CustomerGenerator.MAX_ROWS)
        # Make the dataframe
        self.df = pd.DataFrame(columns=cust_columns)
        # Get number of each type of customer
        n_low = np.floor(customers * perc_low)
        n_avg = np.floor(customers * perc_avg)
        n_high = np.floor(customers * perc_high)
        # Ensure the total number of customers remains the same
        tot = n_low + n_avg + n_high
        while tot != customers:
            if tot < customers:
                n_avg += 1
            else:
                n_avg -= 1
            tot = n_low + n_avg + n_high

        # Generate that number of customer uuids
        uuids = pd.Series([i for i in range(0, customers)])
        # And starting cashes
        low = np.random.normal(loc=min_cash, scale=min_cash / 2, size=n_low).tolist()
        avg = np.random.normal(loc=avg_cash, scale=avg_cash / 2, size=n_avg).tolist()
        high = np.random.normal(loc=max_cash, scale=max_cash / 2, size=n_high).tolist()
        cashes = pd.Series(np.append(low, [avg, high]))
        # As well as starting experience level
        experiences = pd.Series(
            np.random.normal(loc=average_experience, scale=CustomerGenerator.SCALE, size=customers))

        # Then add the values to our DataFrame
        self.df['Customer ID'] = uuids
        self.df['Experience'] = experiences
        self.df['Starting Cash'] = cashes
        self.df['Spending Cash'] = cashes


class ProductsGenerator:
    __generatortype__ = DataGeneratorType.PRODUCTS
    MAX_ROWS = 20000
    MIN_ROWS = 10
    MAX_PRICE = 500
    MIN_PRICE = 1
    MAX_CATEGORIES = 100

    def __init__(self, rows: int, categories: int, min_price: float, avg_price: float, max_price: float, perc_low,
                 perc_avg,
                 perc_high):
        # Validate the requested price ranges
        if not min_price < avg_price < max_price:
            raise ValueError("Invalid Price Range")
        # As well as the distribution percentages
        if not perc_low + perc_avg + perc_high == 1.0:
            raise ValueError("Invalid Price Distribution")
        # Compress the requested row count
        rows = compress_int(rows, ProductsGenerator.MIN_ROWS, ProductsGenerator.MAX_ROWS)
        # And the prices requested
        min_price = compress_int(min_price, ProductsGenerator.MIN_PRICE, avg_price)
        max_price = compress_int(max_price, avg_price, ProductsGenerator.MAX_PRICE)
        # Create the DataFrame needed
        self.df = pd.DataFrame(columns=prod_columns)
        # Then generate the product categories


class CategoryGenerator:
    __generatortype__ = DataGeneratorType.CATEGORY
    MAX_CATEGORIES = 100
    MIN_CATEGORIES = 10

    def __init__(self, categories, avg_intensity):
        self.df = pd.DataFrame(columns=category_columns)
        self.df['Category ID'] = pd.Series([i for i in range(1, categories + 1)])
        self.df['Intensity'] = pd.Series(np.random.normal(loc=avg_intensity))


class SalesDataGenerator:
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
        if rows < SalesDataGenerator.MIN_ROWS:
            self.rows = SalesDataGenerator.MIN_ROWS
        elif rows > SalesDataGenerator.MAX_ROWS:
            self.rows = SalesDataGenerator.MAX_ROWS

        # Create a DataFrame based on the columns given by the template
        data = pd.DataFrame(columns=sale_columns)
