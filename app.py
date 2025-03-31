import streamlit as st

st.set_page_config(layout="wide")

import pandas as pd
from utils.data_loader import load_data as raw_load_data, merge_dimensions

@st.cache_data
def load_data():
    return raw_load_data()

from pages import (
    revenue_trend,
    monthly_breakdown,
    food_nonholiday,
    product_threshold,
    cumulative_sales,
    cashflow_ratio,
    sales_inventory_page,
)

# st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align: center;'>🧠 ThoughtSpot Data Challenge Dashboard</h1>", unsafe_allow_html=True)

# -------------------------
# Load & Prepare Data
# -------------------------
f_sales, f_inventory, d_products, d_date = load_data()
sales_df, inventory_df = merge_dimensions(f_sales, f_inventory, d_products, d_date)

# -------------------------
# Sidebar Filters
# -------------------------
st.sidebar.header("Filter Data")

# Product type
product_types = sorted(d_products["type"].dropna().unique().tolist())
type_options = ["Overall"] + product_types
selected_type = st.sidebar.selectbox("Select Product Type", type_options)

# Full product list for selected type
if selected_type == "Overall":
    all_products_in_type = sorted(d_products["product_name"].dropna().unique().tolist())
else:
    all_products_in_type = sorted(
        d_products[d_products["type"] == selected_type]["product_name"].dropna().unique().tolist()
    )

# Search + Select All Toggle
search_term = st.sidebar.text_input("🔎 Search Product")
select_all = st.sidebar.checkbox("Select All Products", value=True)

if search_term:
    filtered_products = [p for p in all_products_in_type if search_term.lower() in p.lower()]
    default_selected = filtered_products
else:
    filtered_products = all_products_in_type
    default_selected = all_products_in_type if select_all else []

selected_products = st.sidebar.multiselect(
    "Select Product(s)",
    options=filtered_products,
    default=default_selected,
    key="product_select"
)

st.sidebar.caption(f"Selected {len(selected_products)} of {len(filtered_products)} shown | {len(all_products_in_type)} total in type")

# Date Range
min_date = sales_df["date"].min()
max_date = sales_df["date"].max()
selected_dates = st.sidebar.date_input("Select Date Range", [min_date, max_date])
start_date, end_date = pd.to_datetime(selected_dates[0]), pd.to_datetime(selected_dates[1])

# -------------------------
# Filtered Data for Pages
# -------------------------
sales_df["sales_revenue"] = sales_df["quantity_sold"] * sales_df["unit_retail_price_usd"]
inventory_df["inventory_cost"] = inventory_df["quantity_purchased"] * inventory_df["unit_cost_usd"]

sales_filtered = sales_df[
    (sales_df["product_name"].isin(selected_products)) &
    (sales_df["date"].between(start_date, end_date))
].copy()

inventory_filtered = inventory_df[
    (inventory_df["product_name"].isin(selected_products)) &
    (inventory_df["date"].between(start_date, end_date))
].copy()


import pages.sales_inventory_page as test
print("DEBUG:", dir(test))

# -------------------------
# Render Pages
# -------------------------
sales_inventory_page.show(sales_filtered, inventory_filtered)
revenue_trend.show(sales_filtered, inventory_filtered)
monthly_breakdown.show(sales_filtered, inventory_filtered)
food_nonholiday.show(sales_df)
product_threshold.show(sales_df, selected_products, start_date, end_date)
cumulative_sales.show(sales_df, selected_products, start_date, end_date)
cashflow_ratio.show(sales_df, inventory_df, selected_products, start_date, end_date)