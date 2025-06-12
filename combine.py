import pandas as pd
import os

folder_path = "xlsx"  # Folder with all Excel files
all_data = []

for filename in os.listdir(folder_path):
    if filename.endswith(".xlsx"):
        file_path = os.path.join(folder_path, filename)
        try:
            df = pd.read_excel(file_path, sheet_name='Sheet1')
            df['Source File'] = filename
            df['Letting Date'] = pd.to_datetime(filename.replace('.xlsx', ''), errors='coerce')
            all_data.append(df)
        except Exception as e:
            print(f"Error reading {filename}: {e}")

# Combine all data
df = pd.concat(all_data, ignore_index=True)

# Clean numeric columns
df['Quantity'] = df['Quantity'].replace(',', '', regex=True).astype(float)
df['Bid Price'] = df['Bid Price'].replace(r'[\$,]', '', regex=True).astype(float)
df['Ext Amount'] = df['Ext Amount'].replace(r'[\$,]', '', regex=True).astype(float)
df['Vend Rank'] = pd.to_numeric(df['Vend Rank'], errors='coerce').fillna(-1).astype(int)

# Save to CSV for Streamlit or Excel use
df.to_csv("combined_mdot_bid_data.csv", index=False)
print("✅ Combined data saved as 'combined_mdot_bid_data.csv'")
