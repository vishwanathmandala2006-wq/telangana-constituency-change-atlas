import pandas as pd

# 1. Load the original report
file_path = "data/telangana_2023_raw.xlsx"
df = pd.read_excel(file_path, header=3)

print("Original rows:", len(df))

# 2. Keep rows that identify actual constituency candidate records
clean_df = df[
    df["AC NO."].notna()
    & df["AC NAME"].notna()
    & df["CANDIDATE NAME"].notna()
].copy()

# 3. Convert numerical columns to appropriate numeric types
numeric_columns = [
    "AC NO.",
    "GENERAL",
    "POSTAL",
    "TOTAL",
    "% VOTES POLLED",
    "TOTAL ELECTORS",
]

for column in numeric_columns:
    clean_df[column] = pd.to_numeric(
        clean_df[column], errors="coerce"
    )

clean_df["AC NO."] = clean_df["AC NO."].astype(int)

# 4. Check the cleaned dataset
print("\nCleaned rows:", len(clean_df))
print("Unique constituencies:", clean_df["AC NAME"].nunique())
print("Missing values in key columns:")
print(
    clean_df[
        ["AC NO.", "AC NAME", "CANDIDATE NAME", "PARTY", "TOTAL"]
    ].isna().sum()
)

# 5. Save a separate cleaned dataset
output_path = "data/telangana_2023_candidates_clean.csv"
clean_df.to_csv(output_path, index=False)

print("\nSaved cleaned dataset to:", output_path)
print("\nPreview:")
print(
    clean_df[
        ["AC NO.", "AC NAME", "CANDIDATE NAME", "PARTY", "TOTAL"]
    ].head(10).to_string(index=False)
)

# Exclude NOTA when identifying candidates in the contest
contestants = clean_df[
    clean_df["PARTY"].str.strip().str.upper() != "NOTA"
].copy()

# Sort candidates by votes within each constituency
ranked = contestants.sort_values(
    ["AC NO.", "TOTAL"],
    ascending=[True, False]
)

# Select the top two candidates in each constituency
top_two = ranked.groupby("AC NO.", sort=False).head(2).copy()

top_two["Rank"] = (
    top_two.groupby("AC NO.").cumcount() + 1
)

# Convert the top-two rows into one row per constituency
leaders = top_two.pivot(
    index=["AC NO.", "AC NAME"],
    columns="Rank",
    values=["CANDIDATE NAME", "PARTY", "TOTAL"]
)

leaders.columns = [
    f"{field}_{rank}" for field, rank in leaders.columns
]

leaders = leaders.reset_index()

leaders["Winning Margin"] = (
    leaders["TOTAL_1"] - leaders["TOTAL_2"]
)

print("\nSample constituency results:")
print(
    leaders[
        [
            "AC NAME",
            "CANDIDATE NAME_1",
            "PARTY_1",
            "TOTAL_1",
            "CANDIDATE NAME_2",
            "PARTY_2",
            "TOTAL_2",
            "Winning Margin",
        ]
    ].head(10).to_string(index=False)
)

leaders.to_csv(
    "outputs/telangana_2023_constituency_results.csv",
    index=False
)