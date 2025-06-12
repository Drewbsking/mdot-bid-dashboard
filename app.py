import streamlit as st
import pandas as pd

# --- Basic Page Setup ---
st.set_page_config(layout="wide", page_title="MDOT Price Explorer")

# --- Load Data (no cache) ---
def load_data():
    return pd.read_parquet("combined_mdot_bid_data.parquet")

df = load_data()
df["Letting Date"] = pd.to_datetime(df["Letting Date"]).dt.date

# --- Start Page ---
st.title("MDOT Pay Item Price Explorer")

# Reset Button
if st.button("🔄 Reset Filters"):
    st.rerun()

# --- Search Input ---
descriptions = sorted(df["Item Description/Supplemental Description"].dropna().unique())
selected_description = st.selectbox(
    "Select Pay Item Description (start typing):",
    options=[""] + descriptions,
    index=0
)

# --- Quantity Slider ---
if selected_description:
    item_data = df[df["Item Description/Supplemental Description"] == selected_description]
else:
    item_data = df.copy()

min_qty = int(item_data["Quantity"].min())
max_qty = int(item_data["Quantity"].max())

if min_qty == max_qty:
    min_qty = int(min_qty * 0.9)
    max_qty = int(max_qty * 1.1) + 1

qty_range = st.slider(
    "Quantity Range",
    min_value=min_qty,
    max_value=max_qty,
    value=(min_qty, max_qty)
)

# --- Lowest Bidder Filter ---
lowest_only = st.checkbox("Only include lowest bidder (Vend Rank = 1)?", value=True)

# --- Date Filter ---
min_date = df["Letting Date"].min()
max_date = df["Letting Date"].max()
date_range = st.slider(
    "Letting Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date)
)

# --- Apply Filters ---
filtered = item_data[
    item_data["Quantity"].between(qty_range[0], qty_range[1]) &
    item_data["Letting Date"].between(date_range[0], date_range[1])
]
if lowest_only:
    filtered = filtered[filtered["Vend Rank"] == 1]

# --- Display Results ---
if filtered.empty:
    st.warning("⚠️ No matching records found. Please adjust your filters.")
    st.stop()

st.subheader("Filtered Results")
st.write(f"🔎 Matches: {len(filtered)}")

# Summary Stats
total_quantity = filtered["Quantity"].sum()
weighted_avg = (filtered["Bid Price"] * filtered["Quantity"]).sum() / total_quantity if total_quantity else None

st.write(f"📊 Average Unit Price: ${filtered['Bid Price'].mean():.2f}")
if weighted_avg:
    st.write(f"📦 Weighted Average Unit Price: ${weighted_avg:.2f}")
st.write(f"💲 Min: ${filtered['Bid Price'].min():.2f} | Max: ${filtered['Bid Price'].max():.2f}")

st.dataframe(filtered[[
    'Proposal ID',
    'Item Description/Supplemental Description',
    'Unit',
    'Quantity',
    'Bid Price',
    'Ext Amount',
    'Vendor Name',
    'Vend Rank',
    'Letting Date'
]])
