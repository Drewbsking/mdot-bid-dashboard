import streamlit as st
import pandas as pd

# --- Basic Page Setup ---
st.set_page_config(layout="wide", page_title="MDOT Price Explorer")

# --- Page Title ---
st.title("MDOT Pay Item Price Explorer")

# --- Load Data ---
def load_data():
    return pd.read_parquet("combined_mdot_bid_data.parquet")

df = load_data()
df["Letting Date"] = pd.to_datetime(df["Letting Date"]).dt.date

# --- Reset Button ---
if st.button("🔄 Reset Filters"):
    st.rerun()

# --- County Filter ---
county_map = {
    "Alcona": 1, "Alger": 2, "Allegan": 3, "Alpena": 4, "Antrim": 5, "Arenac": 6, "Baraga": 7, "Barry": 8,
    "Bay": 9, "Benzie": 10, "Berrien": 11, "Branch": 12, "Calhoun": 13, "Cass": 14, "Charlevoix": 15,
    "Cheboygan": 16, "Chippewa": 17, "Clare": 18, "Clinton": 19, "Crawford": 20, "Delta": 21, "Dickinson": 22,
    "Eaton": 23, "Emmet": 24, "Genesee": 25, "Gladwin": 26, "Gogebic": 27, "Grand Traverse": 28, "Gratiot": 29,
    "Hillsdale": 30, "Houghton": 31, "Huron": 32, "Ingham": 33, "Ionia": 34, "Iosco": 35, "Iron": 36,
    "Isabella": 37, "Jackson": 38, "Kalamazoo": 39, "Kalkaska": 40, "Kent": 41, "Keweenaw": 42, "Lake": 43,
    "Lapeer": 44, "Leelanau": 45, "Lenawee": 46, "Livingston": 47, "Luce": 48, "Mackinac": 49, "Macomb": 50,
    "Manistee": 51, "Marquette": 52, "Mason": 53, "Mecosta": 54, "Menominee": 55, "Midland": 56,
    "Missaukee": 57, "Monroe": 58, "Montcalm": 59, "Montmorency": 60, "Muskegon": 61, "Newaygo": 62,
    "Oakland": 63, "Oceana": 64, "Ogemaw": 65, "Ontonagon": 66, "Osceola": 67, "Oscoda": 68, "Otsego": 69,
    "Ottawa": 70, "Presque Isle": 71, "Roscommon": 72, "Saginaw": 73, "St. Clair": 74, "St. Joseph": 75,
    "Sanilac": 76, "Schoolcraft": 77, "Shiawassee": 78, "Tuscola": 79, "Van Buren": 80, "Washtenaw": 81,
    "Wayne": 82, "Detroit City": 83, "Wexford": 84
}

default_counties = [
    "Livingston", "Macomb", "Monroe", "Oakland", "St. Clair", "Washtenaw", "Wayne", "Lapeer", "Genesee"
]

county_names = sorted(county_map.keys())
selected_counties = st.multiselect(
    "Select Counties (based on Proposal ID):",
    options=county_names,
    default=default_counties
)

if selected_counties:
    county_codes = [f"{county_map[c]:02d}" for c in selected_counties]
    df = df[df["Proposal ID"].astype(str).str[:2].isin(county_codes)]

# --- Item Description Filter ---
descriptions = sorted(df["Item Description/Supplemental Description"].dropna().unique())
selected_description = st.selectbox(
    "Select Pay Item Description (start typing):",
    options=[""] + descriptions,
    index=0
)

# --- Quantity Filter ---
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

# --- Vendor Rank Filter ---
lowest_only = st.checkbox("Only include lowest bidder (Vend Rank = 1)?", value=True)

# --- Letting Date Filter ---
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

# --- Summary Stats ---
total_quantity = filtered["Quantity"].sum()
weighted_avg = (filtered["Bid Price"] * filtered["Quantity"]).sum() / total_quantity if total_quantity else None

st.write(f"📊 Average Unit Price: ${filtered['Bid Price'].mean():.2f}")
if weighted_avg:
    st.write(f"📦 Weighted Average Unit Price: ${weighted_avg:.2f}")
st.write(f"💲 Min: ${filtered['Bid Price'].min():.2f} | Max: ${filtered['Bid Price'].max():.2f}")

# --- Data Table ---
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

# --- Footer ---
st.markdown("---")
st.markdown("**Questions, bugs, or feature requests? Contact Andrew Bates.**")
