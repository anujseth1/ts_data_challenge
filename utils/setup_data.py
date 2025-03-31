import pandas as pd
import os

# Load Excel
source_file = "data/CaseStudy_Role_SA.xlsx"
xl = pd.ExcelFile(source_file)

# Load raw sheets
sales_df = xl.parse("f_sales")
inventory_df = xl.parse("f_inventory")
product_df = xl.parse("d_products")
date_df = xl.parse("d_date")

# ----------------------------
# d_products (Dimension Table)
# ----------------------------
d_products = product_df.drop_duplicates().copy()
d_products = d_products.sort_values("product_id")
d_products.to_csv("data/d_products.csv", index=False)

# ------------------------
# d_date (Dimension Table)
# ------------------------
d_date = date_df.drop_duplicates().copy()
d_date = d_date.sort_values("date_id")
d_date.to_csv("data/d_date.csv", index=False)

# ---------------------
# f_sales (Fact Table)
# ---------------------
f_sales = sales_df[["product_id", "date_id", "quantity_sold"]].copy()
f_sales = f_sales.sort_values(by=["date_id", "product_id"])
f_sales.to_csv("data/f_sales.csv", index=False)

# -------------------------
# f_inventory (Fact Table)
# -------------------------
f_inventory = inventory_df[["product_id", "date_id", "quantity_purchased"]].copy()
f_inventory = f_inventory.sort_values(by=["date_id", "product_id"])
f_inventory.to_csv("data/f_inventory.csv", index=False)

print("✅ ERD-based tables saved as CSV in /data folder.")