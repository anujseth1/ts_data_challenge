import streamlit as st
import pandas as pd

def sidebar_filters(sales_df, inventory_df, d_products):
    st.sidebar.header("🔍 Filter Data")

    product_types = sorted(d_products["type"].dropna().unique().tolist())
    type_options = ["Overall"] + product_types
    selected_type = st.sidebar.selectbox("Select Product Type", type_options)

    if selected_type == "Overall":
        all_products = sorted(d_products["product_name"].dropna().unique().tolist())
    else:
        all_products = sorted(
            d_products[d_products["type"] == selected_type]["product_name"].dropna().unique().tolist()
        )

    search_term = st.sidebar.text_input("🔎 Search Product")
    select_all = st.sidebar.checkbox("Select All Products", value=True)

    if search_term:
        filtered_products = [p for p in all_products if search_term.lower() in p.lower()]
        default_selected = filtered_products
    else:
        filtered_products = all_products
        default_selected = all_products if select_all else []

    selected_products = st.sidebar.multiselect(
        "Select Product(s)", options=filtered_products, default=default_selected, key="product_select"
    )

    st.sidebar.caption(
        f"Selected {len(selected_products)} of {len(filtered_products)} shown | {len(all_products)} total in type"
    )

    min_date = sales_df["date"].min()
    max_date = sales_df["date"].max()
    selected_dates = st.sidebar.date_input("Select Date Range", [min_date, max_date])
    start_date, end_date = pd.to_datetime(selected_dates[0]), pd.to_datetime(selected_dates[1])

    return selected_products, start_date, end_date
