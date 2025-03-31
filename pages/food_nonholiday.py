import streamlit as st

def show(sales_df):
    st.markdown("### Sales Revenue - Overall by Product Type and Holiday Period")

    # Ensure calculated column exists
    sales_df["sales_revenue"] = sales_df["quantity_sold"] * sales_df["unit_retail_price_usd"]

    # Define filters
    food_nonholiday = sales_df[(sales_df["type"] == "food") & (sales_df["is_holiday"] == 0)]
    food_holiday = sales_df[(sales_df["type"] == "food") & (sales_df["is_holiday"] == 1)]
    nonfood_nonholiday = sales_df[(sales_df["type"] != "food") & (sales_df["is_holiday"] == 0)]
    nonfood_holiday = sales_df[(sales_df["type"] != "food") & (sales_df["is_holiday"] == 1)]

    # Calculate totals
    fnh_total = food_nonholiday["sales_revenue"].sum()
    fh_total = food_holiday["sales_revenue"].sum()
    nfn_total = nonfood_nonholiday["sales_revenue"].sum()
    nfh_total = nonfood_holiday["sales_revenue"].sum()

    # Show KPI Cards
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    col1.metric("Food (Non-Holiday)", f"${fnh_total:,.2f}")
    col3.metric("Food (Holiday)", f"${fh_total:,.2f}")
    col4.metric("Non-Food (Non-Holiday)", f"${nfn_total:,.2f}")
    col6.metric("Non-Food (Holiday)", f"${nfh_total:,.2f}")

    
    st.markdown("---")