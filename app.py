import streamlit as st
import pandas as pd
import os

# Set up wide layout before any Streamlit widgets
st.set_page_config(layout="wide", page_title="MDOT Price Explorer")

@st.cache_data
def load_data():
    # Load from local file in your GitHub repo
    return pd.read_parquet("combined_mdot_bid_data.parquet")

# Load and preprocess data
df = load_data()

# Extract county code and map it to county name
county_map = {
    "01": "Alcona", "02": "Alger", "03": "Allegan", "04": "Alpena", "05": "Antrim",
    "06": "Arenac", "07": "Baraga", "08": "Barry", "09": "Bay", "10": "Benzie",
    "11": "Berrien", "12": "Branch", "13": "Calhoun", "14": "Cass", "15": "Charlevoix",
    "16": "Cheboygan", "17": "Chippewa", "18": "Clare", "19": "Clinton", "20": "Crawford",
    "21": "Delta", "22": "Dickinson", "23": "Eaton", "24": "Emmet", "25": "Genesee",
    "26": "Gladwin", "27": "Gogebic", "28": "Grand Traverse", "29": "Gratiot", "30": "Hillsdale",
    "31": "Houghton", "32": "Huron", "33": "Ingham", "34": "Ionia", "35": "Iosco",
    "36": "Iron", "37": "Isabella", "38": "Jackson", "39": "Kalamazoo", "40": "Kalkaska",
    "41": "Kent", "42": "Keweenaw", "43": "Lake", "44": "Lapeer", "45": "Leelanau",
    "46": "Lenawee", "47": "Livingston", "48": "Luce", "49": "Mackinac", "50": "Macomb",
    "51": "Manistee", "52": "Marquette", "53": "Mason", "54": "Mecosta", "55": "Menominee",
    "56": "Midland", "57": "Missaukee", "58": "Monroe", "59": "Montcalm", "60": "Montmorency",
    "61": "Muskegon", "62": "Newaygo", "63": "Oakland", "64": "Oceana", "65": "Ogemaw",
    "66": "Ontonagon", "67": "Osceola", "68": "Oscoda", "69": "Otsego", "70": "Ottawa",
    "71": "Presque Isle", "72": "Roscommon", "73": "Saginaw", "74": "St. Clair", "75": "St. Joseph",
    "76": "Sanilac", "77": "Schoolcraft", "78": "Shiawassee", "79": "Tuscola", "80": "Van Buren",
    "81": "Washtenaw", "82": "Wayne", "83": "Detroit City", "84": "Wexford"
}

df["County Code"] = df["Proposal ID"].astype(str).str[:2].str.zfill(2)
df["County"] = df["County Code"].map(county_map)
df["Letting Date"] = pd.to_datetime(df["Letting Date"]).dt.date

st.title("MDOT Pay Item Price Explorer")

if st.button("🔄 Reset Filters"):
    st.rerun()

# --- Search input ---
descriptions = sorted(df["Item Description/Supplemental Description"].dropna().unique())
selected_description = st.selectbox(
    "Select Pay Item Description (start typing):",
    options=[""] + descriptions,
    index=0
)

# --- Quantity slider ---
min_qty = int(df["Quantity"].min())
max_qty = int(df["Quantity"].max())

if selected_description:
    item_data = df[df["Item Description/Supplemental Description"] == selected_description]

    if not item_data.empty:
        min_qty = int(item_data["Quantity"].min())
        max_qty = int(item_data["Quantity"].max())

        if min_qty == max_qty:
            min_qty = int(min_qty * 0.9)
            max_qty = int(max_qty * 1.1) + 1

        qty_range = st.slider(
            "Quantity Range (Auto-scaled to item)",
            min_value=min_qty,
            max_value=max_qty,
            value=(min_qty, max_qty),
            key="qty_slider"
        )

        filtered_preview = item_data[item_data["Quantity"].between(qty_range[0], qty_range[1])]
        if filtered_preview.empty:
            st.warning("⚠️ No matching records for this quantity range.")
            st.stop()
    else:
        st.warning("⚠️ No data found for this pay item.")
        st.stop()
else:
    qty_range = st.slider(
        "Quantity Range (All items)",
        min_value=min_qty,
        max_value=max_qty,
        value=(min_qty, max_qty),
        key="qty_slider_all"
    )

# --- Lowest bidder checkbox ---
lowest_only = st.checkbox("Only include lowest bidder (Vend Rank = 1)?", value=True)

# --- Letting date range slider ---
min_date = min(df["Letting Date"])
max_date = max(df["Letting Date"])
date_range = st.slider(
    "Letting Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date)
)

# --- County filter ---
available_counties = sorted(df["County"].dropna().unique())
selected_counties = st.multiselect("Filter by County (optional):", options=available_counties)

# --- Filter data ---
filtered = df.copy()

if selected_description:
    filtered = filtered[filtered["Item Description/Supplemental Description"] == selected_description]

filtered = filtered[filtered["Quantity"].between(qty_range[0], qty_range[1])]
filtered = filtered[filtered["Letting Date"].between(date_range[0], date_range[1])]

if lowest_only:
    filtered = filtered[filtered["Vend Rank"] == 1]

if selected_counties:
    filtered = filtered[filtered["County"].isin(selected_counties)]

# ✅ Handle no match
if filtered.empty:
    st.warning("⚠️ No matching records found. Please adjust your filters.")
    st.stop()

# --- Display results ---
st.subheader("Filtered Results")
st.write(f"🔎 Matches: {len(filtered)}")

total_quantity = filtered["Quantity"].sum()
weighted_avg = (filtered["Bid Price"] * filtered["Quantity"]).sum() / total_quantity if total_quantity else None

st.write(f"📊 Average Unit Price: ${filtered['Bid Price'].mean():.2f}")
if weighted_avg is not None:
    st.write(f"📦 Weighted Average Unit Price: ${weighted_avg:.2f}")
st.write(f"💲 Min: ${filtered['Bid Price'].min():.2f} | Max: ${filtered['Bid Price'].max():.2f}")

st.dataframe(filtered[[
    'County',
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
