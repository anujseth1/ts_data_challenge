import streamlit as st
import pandas as pd
import plotly.express as px

def show(sales_df, inventory_df, selected_products, start_date, end_date):
    st.subheader("Weekly Cashflow Ratio Report")

    # Grouping toggle
    grouping = st.radio(
        "Compare Cashflow Ratio By",
        ["Overall", "Product Type", "Product"],
        horizontal=True
    )

    # Filter
    sales = sales_df[
        (sales_df["product_name"].isin(selected_products)) &
        (sales_df["date"].between(start_date, end_date))
    ].copy()
    inventory = inventory_df[
        (inventory_df["product_name"].isin(selected_products)) &
        (inventory_df["date"].between(start_date, end_date))
    ].copy()

    # Add week column
    sales["week"] = sales["date"].dt.to_period("W").apply(lambda r: r.start_time)
    inventory["week"] = inventory["date"].dt.to_period("W").apply(lambda r: r.start_time)

    # Decide grouping
    if grouping == "Product Type":
        group_cols = ["type", "week"]
        color_col = "type"
    elif grouping == "Product":
        group_cols = ["product_name", "week"]
        color_col = "product_name"
    else:
        group_cols = ["week"]
        color_col = None

    # Aggregate
    weekly_sales = sales.groupby(group_cols)["sales_revenue"].sum().reset_index()
    weekly_cost = inventory.groupby(group_cols)["inventory_cost"].sum().reset_index()

    # Merge
    cashflow = pd.merge(weekly_sales, weekly_cost, on=group_cols, how="outer").fillna(0)
    cashflow["cashflow_ratio"] = cashflow.apply(
        lambda row: row["sales_revenue"] / row["inventory_cost"] if row["inventory_cost"] != 0 else float("inf"),
        axis=1
    )

    cashflow["Week Start"] = cashflow["week"].dt.strftime("%b %d, %Y")

    # KPI Summary (only for Overall)
    if len(group_cols) == 1:
        sorted_cf = cashflow.sort_values(by="Week Start")

        if len(sorted_cf) >= 2:
            current, previous = sorted_cf.iloc[-1], sorted_cf.iloc[-2]
            delta_sales = current["sales_revenue"] - previous["sales_revenue"]
            delta_cost = current["inventory_cost"] - previous["inventory_cost"]
            delta_ratio = current["cashflow_ratio"] - previous["cashflow_ratio"]

            sales_delta = f"{delta_sales:+.2f}"
            cost_delta = f"{delta_cost:+.2f}"
            ratio_delta = f"{delta_ratio:+.2f}x"
        else:
            sales_delta = cost_delta = ratio_delta = "N/A"

        total_sales = sorted_cf["sales_revenue"].sum()
        total_cost = sorted_cf["inventory_cost"].sum()
        total_ratio = total_sales / total_cost if total_cost else float("inf")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Sales", f"${total_sales:,.2f}", delta=sales_delta)
        col2.metric("Total Inventory Cost", f"${total_cost:,.2f}", delta=cost_delta)
        col3.metric("Cashflow Ratio", f"{total_ratio:.2f}x", delta=ratio_delta)

    # Chart
    fig = px.line(
        cashflow,
        x="Week Start",
        y="cashflow_ratio",
        color=color_col if color_col else None,
        markers=True,
        title="Weekly Cashflow Ratio" + (f" by {grouping}" if grouping != "Overall" else ""),
        labels={"cashflow_ratio": "Cashflow Ratio"},
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

    # Table
    cols = ["Week Start", "sales_revenue", "inventory_cost", "cashflow_ratio"]
    if color_col:
        cols.insert(0, color_col)

    st.dataframe(
        cashflow[cols].rename(columns={
            "sales_revenue": "Sales ($)",
            "inventory_cost": "Inventory Cost ($)",
            "cashflow_ratio": "Cashflow Ratio"
        })
    )

    st.markdown("---")