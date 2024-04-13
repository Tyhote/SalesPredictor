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


cust_columns = ["ID", "Experience", "Starting Cash", "Spending Cash", "Categories"]
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


class CategoryGenerator:
    __generatortype__ = DataGeneratorType.CATEGORY
    MAX_CATEGORIES = 100
    MIN_CATEGORIES = 10

    # Suspiciously simple. This init is complete.
    def __init__(self, categories, avg_intensity):
        self.df = pd.DataFrame(columns=category_columns)
        self.df['Category ID'] = pd.Series([i for i in range(1, categories + 1)])
        self.df['Intensity'] = pd.Series(np.random.normal(loc=avg_intensity))


class CustomerGenerator:
    __generatortype__ = DataGeneratorType.CUSTOMER

    MAX_ROWS = 2000
    MIN_ROWS = 10
    MAX_SPENDING_CASH = 2000
    MIN_SPENDING_CASH = 5
    SCALE = 0.114

    def __init__(self, categories: CategoryGenerator, customers, avg_cash, min_cash, max_cash, average_experience,
                 perc_low, perc_avg, perc_high):
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

        rng = np.random.default_rng()
        # Generate that number of customer uuids
        uuids = pd.Series([i for i in range(0, customers)])
        # And starting cashes
        low = rng.normal(loc=min_cash, scale=min_cash / 4, size=n_low).tolist()
        avg = rng.normal(loc=avg_cash, scale=avg_cash / 4, size=n_avg).tolist()
        high = rng.normal(loc=max_cash, scale=max_cash / 4, size=n_high).tolist()
        cashes = pd.Series(np.append(low, [avg, high]))
        # As well as starting experience level
        experiences = pd.Series(
            rng.normal(loc=average_experience, scale=CustomerGenerator.SCALE, size=customers))

        # Now we give them "interests"
        # noinspection PyTypeChecker
        ints_per_each: list = rng.integers(low=1, high=21, size=customers)
        interests = []
        num_categories = categories.df.shape[0]
        for customer in range(0, customers):
            interests[customer] = rng.integers(low=0, high=num_categories + 1, size=ints_per_each[customer])
        interests = pd.Series()

        # Then add the values to our DataFrame
        self.df['Customer ID'] = uuids
        self.df['Experience'] = experiences
        self.df['Starting Cash'] = cashes
        self.df['Spending Cash'] = cashes
        self.df["Categories"] = interests


prod_columns = ["Item ID", "Wholesale Price", "Retail Price", "Num in Inventory", "Total Sold", "Current Discount",
                "Expiration Date", "Categories"]


class ProductsGenerator:
    __generatortype__ = DataGeneratorType.PRODUCTS
    MAX_ROWS = 20000
    MIN_ROWS = 10
    MAX_PRICE = 500
    MIN_PRICE = 1
    MAX_CATEGORIES = 100
    MAX_WHOLESALE = 100
    MARKUP = 4
    MAX_INVENTORY = 10

    def __init__(self, products: int, categories: CategoryGenerator,
                 min_price: float,
                 avg_price: float,
                 max_price: float,
                 perc_low,
                 perc_avg,
                 perc_high):
        rng = np.random.default_rng()
        # Validate the requested price ranges
        if not min_price < avg_price < max_price:
            raise ValueError("Invalid Price Range")
        # As well as the distribution percentages
        if not perc_low + perc_avg + perc_high == 1.0:
            raise ValueError("Invalid Price Distribution")
        # Compress the requested row count
        products = compress_int(products, ProductsGenerator.MIN_ROWS, ProductsGenerator.MAX_ROWS)
        # And the prices requested
        min_price = compress_int(min_price, ProductsGenerator.MIN_PRICE, avg_price)
        max_price = compress_int(max_price, avg_price, ProductsGenerator.MAX_PRICE)
        # Create the DataFrame needed
        self.df = pd.DataFrame(columns=prod_columns)
        # Then generate the product uuids
        uuids = pd.Series([i for i in range(0, products)])
        # And the wholesale prices
        wholesale = pd.Series(rng.integers(low=min_price, high=max_price, size=products))
        # Multiply by the markup to get retail price
        retail = wholesale * ProductsGenerator.MARKUP
        # Randomly generate inventory numbers
        inventory = pd.Series(rng.integers(low=1, high=ProductsGenerator.MAX_INVENTORY, size=products))
        # Set sales to 0
        sales = pd.Series(np.zeros(products))
        # Giving ten percent of items a 25% or 50% discount
        # noinspection PyTypeChecker
        discounts = pd.Series([rng.choice([.25, .50]) for i in rng.random(size=products) if i < 0.1])
        # Give expiration date in timestamp one to two years from now
        year_secs = 31536000
        expirations = ((pd.Series(rng.random(size=products)) + 1) * year_secs) + datetime.datetime.now().timestamp()
        # Select some categories for each product, 1-3
        cats = [rng.choice(categories.df.shape[0] + 1, size=i) for i in
                pd.Series(rng.integers(low=1, high=4, size=products))]
        # Now we have to assign each field to its respective column in the dataframe
        self.df["Item ID"] = uuids
        self.df["Wholesale Price"] = wholesale
        self.df["Retail Price"] = retail
        self.df["Num in Inventory"] = inventory
        self.df["Total Sold"] = sales
        self.df["Current Discount"] = discounts
        self.df["Expiration Date"] = expirations
        self.df["Categories"] = cats


sale_columns = ["Timestamp", "Item(s)", "Wholesale Price(s)", "Retail Price(s)", "Discount(s)", "Number Sold(each)",
                "Expiration Date(s)"]


class SalesDataGenerator:
    __generatortype__ = DataGeneratorType.SALES
    MAX_ROWS = 2000000
    MIN_ROWS = 100
    MAX_ITEMS = 5
    MIN_ITEMS = 1

    def __init__(self, rows, avg_interval, products: ProductsGenerator, customers: CustomerGenerator, timestamp=None):

        if timestamp is None:
            # Setting timestamp to current time if none given
            self.begin = datetime.datetime.now().timestamp()
        else:
            # Checking if within 1970-2038 (Epochalypse)
            if not isinstance(timestamp, int) or not (-1 < timestamp < 2145938400):
                # Set beginning to current time
                self.begin = datetime.datetime.now()
            else:
                # All checks succeeded, so use the timestamp value
                self.begin = datetime.datetime.fromtimestamp(timestamp)
        # Set current time to beginning time, so we can simulate from that point
        self.current = self.begin

        # Check if rows arg is inbounds, compress to min or max if not
        if rows < SalesDataGenerator.MIN_ROWS:
            self.rows = SalesDataGenerator.MIN_ROWS
        elif rows > SalesDataGenerator.MAX_ROWS:
            self.rows = SalesDataGenerator.MAX_ROWS

        # Create a DataFrame based on the columns given by the template
        data = pd.DataFrame(columns=sale_columns)

        rng = np.random.default_rng()
        # Start "simulation"
        timestamp = []
        n_products = products.df.shape[0]
        n_customers = customers.df.shape[0]
        for row in range(0, rows):
            # Randomly select which customer to use
            customer = customers.df["ID"][rng.choice(n_customers + 1)]
            # Incrementing the time by a normally random distribution from [~0,  avg_interval, ~avg_interval * 2]
            self.current += np.floor(rng.normal(loc=avg_interval, scale=avg_interval / 4))
            #   and recording that time as the time of purchase
            timestamp[row] = self.current
