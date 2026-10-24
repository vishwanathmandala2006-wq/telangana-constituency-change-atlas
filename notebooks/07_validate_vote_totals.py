
import pandas as pd

# --------------------------------------------------
# 1. Load both candidate-level datasets
# --------------------------------------------------

df_2018 = pd.read_csv("data/telangana_2018_raw.csv")
df_2023 = pd.read_csv("data/telangana_2023_candidates_clean.csv")

# Convert vote counts to numeric values
df_2018["Votes"] = pd.to_numeric(df_2018["Votes"], errors="coerce")
df_2018["Valid_Votes"] = pd.to_numeric(
    df_2018["Valid_Votes"], errors="coerce"
)

df_2023["TOTAL"] = pd.to_numeric(df_2023["TOTAL"], errors="coerce")

# --------------------------------------------------
# 2. Validate 2018 constituency vote totals
# --------------------------------------------------

results_2018 = (
    df_2018.groupby(
        ["Constituency_No", "Constituency_Name"],
        as_index=False
    )
    .agg(
        Calculated_Votes=("Votes", "sum"),
        Reported_Valid_Votes=("Valid_Votes", "first"),
        Candidate_Count=("Candidate", "size")
    )
)

results_2018["Difference"] = (
    results_2018["Calculated_Votes"]
    - results_2018["Reported_Valid_Votes"]
)

mismatches_2018 = results_2018[
    results_2018["Difference"].abs() > 0.01
]

# --------------------------------------------------
# 3. Calculate 2023 constituency vote totals
# --------------------------------------------------

results_2023 = (
    df_2023.groupby(
        ["AC NO.", "AC NAME"],
        as_index=False
    )
    .agg(
        Calculated_Votes=("TOTAL", "sum"),
        Candidate_Count=("CANDIDATE NAME", "size"),
        Missing_Vote_Records=("TOTAL", lambda x: x.isna().sum())
    )
)

# --------------------------------------------------
# 4. Print validation results
# --------------------------------------------------

print("\n=== 2018 VOTE-TOTAL VALIDATION ===")
print("Constituencies:", len(results_2018))
print("Vote-total mismatches:", len(mismatches_2018))

if not mismatches_2018.empty:
    print("\nFirst mismatches:")
    print(
        mismatches_2018[
            [
                "Constituency_Name",
                "Calculated_Votes",
                "Reported_Valid_Votes",
                "Difference"
            ]
        ].head(10).to_string(index=False)
    )
else:
    print("All calculated totals match the reported Valid_Votes values.")

print("\n=== 2023 VOTE-TOTAL SUMMARY ===")
print("Constituencies:", len(results_2023))
print(
    "Missing vote records:",
    results_2023["Missing_Vote_Records"].sum()
)

print("\nFirst 10 constituency totals:")
print(results_2023.head(10).to_string(index=False))

print("\n=== VALIDATION NOTES ===")
print("2018 denominator: source Valid_Votes, checked against summed Votes.")
print("2023 denominator: sum of candidate-record TOTAL values.")
print("NOTA is retained in the candidate records where present.")
print("Denominators must be verified before interpreting vote-share changes.")
