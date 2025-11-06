import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# -------------------- DATA PREPARATION --------------------

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    return preprocess(df)

def preprocess(df):

    # Convert to datetime (auto-detect format or assume day first)
    df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True, errors='coerce')
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True, errors='coerce')

    
    # Calculate Order Processing Time (Lead Time)
    df['Order Processing Time'] = (df['Ship Date'] - df['Order Date']).dt.days
    
    # Standard SLA days for each Ship Mode (adjust if needed)
    sla_map = {
        'Same Day': 1,
        'First Class': 2,
        'Second Class': 4,
        'Standard Class': 5
    }
    df['Standard SLA Days'] = df['Ship Mode'].map(sla_map).fillna(999)
    
    # Late Flag
    df['Is Late'] = df['Order Processing Time'] > df['Standard SLA Days']
    
    # Profit Margin
    df['Profit Margin'] = df['Profit'] / df['Sales'].replace({0: np.nan})
    
    # Month column for time-based charts
    df['order_month'] = df['Order Date'].dt.to_period('M').dt.to_timestamp()
    
    return df

# -------------------- STREAMLIT UI --------------------

st.set_page_config(page_title="Supply Chain Dashboard", layout="wide")
st.title("📦 Supply Chain & Business Performance Dashboard")

# Sidebar - Filters
st.sidebar.header("Filters")
data_path = st.sidebar.text_input("CSV File Path","Refined and Cleansed_Supply_Chain_Data.csv")

# Load data
try:
    df = load_data(data_path)
except FileNotFoundError:
    st.error("File not found. Please check the CSV path in the sidebar.")
    st.stop()

# Filter options
min_date = df['Order Date'].min().date()
max_date = df['Order Date'].max().date()
date_range = st.sidebar.date_input("Order Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

regions = st.sidebar.multiselect("Region", options=sorted(df['Region'].dropna().unique()), default=sorted(df['Region'].unique()))
ship_modes = st.sidebar.multiselect("Ship Mode", options=sorted(df['Ship Mode'].dropna().unique()), default=sorted(df['Ship Mode'].unique()))

# Apply filters
mask = (
    (df['Order Date'].dt.date >= date_range[0]) &
    (df['Order Date'].dt.date <= date_range[1]) &
    (df['Region'].isin(regions)) &
    (df['Ship Mode'].isin(ship_modes))
)
df_filtered = df[mask]

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Supply Chain & Fulfillment",
    "Financial Performance",
    "Product & Inventory",
    "Customer & Regional"
])

# -------------------- TAB 1: SUPPLY CHAIN --------------------
with tab1:
    st.subheader("🚚 Supply Chain & Fulfillment Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Avg Order Processing (Days)", round(df_filtered['Order Processing Time'].mean(), 2))
    col2.metric("Total Orders", int(df_filtered['Order ID'].nunique()))
    late_orders = int(df_filtered['Is Late'].sum())
    col3.metric("Total Late Orders", late_orders)
    late_pct = 100 * late_orders / max(1, df_filtered.shape[0])
    col4.metric("Late Order %", f"{late_pct:.1f}%")
    
    # Line Chart: Avg processing time over time
    monthly = df_filtered.groupby('order_month')['Order Processing Time'].mean().reset_index()
    fig1 = px.line(monthly, x='order_month', y='Order Processing Time', markers=True,
                   title="Average Order Processing Time Over Time")
    st.plotly_chart(fig1, use_container_width=True)
    
    # Bar Chart: Avg processing time by Ship Mode
    mode_avg = df_filtered.groupby('Ship Mode')['Order Processing Time'].mean().reset_index()
    fig2 = px.bar(mode_avg, x='Ship Mode', y='Order Processing Time',
                  title="Average Processing Time by Ship Mode", color='Order Processing Time')
    st.plotly_chart(fig2, use_container_width=True)
    
    # Bar Chart: Order count by Priority
    pri = df_filtered.groupby('Order Priority').agg(
        Order_Count=('Order ID', 'nunique'),
        Avg_Time=('Order Processing Time', 'mean')
    ).reset_index()
    fig3 = px.bar(pri, x='Order Priority', y='Order_Count', color='Avg_Time',
                  title="Order Count by Order Priority (Color: Avg Processing Time)")
    st.plotly_chart(fig3, use_container_width=True)

# -------------------- TAB 2: FINANCIAL PERFORMANCE --------------------
with tab2:
    st.subheader("💰 Financial Performance Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Sales", f"${df_filtered['Sales'].sum():,.0f}")
    col2.metric("Total Profit", f"${df_filtered['Profit'].sum():,.0f}")
    col3.metric("Profit Margin", f"{(df_filtered['Profit'].sum() / max(1, df_filtered['Sales'].sum())):.2%}")
    col4.metric("Avg Discount", f"{df_filtered['Discount'].mean():.2%}")
    
    # Line Chart: Sales vs Profit Over Time
    time_agg = df_filtered.groupby('order_month')[['Sales', 'Profit']].sum().reset_index()
    fig4 = px.line(time_agg, x='order_month', y=['Sales', 'Profit'],
                   title="Sales vs Profit Over Time")
    st.plotly_chart(fig4, use_container_width=True)
    
    # Scatter: Discount vs Profit by Sub-Category
    disc_prof = df_filtered.groupby('Sub-Category').agg(
        avg_discount=('Discount', 'mean'),
        total_profit=('Profit', 'sum')
    ).reset_index()
    fig5 = px.scatter(disc_prof, x='avg_discount', y='total_profit', color='total_profit',
                      size='total_profit', hover_name='Sub-Category',
                      title="Discount vs Profit by Sub-Category")
    st.plotly_chart(fig5, use_container_width=True)
    
    # Bar: Shipping Cost by Ship Mode
    ship_cost = df_filtered.groupby('Ship Mode')['Shipping_Cost'].sum().reset_index()
    fig6 = px.bar(ship_cost, x='Ship Mode', y='Shipping_Cost',
                  title="Total Shipping Cost by Ship Mode", color='Shipping_Cost')
    st.plotly_chart(fig6, use_container_width=True)

# -------------------- TAB 3: PRODUCT & INVENTORY --------------------
with tab3:
    st.subheader("📦 Product & Inventory Analysis")
    
    prod_agg = df_filtered.groupby('Product Name').agg(
        Sales=('Sales', 'sum'),
        Profit=('Profit', 'sum'),
        Quantity=('Quantity', 'sum')
    ).reset_index()
    
    best_selling = prod_agg.sort_values('Sales', ascending=False).head(1)
    most_profitable = prod_agg.sort_values('Profit', ascending=False).head(1)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Best Selling Product", best_selling['Product Name'].values[0] if not best_selling.empty else "N/A")
    col2.metric("Most Profitable Product", most_profitable['Product Name'].values[0] if not most_profitable.empty else "N/A")
    col3.metric("Total Quantity Sold", int(prod_agg['Quantity'].sum()))
    
    # Top 10 products by Sales
    top10_sales = prod_agg.sort_values('Sales', ascending=True).tail(10)
    fig7 = px.bar(top10_sales, x='Sales', y='Product Name', orientation='h', title="Top 10 Products by Sales")
    st.plotly_chart(fig7, use_container_width=True)
    
    # Bottom 10 products by Profit
    bottom10_profit = prod_agg.sort_values('Profit', ascending=True).head(10)
    fig8 = px.bar(bottom10_profit, x='Profit', y='Product Name', orientation='h',
                  title="Bottom 10 Products by Profit")
    st.plotly_chart(fig8, use_container_width=True)
    
    # Treemap: Sales by Category & Sub-Category
    cat_tree = df_filtered.groupby(['Category', 'Sub-Category']).agg(
        Sales=('Sales', 'sum'),
        Profit=('Profit', 'sum')
    ).reset_index()
    fig9 = px.treemap(cat_tree, path=['Category', 'Sub-Category'], values='Sales',
                      color='Profit', title="Sales by Category and Sub-Category")
    st.plotly_chart(fig9, use_container_width=True)
    
    # Scatter: Sales vs Profit by Product
    fig10 = px.scatter(prod_agg, x='Sales', y='Profit', size='Sales', hover_name='Product Name',
                       title="Sales vs Profit by Product")
    st.plotly_chart(fig10, use_container_width=True)

# -------------------- TAB 4: CUSTOMER & REGIONAL --------------------
with tab4:
    st.subheader("🌎 Customer & Regional Dashboard")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Customers", df_filtered['Customer ID'].nunique())
    
    top_cust = df_filtered.groupby('Customer Name')['Sales'].sum().reset_index().sort_values('Sales', ascending=False).head(1)
    top_region = df_filtered.groupby('Region')['Sales'].sum().reset_index().sort_values('Sales', ascending=False).head(1)
    
    col2.metric("Top Customer", f"{top_cust.iloc[0]['Customer Name']} (${top_cust.iloc[0]['Sales']:.0f})" if not top_cust.empty else "N/A")
    col3.metric("Top Region", f"{top_region.iloc[0]['Region']} (${top_region.iloc[0]['Sales']:.0f})" if not top_region.empty else "N/A")
    
    # Donut: Sales by Segment
    seg = df_filtered.groupby('Segment')['Sales'].sum().reset_index()
    fig11 = px.pie(seg, names='Segment', values='Sales', hole=0.45, title="Sales by Segment")
    st.plotly_chart(fig11, use_container_width=True)
    
    # Top 10 Customers by Profit
    top_cust_profit = df_filtered.groupby('Customer Name')['Profit'].sum().reset_index().sort_values('Profit', ascending=False).head(10)
    fig12 = px.bar(top_cust_profit, x='Profit', y='Customer Name', orientation='h', title="Top 10 Customers by Profit")
    st.plotly_chart(fig12, use_container_width=True)
    
    # Stacked Bar: Sales by Region & Segment
    reg_seg = df_filtered.groupby(['Region', 'Segment'])['Sales'].sum().reset_index()
    fig13 = px.bar(reg_seg, x='Region', y='Sales', color='Segment', title="Sales by Region and Segment")
    st.plotly_chart(fig13, use_container_width=True)
