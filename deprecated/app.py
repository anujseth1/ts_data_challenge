import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("🧠 ThoughtSpot Data Challenge Dashboard")

# -------------------------
# Load Pre-Processed Data
# -------------------------
@st.cache_data
def load_data():
    sales = pd.read_csv("data/f_sales.csv")
    inventory = pd.read_csv("data/f_inventory.csv")
    product = pd.read_csv("data/d_products.csv")
    date = pd.read_csv("data/d_date.csv")
    return sales, inventory, product, date

f_sales, f_inventory, d_products, d_date = load_data()

# -------------------------
# Join Dimensions to Facts
# -------------------------
sales_df = f_sales.merge(d_products, on="product_id", how="left").merge(d_date, on="date_id", how="left")
inventory_df = f_inventory.merge(d_products, on="product_id", how="left").merge(d_date, on="date_id", how="left")

# Ensure 'date' is datetime
sales_df["date"] = pd.to_datetime(sales_df["date"])
inventory_df["date"] = pd.to_datetime(inventory_df["date"])

# -------------------------
# Sidebar Filters
# -------------------------
st.sidebar.header("🔍 Filter Data")
# st.sidebar.markdown("### ⏱️ Time Aggregation Controls")

# st.sidebar.markdown("**Chart A: Revenue/Cost Over Time**")
# agg_level_over_time = st.sidebar.selectbox(
#     "Aggregation Level (Chart A)", ["Daily", "Weekly", "Monthly"], key="agg_over_time"
# )

# st.sidebar.markdown("**Chart B: Revenue/Cost by Product Type**")
# agg_level_by_type = st.sidebar.selectbox(
#     "Aggregation Level (Chart B)", ["Daily", "Weekly", "Monthly"], key="agg_by_type"
# )


# STEP 1: Product Type selection
product_types = sorted(d_products["type"].dropna().unique().tolist())
type_options = ["Overall"] + product_types
selected_type = st.sidebar.selectbox("Select Product Type", type_options)


# # Filter products based on selected type (or show all if 'Overall')
# if selected_type == "Overall":
#     filtered_products = sorted(d_products["product_name"].dropna().unique().tolist())
# else:
#     filtered_products = sorted(
#         d_products[d_products["type"] == selected_type]["product_name"].dropna().unique().tolist()
#     )

# # Select All Toggle
# select_all = st.sidebar.checkbox("Select All Products", value=True)

# if select_all:
#     selected_products = st.sidebar.multiselect(
#         "Select Product(s)", options=filtered_products, default=filtered_products
#     )
# else:
#     selected_products = st.sidebar.multiselect(
#         "Select Product(s)", options=filtered_products
#     )

# STEP 1: Full product list for selected type
if selected_type == "Overall":
    all_products_in_type = sorted(d_products["product_name"].dropna().unique().tolist())
else:
    all_products_in_type = sorted(
        d_products[d_products["type"] == selected_type]["product_name"].dropna().unique().tolist()
    )

# STEP 2: Search input
search_term = st.sidebar.text_input("🔎 Search Product")

# STEP 3: Checkbox to Select All
select_all = st.sidebar.checkbox("Select All Products", value=True)

# STEP 4: Apply search and selection logic
if search_term:
    filtered_products = [p for p in all_products_in_type if search_term.lower() in p.lower()]
    default_selected = filtered_products  # Auto-select all matches
else:
    filtered_products = all_products_in_type
    default_selected = all_products_in_type if select_all else []

# STEP 5: Always show the multiselect
selected_products = st.sidebar.multiselect(
    "Select Product(s)",
    options=filtered_products,
    default=default_selected,
    key="product_select"
)

# Optional info text
st.sidebar.caption(f"Selected {len(selected_products)} of {len(filtered_products)} shown | {len(all_products_in_type)} total in type")

# Date Range
min_date = sales_df["date"].min()
max_date = sales_df["date"].max()
selected_dates = st.sidebar.date_input("Select Date Range", [min_date, max_date])

# Apply Filters
start_date, end_date = pd.to_datetime(selected_dates[0]), pd.to_datetime(selected_dates[1])

sales_filtered = sales_df[
    (sales_df["product_name"].isin(selected_products)) &
    (sales_df["date"].between(start_date, end_date))
]

inventory_filtered = inventory_df[
    (inventory_df["product_name"].isin(selected_products)) &
    (inventory_df["date"].between(start_date, end_date))
]



# Period aggregation helper
def add_period_column(df, date_col, level):
    df = df.copy()
    if level == "Weekly":
        df["period"] = df[date_col].dt.to_period("W").apply(lambda r: r.start_time)
    elif level == "Monthly":
        df["period"] = df[date_col].dt.to_period("M").apply(lambda r: r.start_time)
    else:
        df["period"] = df[date_col]
    return df



# -------------------------
# Sales and Inventory USD
# -------------------------

st.subheader("💵 Sales & Inventory Value by Product")

# Step 1: Add monetary value columns
sales_filtered["sales_revenue"] = sales_filtered["quantity_sold"] * sales_filtered["unit_retail_price_usd"]
inventory_filtered["inventory_cost"] = inventory_filtered["quantity_purchased"] * inventory_filtered["unit_cost_usd"]

# Step 2: Aggregate by product
revenue_by_product = (
    sales_filtered.groupby("product_name")["sales_revenue"].sum().reset_index()
)
cost_by_product = (
    inventory_filtered.groupby("product_name")["inventory_cost"].sum().reset_index()
)

# Step 3: Merge into one table
product_dollars = pd.merge(revenue_by_product, cost_by_product, on="product_name", how="outer").fillna(0)

# Step 4: Plot
fig = px.bar(
    product_dollars.melt(id_vars="product_name", value_vars=["sales_revenue", "inventory_cost"]),
    x="product_name",
    y="value",
    color="variable",
    barmode="group",
    labels={"value": "Amount ($)", "product_name": "Product", "variable": "Metric"},
    title="Sales Revenue vs Inventory Cost by Product"
)

st.plotly_chart(fig, use_container_width=True)




st.subheader("📈 Sales Revenue vs Inventory Cost Over Time")
agg_level_over_time = st.selectbox(
    "Aggregation Level for this chart",
    ["Daily", "Weekly", "Monthly"],
    key="agg_over_time"
)

sales_chart = add_period_column(sales_filtered, "date", agg_level_over_time)
inventory_chart = add_period_column(inventory_filtered, "date", agg_level_over_time)

sales_agg = sales_chart.groupby("period")["sales_revenue"].sum().reset_index()
inventory_agg = inventory_chart.groupby("period")["inventory_cost"].sum().reset_index()

revenue_trend = pd.merge(sales_agg, inventory_agg, on="period", how="outer").fillna(0)

fig = px.line(
    revenue_trend.melt(id_vars="period", value_vars=["sales_revenue", "inventory_cost"]),
    x="period",
    y="value",
    color="variable",
    labels={"value": "Amount ($)", "period": "Date", "variable": "Metric"},
    title=f"Sales Revenue vs Inventory Cost Over Time ({agg_level_over_time})"
)
st.plotly_chart(fig, use_container_width=True)


# -------------------------
# Sales and Inventory MoM
# -------------------------

# Extract month
sales_filtered["month"] = sales_filtered["date"].dt.strftime("%B %Y")
inventory_filtered["month"] = inventory_filtered["date"].dt.strftime("%B %Y")

# Group by product and month
revenue_monthly = sales_filtered.groupby(["product_name", "month"])["sales_revenue"].sum().reset_index()
cost_monthly = inventory_filtered.groupby(["product_name", "month"])["inventory_cost"].sum().reset_index()

# Combine and melt
monthly_combined = pd.merge(revenue_monthly, cost_monthly, on=["product_name", "month"], how="outer").fillna(0)
melted_monthly = monthly_combined.melt(
    id_vars=["product_name", "month"],
    value_vars=["sales_revenue", "inventory_cost"],
    var_name="Metric",
    value_name="Amount"
)

# Create faceted grouped bar chart
st.subheader("📊 Monthly Sales Revenue vs Inventory Cost by Product")
fig = px.bar(
    melted_monthly,
    x="product_name",
    y="Amount",
    color="Metric",
    barmode="group",
    facet_col="month",
    facet_col_wrap=3,
    labels={"product_name": "Product", "Amount": "Amount ($)", "Metric": "Metric"},
    height=600
)
fig.update_layout(
    xaxis_tickangle=0,  # 0 degrees = fully horizontal
    xaxis_title=None
)
st.plotly_chart(fig, use_container_width=True)

# -------------------------
# question 3
# -------------------------

st.subheader("🍽️ Total Sales for Food on Non-Holidays")

# Filter for food items on non-holidays
food_nonholiday_sales = sales_df[
    (sales_df["type"] == "food") &
    (sales_df["is_holiday"] == 0)  # assuming is_holiday is boolean or 0/1
]

food_nonholiday_sales = food_nonholiday_sales.copy()  # safe copy
food_nonholiday_sales["sales_revenue"] = (
    food_nonholiday_sales["quantity_sold"] * food_nonholiday_sales["unit_retail_price_usd"]
)

# Compute total
total_food_sales_nonholiday = food_nonholiday_sales["sales_revenue"].sum()

# Display
st.metric(label="Total Sales (Food, Non-Holiday)", value=f"${total_food_sales_nonholiday:,.2f}")

# -------------------------
# question 4
# -------------------------

import plotly.express as px

# Make sure revenue and cost columns are calculated
sales_df["sales_revenue"] = sales_df["quantity_sold"] * sales_df["unit_retail_price_usd"]
inventory_df["inventory_cost"] = inventory_df["quantity_purchased"] * inventory_df["unit_cost_usd"]


st.subheader("📊 Sales Revenue vs Inventory Cost by Product Type")

agg_level_by_type = st.selectbox(
    "Aggregation Level for this chart",
    ["Overall", "Daily", "Weekly", "Monthly"],
    key="agg_by_type"
)

if agg_level_by_type == "Overall":
    # Simple bar chart with totals
    sales_by_type = sales_df.groupby("type")["sales_revenue"].sum().reset_index()
    inventory_by_type = inventory_df.groupby("type")["inventory_cost"].sum().reset_index()

    type_summary = pd.merge(sales_by_type, inventory_by_type, on="type", how="outer").fillna(0)

    melted_type_summary = type_summary.melt(
        id_vars="type",
        value_vars=["sales_revenue", "inventory_cost"],
        var_name="Metric",
        value_name="Amount"
    )

    fig = px.bar(
        melted_type_summary,
        x="type",
        y="Amount",
        color="Metric",
        barmode="group",
        title="Total Sales vs Inventory Cost by Product Type",
        labels={"type": "Product Type", "Amount": "Amount ($)", "Metric": "Metric"},
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    # Step 1: Add period column first
    sales_df_period = add_period_column(sales_df, "date", agg_level_by_type)
    inventory_df_period = add_period_column(inventory_df, "date", agg_level_by_type)

    # Step 2: Group by type and period
    sales_by_type = sales_df_period.groupby(["type", "period"])["sales_revenue"].sum().reset_index()
    inventory_by_type = inventory_df_period.groupby(["type", "period"])["inventory_cost"].sum().reset_index()

    # Step 3: Format period for cleaner facet labels
    if agg_level_by_type == "Monthly":
        fmt = "%b %Y"  # e.g., Mar 2024
    else:
        fmt = "%b %d"  # e.g., Mar 01

    sales_by_type["Period Label"] = pd.to_datetime(sales_by_type["period"]).dt.strftime(fmt)
    inventory_by_type["Period Label"] = pd.to_datetime(inventory_by_type["period"]).dt.strftime(fmt)

    # Step 4: Merge and melt
    type_summary = pd.merge(
        sales_by_type[["type", "Period Label", "sales_revenue"]],
        inventory_by_type[["type", "Period Label", "inventory_cost"]],
        on=["type", "Period Label"],
        how="outer"
    ).fillna(0)

    melted_type_summary = type_summary.melt(
        id_vars=["type", "Period Label"],
        value_vars=["sales_revenue", "inventory_cost"],
        var_name="Metric",
        value_name="Amount"
    )

    # Step 5: Plot with formatted facet column
    fig = px.bar(
        melted_type_summary,
        x="type",
        y="Amount",
        color="Metric",
        barmode="group",
        facet_col="Period Label",
        facet_col_wrap=3,
        title=f"{agg_level_by_type} Sales vs Inventory Cost by Product Type",
        labels={"type": "Product Type", "Amount": "Amount ($)", "Metric": "Metric"},
        height=600
    )
    fig.update_layout(xaxis_tickangle=0)
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    st.plotly_chart(fig, use_container_width=True)


# -------------------------
# Slider based product selection
# -------------------------

st.subheader("💸 Products with High Sales Revenue")

filtered_sales_q4 = sales_df[
    (sales_df["product_name"].isin(selected_products)) &
    (sales_df["date"].between(start_date, end_date))
].copy()

product_sales = filtered_sales_q4.groupby("product_name")["sales_revenue"].sum().reset_index()

if not product_sales.empty:
    min_revenue = int(product_sales["sales_revenue"].min())
    max_revenue = int(product_sales["sales_revenue"].max())
    default_value = min(150, max_revenue)

    threshold = st.slider(
        "Minimum Total Sales ($)",
        min_value=min_revenue,
        max_value=max_revenue,
        value=default_value,
        step=2
    )

    high_sellers = product_sales[product_sales["sales_revenue"] > threshold].sort_values(
        by="sales_revenue", ascending=False
    )

    if not high_sellers.empty:
        fig_q4 = px.bar(
            high_sellers,
            x="product_name",
            y="sales_revenue",
            title=f"Products with Sales > ${threshold}",
            labels={"product_name": "Product", "sales_revenue": "Total Sales ($)"},
            color="sales_revenue"
        )
        fig_q4.update_layout(xaxis_tickangle=0)
        st.plotly_chart(fig_q4, use_container_width=True)

        st.dataframe(high_sellers)
    else:
        st.warning("No products found with sales above the selected threshold.")
else:
    st.info("No matching sales found for the selected filters.")


# -------------------------
# Cumulative sales
# -------------------------

st.subheader("📈 Cumulative Sales by Product (Daily)")

# Step 1: Filter sales_df using sidebar selections
filtered_sales_q5 = sales_df[
    (sales_df["product_name"].isin(selected_products)) &
    (sales_df["date"].between(start_date, end_date))
].copy()

# Step 2: If filtered data is empty, show warning
if filtered_sales_q5.empty:
    st.warning("No sales data found for selected filters.")
else:
    # Step 3: Group daily sales and compute cumulative revenue
    daily_revenue = (
        filtered_sales_q5.groupby(["product_name", "date"])["sales_revenue"]
        .sum()
        .reset_index()
        .sort_values(["product_name", "date"])
    )

    daily_revenue["cumulative_sales"] = (
        daily_revenue.groupby("product_name")["sales_revenue"].cumsum()
    )

    # Step 4: Plot chart
    fig_q5 = px.line(
        daily_revenue,
        x="date",
        y="cumulative_sales",
        color="product_name",
        title="Cumulative Sales by Product",
        labels={
            "date": "Date",
            "cumulative_sales": "Cumulative Sales ($)",
            "product_name": "Product"
        }
    )
    st.plotly_chart(fig_q5, use_container_width=True)
    # st.dataframe(daily_revenue)

# -------------------------
# 💰 Weekly Cashflow Ratio Report
# -------------------------
st.subheader("💰 Weekly Cashflow Ratio Report")

# Toggle: how to compare
cashflow_grouping = st.radio(
    "Compare Cashflow Ratio By",
    ["Overall", "Product Type","Product"],
    horizontal=True
)

# Step 1: Filter sales and inventory using sidebar filters
sales_q6 = sales_df[
    (sales_df["product_name"].isin(selected_products)) &
    (sales_df["date"].between(start_date, end_date))
].copy()

inventory_q6 = inventory_df[
    (inventory_df["product_name"].isin(selected_products)) &
    (inventory_df["date"].between(start_date, end_date))
].copy()

# Step 2: Add week start date
sales_q6["week"] = sales_q6["date"].dt.to_period("W").apply(lambda r: r.start_time)
inventory_q6["week"] = inventory_q6["date"].dt.to_period("W").apply(lambda r: r.start_time)

# Step 3: Decide grouping
if cashflow_grouping == "Product Type":
    group_cols = ["type", "week"]
    color_col = "type"
elif cashflow_grouping == "Product":
    group_cols = ["product_name", "week"]
    color_col = "product_name"
else:
    group_cols = ["week"]
    color_col = None

# Step 4: Aggregate sales and cost
weekly_sales = sales_q6.groupby(group_cols)["sales_revenue"].sum().reset_index()
weekly_cost = inventory_q6.groupby(group_cols)["inventory_cost"].sum().reset_index()

# Step 5: Merge and calculate ratio
cashflow = pd.merge(weekly_sales, weekly_cost, on=group_cols, how="outer").fillna(0)
cashflow["cashflow_ratio"] = cashflow.apply(
    lambda row: row["sales_revenue"] / row["inventory_cost"] if row["inventory_cost"] != 0 else float("inf"),
    axis=1
)

# Step 6: Format week label
cashflow["Week Start"] = cashflow["week"].dt.strftime("%b %d, %Y")

# -----------------------------
# 💡 KPI Summary for Cashflow (Overall)
# -----------------------------
if len(group_cols) == 1:  # Only show KPI if not comparing across types/stores
    cashflow_sorted = cashflow.sort_values(by="Week Start")

    if len(cashflow_sorted) >= 2:
        current_week = cashflow_sorted.iloc[-1]
        previous_week = cashflow_sorted.iloc[-2]

        delta_sales = current_week["sales_revenue"] - previous_week["sales_revenue"]
        delta_cost = current_week["inventory_cost"] - previous_week["inventory_cost"]
        delta_ratio = current_week["cashflow_ratio"] - previous_week["cashflow_ratio"]

        sales_delta_text = f"{delta_sales:+.2f}"
        cost_delta_text = f"{delta_cost:+.2f}"
        ratio_delta_text = f"{delta_ratio:+.2f}x"
    else:
        sales_delta_text = "N/A"
        cost_delta_text = "N/A"
        ratio_delta_text = "N/A"

    total_sales = cashflow_sorted["sales_revenue"].sum()
    total_cost = cashflow_sorted["inventory_cost"].sum()
    overall_ratio = total_sales / total_cost if total_cost > 0 else float("inf")

    col1, col2, col3 = st.columns(3)
    col1.metric("📈 Total Sales", f"${total_sales:,.2f}", delta=sales_delta_text)
    col2.metric("📦 Total Inventory Cost", f"${total_cost:,.2f}", delta=cost_delta_text)
    col3.metric("💰 Cashflow Ratio", f"{overall_ratio:.2f}x", delta=ratio_delta_text)

# -----------------------------
# 📊 Chart: Cashflow Ratio
# -----------------------------

x_col = "Week Start"

fig = px.line(
    cashflow,
    x=x_col,
    y="cashflow_ratio",
    color=color_col if color_col else None,
    markers=True,
    title=f"Weekly Cashflow Ratio" + (f" by {cashflow_grouping}" if cashflow_grouping != "Overall" else ""),
    labels={"cashflow_ratio": "Cashflow Ratio", x_col: "Week Starting"},
    height=500
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# 📋 Data Table
# -----------------------------
cols_to_display = ["Week Start", "sales_revenue", "inventory_cost", "cashflow_ratio"]
if color_col:
    cols_to_display.insert(0, color_col)

st.dataframe(
    cashflow[cols_to_display].rename(columns={
        "sales_revenue": "Sales ($)",
        "inventory_cost": "Inventory Cost ($)",
        "cashflow_ratio": "Cashflow Ratio"
    })
)

# # -------------------------
# # Show Filtered Data
# # -------------------------
# st.subheader("📊 Filtered Sales Data")
# st.dataframe(sales_filtered.head())

# st.subheader("📦 Filtered Inventory Data")
# st.dataframe(inventory_filtered.head())