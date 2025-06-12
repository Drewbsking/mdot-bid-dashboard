import pandas as pd

# Load your large CSV
df = pd.read_csv("combined_mdot_bid_data.csv", parse_dates=["Letting Date"])

# Save as Parquet
df.to_parquet("combined_mdot_bid_data.parquet", index=False)
