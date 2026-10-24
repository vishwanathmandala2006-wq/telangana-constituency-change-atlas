
import pandas as pd
from pathlib import Path

# Load the verified 2018 dataset
file_path = Path("data/telangana_2018_raw.csv")
df = pd.read_csv(file_path)

print("Original rows:", len(df))
print("Columns:", df.columns.tolist())

# Display the fields needed for election analysis
print("\nFirst 5 rows:")
print(df.head().to_string())

print("\nMissing values in columns:")
print(df.isna().sum().sort_values(ascending=False).head(15))
