import streamlit as st
import pandas as pd

# --- Page Setup ---
st.set_page_config(layout="wide", page_title="MDOT Price Explorer")
st.markdown("_Use the sidebar (👈) for filter options._")
st.title("🛣️ MDOT Pay Item Price Explorer")


# --- Load Data ---
@st.cache_data
def load_data():
    return pd.read_parquet("combined_mdot_bid_data.parquet")

df = load_data()
df["Letting Date"] = pd.to_datetime(df["Letting Date"]).dt.date

# --- Load RCOC Proposal IDs ---
try:
    with open("rcocProjects.txt", "r") as f:
        rcoc_ids = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    rcoc_ids = []
    st.warning("⚠️ RCOC project file not found.")

# --- Sidebar Filters ---
with st.sidebar:
    st.header("🔎 Filter Options")

    if st.button("🔄 Reset Filters"):
        st.rerun()

    # County Filter
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

    selected_counties = st.multiselect(
        "Select Counties (Default: SEMCOG region, inclusive of MDOT Metro, plus Lapeer and Genesee):",
        options=sorted(county_map.keys()),
        default=default_counties
    )

    if selected_counties:
        county_codes = [f"{county_map[c]:02d}" for c in selected_counties]
        df = df[df["Proposal ID"].astype(str).str[:2].isin(county_codes)]

    # Item Filter
    descriptions = sorted(df["Item Description/Supplemental Description"].dropna().unique())
    selected_description = st.selectbox(
        "Pay Item Description:",
        options=[""] + descriptions,
        index=0
    )

    # Add text input for search
    search_term = st.text_input("Search Pay Item Descriptions (contains term):").strip()

    # Vendor Rank Filter
    lowest_only = st.checkbox("Only include lowest bidder (Vend Rank = 1)?", value=True)

    # RCOC Filter
    show_rcoc_only = st.checkbox("Only include RCOC projects?")

    if show_rcoc_only and rcoc_ids:
        all_rcoc_ids_set = set(rcoc_ids)
        matched_rcoc_ids = sorted(set(df["Proposal ID"]).intersection(all_rcoc_ids_set))
        unmatched_rcoc_ids = sorted(all_rcoc_ids_set - set(matched_rcoc_ids))

        st.markdown("📋 **RCOC Proposal Check**")
        if matched_rcoc_ids:
            st.markdown(f"✅ **Matched Proposals ({len(matched_rcoc_ids)}):**")
            for pid in matched_rcoc_ids:
                st.markdown(f"- `{pid}`")
        else:
            st.markdown("❌ No RCOC projects matched current dataset.")

        if unmatched_rcoc_ids:
            with st.expander(f"📄 Unmatched Proposal IDs ({len(unmatched_rcoc_ids)})"):
                for pid in unmatched_rcoc_ids:
                    st.markdown(f"- `{pid}`")

# --- Filter Data ---
if selected_description:
    # Dropdown exact match takes priority
    item_data = df[df["Item Description/Supplemental Description"] == selected_description]
elif search_term:
    # If no dropdown selected, use search term
    item_data = df[df["Item Description/Supplemental Description"].str.contains(search_term, case=False, na=False)]
else:
    # No filter applied — show everything
    item_data = df.copy()


# Quantity Range
min_qty = int(item_data["Quantity"].min())
max_qty = int(item_data["Quantity"].max())
if min_qty == max_qty:
    min_qty = int(min_qty * 0.9)
    max_qty = int(max_qty * 1.1) + 1

qty_range = st.slider("📦 Quantity Range", min_value=min_qty, max_value=max_qty, value=(min_qty, max_qty))

# Letting Date
min_date = df["Letting Date"].min()
max_date = df["Letting Date"].max()
date_range = st.slider("📅 Letting Date Range", min_value=min_date, max_value=max_date, value=(min_date, max_date))

# --- Apply Filters ---
filtered = item_data[
    item_data["Quantity"].between(qty_range[0], qty_range[1]) &
    item_data["Letting Date"].between(date_range[0], date_range[1])
]

if lowest_only:
    filtered = filtered[filtered["Vend Rank"] == 1]

if show_rcoc_only and rcoc_ids:
    all_rcoc_ids_set = set(rcoc_ids)
    filtered = filtered[filtered["Proposal ID"].isin(all_rcoc_ids_set)]

# --- Display Results ---
if filtered.empty:
    st.warning("⚠️ No matching records found. Please adjust your filters.")
    st.stop()

st.subheader("📊 Filtered Results")
st.write(f"🔎 Matches: {len(filtered)}")

# Summary Stats
total_quantity = filtered["Quantity"].sum()
weighted_avg = (filtered["Bid Price"] * filtered["Quantity"]).sum() / total_quantity if total_quantity else None

col1, col2, col3 = st.columns(3)
col1.metric("Average Unit Price", f"${filtered['Bid Price'].mean():,.2f}")
col2.metric("Weighted Avg Price", f"${weighted_avg:,.2f}" if weighted_avg else "N/A")
col3.metric("Min / Max", f"${filtered['Bid Price'].min():,.2f} / ${filtered['Bid Price'].max():,.2f}")

# --- Data Table ---
display_df = filtered.copy()
display_df["Quantity"] = display_df["Quantity"].apply(lambda x: f"{x:,.0f}")
display_df["Bid Price"] = display_df["Bid Price"].apply(lambda x: f"${x:,.2f}")
display_df["Ext Amount"] = display_df["Ext Amount"].apply(lambda x: f"${x:,.2f}")

# Create CCI links for each Proposal ID
display_df["Proposal ID"] = display_df["Proposal ID"].apply(
    lambda pid: f'<a href="https://mdotjboss.state.mi.us/CCI/search.htm?selectedReportType=gcli&selectedPeriodType=1y&contractProjectNum={pid}" target="_blank">{pid}</a>'
)

# Choose columns to show
columns_to_display = [
    'Proposal ID',
    'Item Description/Supplemental Description',
    'Unit',
    'Quantity',
    'Bid Price',
    'Ext Amount',
    'Vendor Name',
    'Vend Rank',
    'Letting Date'
]

# Convert to HTML and show
st.write(display_df[columns_to_display].to_html(escape=False, index=False), unsafe_allow_html=True)




# --- Footer ---
st.markdown("---")
st.markdown("Questions, bugs, or feature requests? Contact Andrew Bates.")
st.markdown("_This tool is for informational purposes only and is not an official source for contract pricing or bid disputes._")
st.markdown(
    "[🗺️ Michigan Counties Map](https://www.michigan.gov/lara/bureau-list/bchs/adult/online-lookups/michigan-counties-map)"
)

