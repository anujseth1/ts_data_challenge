import pandas as pd

def load_data():
    sales = pd.read_csv("data/f_sales.csv")
    inventory = pd.read_csv("data/f_inventory.csv")
    product = pd.read_csv("data/d_products.csv")
    date = pd.read_csv("data/d_date.csv")
    return sales, inventory, product, date

# def merge_dimensions(f_sales, f_inventory, d_products, d_date):
#     sales_df = f_sales.merge(d_products, on="product_id", how="left").merge(d_date, on="date_id", how="left")
#     inventory_df = f_inventory.merge(d_products, on="product_id", how="left").merge(d_date, on="date_id", how="left")

#     sales_df["date"] = pd.to_datetime(sales_df["date"])
#     inventory_df["date"] = pd.to_datetime(inventory_df["date"])

#     return sales_df, inventory_df

def merge_dimensions(f_sales, f_inventory, d_products, d_date):
    d_date["date"] = pd.to_datetime(d_date["date"])

    # Get all date-product combinations
    date_product_matrix = d_date.merge(d_products, how="cross")

    sales_df = date_product_matrix.merge(f_sales, on=["product_id", "date_id"], how="left")
    inventory_df = date_product_matrix.merge(f_inventory, on=["product_id", "date_id"], how="left")

    sales_df["quantity_sold"] = sales_df["quantity_sold"].fillna(0)
    inventory_df["quantity_purchased"] = inventory_df["quantity_purchased"].fillna(0)

    return sales_df, inventory_df
