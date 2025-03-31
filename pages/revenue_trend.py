import streamlit as st
import plotly.express as px

def add_period_column(df, date_col, level):
    df = df.copy()
    if level == "Weekly":
        df["period"] = df[date_col].dt.to_period("W").apply(lambda r: r.start_time)
    elif level == "Monthly":
        df["period"] = df[date_col].dt.to_period("M").apply(lambda r: r.start_time)
    else:
        df["period"] = df[date_col]
    return df

def show(sales_filtered, inventory_filtered):
    st.subheader("Sales Revenue & Inventory Cost - Overall Trend")

    agg_level = st.selectbox(
        "Aggregation Level for this chart",
        ["Daily", "Weekly", "Monthly"],
        key="agg_over_time"
    )

    sales_chart = add_period_column(sales_filtered, "date", agg_level)
    inventory_chart = add_period_column(inventory_filtered, "date", agg_level)

    sales_agg = sales_chart.groupby("period")["sales_revenue"].sum().reset_index()
    inventory_agg = inventory_chart.groupby("period")["inventory_cost"].sum().reset_index()

    revenue_trend = sales_agg.merge(inventory_agg, on="period", how="outer").fillna(0)

    fig = px.line(
        revenue_trend.melt(id_vars="period", value_vars=["sales_revenue", "inventory_cost"]),
        x="period",
        y="value",
        color="variable",
        labels={"value": "Amount ($)", "period": "Date", "variable": "Metric"},
        title=f"Sales Revenue & Inventory Cost Over Time ({agg_level})"
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")