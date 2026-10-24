
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
file_path = ROOT / "data" / "telangana_2023_candidates_clean.csv"

df = pd.read_csv(file_path)

df["TOTAL"] = pd.to_numeric(df["TOTAL"], errors="coerce")
df["PARTY"] = df["PARTY"].astype(str).str.strip()

print("=== ORIGINAL PARTY LABELS RELATED TO BRS ===")

related = df[
    df["PARTY"].str.upper().isin(["BRS", "TRS", "BHRS"])
]

summary = (
    related.groupby("PARTY")
    .agg(
        Candidate_Records=("TOTAL", "size"),
        Total_Votes=("TOTAL", "sum")
    )
    .reset_index()
)

print(summary.to_string(index=False))

print("\n=== NORMALIZED BRS TOTAL ===")
print("Candidate records:", len(related))
print("Total votes:", int(related["TOTAL"].sum()))

print("\n=== MISSING VOTE TOTALS ===")
print("Missing TOTAL values:", int(related["TOTAL"].isna().sum()))

print("\n=== DUPLICATE RECORD CHECK ===")

duplicate_columns = [
    "AC NO.",
    "AC NAME",
    "CANDIDATE NAME",
    "PARTY",
]

duplicates = related[
    related.duplicated(
        subset=duplicate_columns,
        keep=False
    )
].sort_values(duplicate_columns)

print("Potential duplicate records:", len(duplicates))

if not duplicates.empty:
    print(duplicates[duplicate_columns + ["TOTAL"]].to_string(index=False))

print("\n=== CONSTITUENCY-LEVEL BRS VOTES ===")

constituency_totals = (
    related.groupby(["AC NO.", "AC NAME"], as_index=False)["TOTAL"]
    .sum()
    .sort_values("AC NO.")
)

print(constituency_totals.to_string(index=False))

print("\nDiagnostic completed.")
