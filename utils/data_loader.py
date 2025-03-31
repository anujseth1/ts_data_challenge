import pandas as pd

def load_data():
    sales = pd.read_csv("data/f_sales.csv")
    inventory = pd.read_csv("data/f_inventory.csv")
    product = pd.read_csv("data/d_products.csv")
    date = pd.read_csv("data/d_date.csv")
    return sales, inventory, product, date

def merge_dimensions(f_sales, f_inventory, d_products, d_date):
    sales_df = f_sales.merge(d_products, on="product_id", how="left").merge(d_date, on="date_id", how="left")
    inventory_df = f_inventory.merge(d_products, on="product_id", how="left").merge(d_date, on="date_id", how="left")

    sales_df["date"] = pd.to_datetime(sales_df["date"])
    inventory_df["date"] = pd.to_datetime(inventory_df["date"])

    return sales_df, inventory_df
