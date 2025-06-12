import streamlit as st
import pandas as pd

# Set up wide layout before any Streamlit widgets
st.set_page_config(layout="wide", page_title="MDOT Price Explorer")



@st.cache_data

def load_data():
    #For Local Run#return pd.read_csv("combined_mdot_bid_data.csv", parse_dates=["Letting Date"])
    url = "https://drive.google.com/uc?export=download&id=11Qr5RbIr0Ym0nEjKpMJY36w_BmtCqV51"
    return pd.read_csv(url, parse_dates=["Letting Date"])

# Load and preprocess data
df = load_data()
df["Letting Date"] = pd.to_datetime(df["Letting Date"]).dt.date

st.title("MDOT Pay Item Price Explorer")

if st.button("🔄 Reset Filters"):
    st.rerun()

# --- Search input ---
# Get sorted list of unique item descriptions
descriptions = sorted(df["Item Description/Supplemental Description"].dropna().unique())

# Autocomplete-style dropdown
selected_description = st.selectbox(
    "Select Pay Item Description (start typing):",
    options=[""] + descriptions,  # Add empty string to allow 'all'
    index=0
)


# --- Quantity slider ---
min_qty = int(df["Quantity"].min())
max_qty = int(df["Quantity"].max())
if selected_description:
    item_data = df[df["Item Description/Supplemental Description"] == selected_description]
    min_qty = int(item_data["Quantity"].min())
    max_qty = int(item_data["Quantity"].max())

    if min_qty == max_qty:
        min_qty = int(min_qty * 0.9)
        max_qty = int(max_qty * 1.1) + 1  # Add 1 to avoid same value

    qty_range = st.slider(
        "Quantity Range (Auto-scaled to item)",
        min_value=min_qty,
        max_value=max_qty,
        value=(min_qty, max_qty)
    )

else:
    qty_range = st.slider(
        "Quantity Range (All items)",
        min_value=int(df["Quantity"].min()),
        max_value=int(df["Quantity"].max()),
        value=(int(df["Quantity"].min()), int(df["Quantity"].max()))
    )


# --- Lowest bidder checkbox ---
lowest_only = st.checkbox("Only include lowest bidder (Vend Rank = 1)?", value=True)

# --- Letting date range slider ---
min_date = min(df["Letting Date"])
max_date = max(df["Letting Date"])
date_range = st.slider("Letting Date Range", min_value=min_date, max_value=max_date, value=(min_date, max_date))

# --- Filter data ---
filtered = df.copy()
if selected_description:
    filtered = filtered[filtered["Item Description/Supplemental Description"] == selected_description]
filtered = filtered[filtered["Quantity"].between(qty_range[0], qty_range[1])]
filtered = filtered[filtered["Letting Date"].between(date_range[0], date_range[1])]
if lowest_only:
    filtered = filtered[filtered["Vend Rank"] == 1]

# --- Display results ---
if not filtered.empty:
    st.subheader("Filtered Results")
    st.write(f"🔎 Matches: {len(filtered)}")

    # Calculate weighted average
    total_quantity = filtered["Quantity"].sum()
    weighted_avg = (filtered["Bid Price"] * filtered["Quantity"]).sum() / total_quantity if total_quantity else None

    # Show average, weighted average, min, max
    st.write(f"📊 Average Unit Price: ${filtered['Bid Price'].mean():.2f}")
    if weighted_avg is not None:
        st.write(f"📦 Weighted Average Unit Price: ${weighted_avg:.2f}")
    st.write(f"💲 Min: ${filtered['Bid Price'].min():.2f} | Max: ${filtered['Bid Price'].max():.2f}")

    # Show data table
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
else:
    st.warning("No matching records found.")

