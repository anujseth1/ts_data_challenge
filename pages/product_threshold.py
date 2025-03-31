import streamlit as st
import plotly.express as px

def show(sales_df, selected_products, start_date, end_date):
    st.subheader("Products with High Sales Revenue")

    # Filter using sidebar selections
    filtered_sales = sales_df[
        (sales_df["product_name"].isin(selected_products)) &
        (sales_df["date"].between(start_date, end_date))
    ].copy()

    if filtered_sales.empty:
        st.info("No matching sales found for the selected filters.")
        return

    # Compute revenue and realized cost
    filtered_sales["sales_revenue"] = (
        filtered_sales["quantity_sold"] * filtered_sales["unit_retail_price_usd"]
    )
    filtered_sales["realized_cost"] = (
        filtered_sales["quantity_sold"] * filtered_sales["unit_cost_usd"]
    )

    # Aggregate metrics
    product_sales = (
        filtered_sales.groupby("product_name")
        .agg(
            sales_revenue=("sales_revenue", "sum"),
            units_sold=("quantity_sold", "sum"),
            realized_cost=("realized_cost", "sum")
        )
        .reset_index()
    )

    # Compute realized profit and profit %
    product_sales["realized_profit"] = product_sales["sales_revenue"] - product_sales["realized_cost"]
    product_sales["profit_pct"] = product_sales.apply(
        lambda row: (row["realized_profit"] / row["realized_cost"] * 100) if row["realized_cost"] != 0 else 0,
        axis=1
    )

    if product_sales.empty:
        st.info("No products found.")
        return

    # Slider to set threshold
    min_revenue = int(product_sales["sales_revenue"].min())
    max_revenue = int(product_sales["sales_revenue"].max())
    default_value = min(150, max_revenue)

    threshold = st.slider(
        "Minimum Total Sales ($)",
        min_value=min_revenue,
        max_value=max_revenue,
        value=default_value,
        step=1
    )

    # Filter products
    high_sellers = product_sales[product_sales["sales_revenue"] > threshold].sort_values(
        by="sales_revenue", ascending=False
    )

    if high_sellers.empty:
        st.warning("No products found with sales above the selected threshold.")
        return

    # Bar chart
    import plotly.graph_objects as go

# Initialize figure with bar traces
    fig = go.Figure()

# Add Sales Revenue bar
    fig.add_bar(
        x=high_sellers["product_name"],
        y=high_sellers["sales_revenue"],
        name="Sales Revenue ($)",
        marker_color="steelblue",
    )

# Add Profit % line on secondary y-axis
    fig.add_trace(
        go.Scatter(
            x=high_sellers["product_name"],
            y=high_sellers["profit_pct"],
            mode="lines+markers",
            name="Profit %",
            yaxis="y2",
            line=dict(color="green", width=2),
            marker=dict(size=6)
        )
    )

# Layout: dual y-axes
    fig.update_layout(
        title=f"Products with Sales > ${threshold}",
        xaxis=dict(title="Product", tickangle=0),
        yaxis=dict(title="Sales Revenue ($)"),
        yaxis2=dict(
            title="Profit %",
            overlaying="y",
            side="right",
            showgrid=False
        ),
            legend=dict(x=0.01, y=1.15, orientation="h"),
            height=500
        )

    st.plotly_chart(fig, use_container_width=True)


    # Data table
    # Step 1: Rename columns
    display_df = high_sellers.rename(columns={
        "product_name": "Product",
        "sales_revenue": "Total Sales ($)",
        "units_sold": "Units Sold",
        "realized_profit": "Profit ($)",
        "profit_pct": "Profit %"
    })

    # Step 2: Format Profit %
    display_df["Profit %"] = display_df["Profit %"].map("{:.1f}%".format)

    # Step 3: Display final table
    st.dataframe(display_df[["Product", "Total Sales ($)", "Units Sold", "Profit ($)", "Profit %"]],
                use_container_width=True)


    st.markdown("---")
