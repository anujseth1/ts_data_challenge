import streamlit as st
import pandas as pd
import plotly.express as px

def show(sales_filtered, inventory_filtered):
    # st.subheader("📆 Monthly Overview")

    # Add month column
    sales_filtered["month"] = sales_filtered["date"].dt.strftime("%B %Y")
    inventory_filtered["month"] = inventory_filtered["date"].dt.strftime("%B %Y")

    # ==============================
    # Chart: Sales & Inventory by Product and Month
    # ==============================
    st.markdown("### Sales Revenue & Inventory Cost - Monthly by Product/Type")

    # Add toggle for product name vs product type
    group_by_option = st.radio("Group Chart By", ["Product Name", "Product Type"], horizontal=True)

    # Set grouping column
    group_col = "product_name" if group_by_option == "Product Name" else "type"
    x_label = "Product" if group_by_option == "Product Name" else "Product Type"

    revenue_monthly = sales_filtered.groupby([group_col, "month"])["sales_revenue"].sum().reset_index()
    cost_monthly = inventory_filtered.groupby([group_col, "month"])["inventory_cost"].sum().reset_index()

    monthly_combined = pd.merge(revenue_monthly, cost_monthly, on=[group_col, "month"], how="outer").fillna(0)
    melted_monthly = monthly_combined.melt(
        id_vars=[group_col, "month"],
        value_vars=["sales_revenue", "inventory_cost"],
        var_name="Metric",
        value_name="Amount"
    )

    
    fig = px.bar(
        melted_monthly,
        x=group_col,
        y="Amount",
        color="Metric",
        barmode="group",
        facet_col="month",
        facet_col_wrap=3,
        labels={group_col: x_label, "Amount": "Amount ($)", "Metric": "Metric"},
        height=600
    )
    fig.update_layout(xaxis_tickangle=0, xaxis_title=None)
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    st.plotly_chart(fig, use_container_width=True)

    # ==============================
    # 📋 Overall Monthly Summary
    # ==============================
    st.markdown("### Monthly Summary – Overall")

    overall_sales = sales_filtered.groupby("month")["sales_revenue"].sum().reset_index()
    overall_inventory = inventory_filtered.groupby("month")["inventory_cost"].sum().reset_index()

    monthly_overall = pd.merge(overall_sales, overall_inventory, on="month", how="outer").fillna(0)
    monthly_overall["profit"] = monthly_overall["sales_revenue"] - monthly_overall["inventory_cost"]
    monthly_overall["profit_pct"] = monthly_overall.apply(
        lambda row: (row["profit"] / row["sales_revenue"]) * 100 if row["sales_revenue"] else 0,
        axis=1
    )

    monthly_overall["month_sort"] = pd.to_datetime(monthly_overall["month"], format="%B %Y")
    monthly_overall = monthly_overall.sort_values("month_sort", ascending=False)

    st.dataframe(
        monthly_overall[["month", "sales_revenue", "inventory_cost"]]
        .rename(columns={
            "month": "Month",
            "sales_revenue": "Total Sales ($)",
            "inventory_cost": "Total Inventory Cost ($)"
            # "profit": "Profit ($)",
            # "profit_pct": "Profit %"
        }),
        use_container_width=True
    )

    # ==============================
    # Monthly Summary – By Product Type
    # ==============================
    st.markdown("### Monthly Summary – By Product Type")

    sales_by_type = sales_filtered.groupby(["type", "month"])["sales_revenue"].sum().reset_index()
    inventory_by_type = inventory_filtered.groupby(["type", "month"])["inventory_cost"].sum().reset_index()

    combined_type = pd.merge(sales_by_type, inventory_by_type, on=["type", "month"], how="outer").fillna(0)
    combined_type["profit"] = combined_type["sales_revenue"] - combined_type["inventory_cost"]
    combined_type["profit_pct"] = combined_type.apply(
        lambda row: (row["profit"] / row["sales_revenue"]) * 100 if row["sales_revenue"] else 0,
        axis=1
    )

    combined_type["month_sort"] = pd.to_datetime(combined_type["month"], format="%B %Y")
    combined_type = combined_type.sort_values(["type", "month_sort"], ascending=[True, False])

    st.dataframe(
        combined_type[["type", "month", "sales_revenue", "inventory_cost"]]
        .rename(columns={
            "type": "Product Type",
            "month": "Month",
            "sales_revenue": "Sales ($)",
            "inventory_cost": "Inventory Cost ($)"
            # "profit": "Profit ($)",
            # "profit_pct": "Profit %"
        }),
        use_container_width=True
    )

    # ==============================
    # 🔽 Product Breakdown by Type
    # ==============================
    st.markdown("### 🔽 Monthly Summary – By Product")

    for t in combined_type["type"].dropna().unique():
        type_sales = sales_filtered[sales_filtered["type"] == t]
        type_inventory = inventory_filtered[inventory_filtered["type"] == t]

        if type_sales.empty and type_inventory.empty:
            continue

        with st.expander(f"🔍 {t.capitalize()} Products"):
            sales_by_prod = type_sales.groupby(["product_name", "month"])["sales_revenue"].sum().reset_index()
            inv_by_prod = type_inventory.groupby(["product_name", "month"])["inventory_cost"].sum().reset_index()

            combined = pd.merge(sales_by_prod, inv_by_prod, on=["product_name", "month"], how="outer").fillna(0)
            combined["profit"] = combined["sales_revenue"] - combined["inventory_cost"]
            combined["profit_pct"] = combined.apply(
                lambda row: (row["profit"] / row["sales_revenue"]) * 100 if row["sales_revenue"] else 0,
                axis=1
            )

            combined["month_sort"] = pd.to_datetime(combined["month"], format="%B %Y")
            combined = combined.sort_values(["product_name", "month_sort"], ascending=[True, False])

            st.dataframe(
                combined[["product_name", "month", "sales_revenue", "inventory_cost"]]
                .rename(columns={
                    "product_name": "Product",
                    "month": "Month",
                    "sales_revenue": "Sales ($)",
                    "inventory_cost": "Inventory Cost ($)"
                    # "profit": "Profit ($)",
                    # "profit_pct": "Profit %"
                }),
                use_container_width=True
            )

    st.markdown("---")