import streamlit as st
import plotly.express as px
import pandas as pd

def show(sales_df, selected_products, start_date, end_date):
    st.subheader("Sales Revenue - Cumulative by Product (Daily)")

    # Toggle for metric
    metric_option = st.radio(
        "View Metric",
        ["Revenue ($)", "Units Sold"],
        horizontal=True
    )

    # Filter sales
    filtered_sales = sales_df[
        (sales_df["product_name"].isin(selected_products)) &
        (sales_df["date"].between(start_date, end_date))
    ].copy()

    if filtered_sales.empty:
        st.warning("No matching sales data found for the selected filters.")
        return

    # Compute metric values
    filtered_sales["sales_revenue"] = filtered_sales["quantity_sold"] * filtered_sales["unit_retail_price_usd"]

    # Group and sort
    if metric_option == "Revenue ($)":
        group_col = "sales_revenue"
        y_label = "Cumulative Sales ($)"
    else:
        group_col = "quantity_sold"
        y_label = "Cumulative Units Sold"

    daily_grouped = (
        filtered_sales.groupby(["product_name", "date"])[group_col]
        .sum()
        .reset_index()
        .sort_values(["product_name", "date"])
    )

    daily_grouped["cumulative"] = (
        daily_grouped.groupby("product_name")[group_col].cumsum()
    )

    # Line chart
    fig = px.line(
        daily_grouped,
        x="date",
        y="cumulative",
        color="product_name",
        labels={
            "date": "Date",
            "cumulative": y_label,
            "product_name": "Product"
        },
        title=f"Cumulative {'Sales' if metric_option == 'Revenue ($)' else 'Units Sold'} Over Time"
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

    # Data preview
    with st.expander("🔍 View Data"):
        display_df = daily_grouped.rename(columns={
            "product_name": "Product",
            "date": "Date",
            group_col: "Daily Value",
            "cumulative": y_label
        })
        display_df["Date"] = pd.to_datetime(display_df["Date"]).dt.date
        st.dataframe(display_df, use_container_width=True)
        
    st.markdown("---")