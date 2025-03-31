import streamlit as st
import pandas as pd
import plotly.express as px

def show(sales_filtered, inventory_filtered):
    st.markdown("---")
    st.subheader("Sales Revenue & Inventory Cost - Overall by Product")

    # Step 1: Add monetary value columns
    sales_filtered["sales_revenue"] = sales_filtered["quantity_sold"] * sales_filtered["unit_retail_price_usd"]
    inventory_filtered["inventory_cost"] = inventory_filtered["quantity_purchased"] * inventory_filtered["unit_cost_usd"]

    # Toggle to group by Product Name or Product Type
    group_by = st.radio("Group By", ["Product Name", "Product Type"], horizontal=True)
    group_col = "product_name" if group_by == "Product Name" else "type"

    # Step 2: Aggregate revenue and cost
    revenue_by_product = sales_filtered.groupby(group_col)["sales_revenue"].sum().reset_index()
    cost_by_product = inventory_filtered.groupby(group_col)["inventory_cost"].sum().reset_index()

    # Step 3: Compute realized cost (only for sold quantity)
    realized_costs = sales_filtered.copy()
    realized_costs["realized_cost"] = realized_costs["quantity_sold"] * realized_costs["unit_cost_usd"]
    cost_by_realized = realized_costs.groupby(group_col)["realized_cost"].sum().reset_index()

    # Step 4: Merge all metrics
    product_dollars = revenue_by_product.merge(cost_by_product, on=group_col, how="outer").fillna(0)
    product_dollars = product_dollars.merge(cost_by_realized, on=group_col, how="left").fillna(0)

    product_dollars["realized_profit"] = product_dollars["sales_revenue"] - product_dollars["realized_cost"]
    product_dollars["profit_pct"] = product_dollars.apply(
        lambda row: (row["realized_profit"] / row["realized_cost"] * 100) if row["realized_cost"] else 0,
        axis=1
    )

    # Step 5: KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    total_sales = product_dollars["sales_revenue"].sum()
    total_inventory_cost = product_dollars["inventory_cost"].sum()
    total_realized_cost = product_dollars["realized_cost"].sum()
    total_profit = total_sales - total_realized_cost
    profit_pct = (total_profit / total_realized_cost * 100) if total_realized_cost else 0

    col1.metric("💰 Total Sales", f"${total_sales:,.0f}")
    col2.metric("📦 Inventory Cost", f"${total_inventory_cost:,.0f}")
    col3.metric("💵 Realized Profit", f"${total_profit:,.0f}")
    col4.metric("📈 Profit %", f"{profit_pct:.1f}%")

    # Step 6: Grouped Bar Chart + Profit % Line
    product_dollars = product_dollars.sort_values(by="sales_revenue", ascending=False)

    fig = px.bar(
        product_dollars,
        x=group_col,
        y=["sales_revenue", "inventory_cost"],
        barmode="group",
        labels={group_col: group_by, "value": "Amount ($)", "variable": "Metric"},
    )

    fig.add_scatter(
        x=product_dollars[group_col],
        y=product_dollars["profit_pct"],
        mode="lines+markers",
        name="Profit %",
        yaxis="y2"
    )

    fig.update_layout(
        yaxis=dict(title="Amount ($)"),
        yaxis2=dict(title="Profit %", overlaying="y", side="right", showgrid=False),
        xaxis_tickangle=0,
        legend_title_text="Metric"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Step 7: Expandable Table
    with st.expander(" 🔽 See Product-Level Details"):
        product_table = product_dollars[[group_col, "sales_revenue", "inventory_cost", "realized_profit", "profit_pct"]]
        product_table = product_table.rename(columns={
            group_col: group_by,
            "sales_revenue": "Sales ($)",
            "inventory_cost": "Inventory Cost ($)",
            "realized_profit": "Profit ($)",
            "profit_pct": "Profit %"
        }).sort_values("Sales ($)", ascending=False)

        product_table["Profit %"] = product_table["Profit %"].map(lambda x: f"{x:.1f}%")
        st.dataframe(product_table, use_container_width=True)

    st.markdown("---")