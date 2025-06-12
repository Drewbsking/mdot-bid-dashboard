import pandas as pd
import os
from datetime import datetime, timedelta

folder_path = "xlsx"  # Folder with all Excel files
all_data = []

# Get today's date and cutoff date (5 years ago)
today = datetime.today()
cutoff_date = today.replace(year=today.year - 5)

for filename in os.listdir(folder_path):
    if filename.endswith(".xlsx"):
        try:
            # Try to extract date from filename
            letting_date = pd.to_datetime(filename.replace('.xlsx', ''), errors='coerce')

            # Skip if date is invalid or too old
            if pd.isna(letting_date) or letting_date < cutoff_date:
                continue

            file_path = os.path.join(folder_path, filename)
            df = pd.read_excel(file_path, sheet_name='Sheet1')
            df['Source File'] = filename
            df['Letting Date'] = letting_date
            all_data.append(df)

        except Exception as e:
            print(f"Error reading {filename}: {e}")

# Combine all data
if all_data:
    df = pd.concat(all_data, ignore_index=True)

    # Clean numeric columns
    df['Quantity'] = df['Quantity'].replace(',', '', regex=True).astype(float)
    df['Bid Price'] = df['Bid Price'].replace(r'[\$,]', '', regex=True).astype(float)
    df['Ext Amount'] = df['Ext Amount'].replace(r'[\$,]', '', regex=True).astype(float)
    df['Vend Rank'] = pd.to_numeric(df['Vend Rank'], errors='coerce').fillna(-1).astype(int)

    # Save to CSV for Streamlit or Excel use
    df.to_csv("combined_mdot_bid_data.csv", index=False)
    print("✅ Combined data saved as 'combined_mdot_bid_data.csv'")
else:
    print("⚠️ No valid files found within the last 5 years.")
