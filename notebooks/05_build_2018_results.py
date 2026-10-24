import pandas as pd
from pathlib import Path

# 1. Load the 2018 candidate-level dataset
input_path = Path("data/telangana_2018_raw.csv")
df = pd.read_csv(input_path)

print("Original candidate records:", len(df))

# 2. Convert relevant fields to numeric
numeric_columns = [
    "Constituency_No",
    "Position",
    "Votes",
    "Valid_Votes",
    "Electors",
    "Vote_Share_Percentage",
    "Turnout_Percentage",
    "Margin",
    "Margin_Percentage",
]

for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

# 3. Keep records with essential candidate and constituency information
candidates = df.dropna(
    subset=[
        "Constituency_No",
        "Constituency_Name",
        "Candidate",
        "Party",
        "Votes",
    ]
).copy()

candidates["Constituency_No"] = (
    candidates["Constituency_No"].astype(int)
)

# 4. Sort candidates by their recorded position
candidates = candidates.sort_values(
    ["Constituency_No", "Position", "Votes"],
    ascending=[True, True, False],
)

# 5. Select the winner and runner-up for each constituency
top_two = (
    candidates.groupby("Constituency_No", sort=False)
    .head(2)
    .copy()
)

top_two["Rank"] = (
    top_two.groupby("Constituency_No").cumcount() + 1
)

# 6. Reshape to one row per constituency
leaders = top_two.pivot(
    index=["Constituency_No", "Constituency_Name"],
    columns="Rank",
    values=["Candidate", "Party", "Votes"],
)

leaders.columns = [
    f"{field}_{rank}" for field, rank in leaders.columns
]

leaders = leaders.reset_index()

leaders = leaders.rename(
    columns={
        "Candidate_1": "Winner",
        "Party_1": "Winner Party Original",
        "Votes_1": "Winner Votes",
        "Candidate_2": "Runner Up",
        "Party_2": "Runner Up Party Original",
        "Votes_2": "Runner Up Votes",
    }
)

# 7. Calculate winning margin from candidate vote totals
leaders["Winning Margin"] = (
    leaders["Winner Votes"] - leaders["Runner Up Votes"]
)

# 8. Get one constituency-level record for turnout and valid votes
constituency_stats = (
    candidates.sort_values(["Constituency_No", "Position"])
    .drop_duplicates("Constituency_No")
    [
        [
            "Constituency_No",
            "Valid_Votes",
            "Electors",
            "Turnout_Percentage",
        ]
    ]
)

leaders = leaders.merge(
    constituency_stats,
    on="Constituency_No",
    how="left",
    validate="one_to_one",
)

# 9. Normalize party labels for comparison
def normalize_party(party):
    party = str(party).strip().upper()

    if party in {"TRS", "BHRS", "BRS"}:
        return "BRS"

    return party

leaders["Winner Party"] = leaders["Winner Party Original"].apply(
    normalize_party
)

leaders["Runner Up Party"] = leaders[
    "Runner Up Party Original"
].apply(normalize_party)

# 10. Validate results
print("\n=== VALIDATION ===")
print("Candidate records retained:", len(candidates))
print("Constituencies:", leaders["Constituency_No"].nunique())
print("Missing winner votes:", leaders["Winner Votes"].isna().sum())
print("Missing runner-up votes:", leaders["Runner Up Votes"].isna().sum())
print("Negative winning margins:", (leaders["Winning Margin"] < 0).sum())

# 11. Display sample results
print("\n=== SAMPLE 2018 RESULTS ===")
print(
    leaders[
        [
            "Constituency_No",
            "Constituency_Name",
            "Winner",
            "Winner Party",
            "Winner Votes",
            "Runner Up",
            "Runner Up Party",
            "Runner Up Votes",
            "Winning Margin",
        ]
    ].head(10).to_string(index=False)
)
# 11.5 Verify calculated margins against the source dataset

source_margins = (
    candidates.sort_values(["Constituency_No", "Position"])
    .drop_duplicates("Constituency_No")
    [["Constituency_No", "Margin"]]
    .rename(columns={"Margin": "Source Margin"})
)

leaders = leaders.merge(
    source_margins,
    on="Constituency_No",
    how="left",
    validate="one_to_one",
)

leaders["Margin Difference"] = (
    leaders["Winning Margin"] - leaders["Source Margin"]
)

mismatches = leaders[
    leaders["Margin Difference"].abs() > 0
]

print("\n=== MARGIN VERIFICATION ===")
print("Constituencies checked:", len(leaders))
print("Margin mismatches:", len(mismatches))

if not mismatches.empty:
    print(
        mismatches[
            [
                "Constituency_Name",
                "Winner",
                "Runner Up",
                "Winning Margin",
                "Source Margin",
                "Margin Difference",
            ]
        ].to_string(index=False)
    )
else:
    print("All calculated margins match the source margins.")

# 12. Save standardized results
output_path = Path("outputs/telangana_2018_constituency_results.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)

leaders.to_csv(output_path, index=False)

print("\nSaved:", output_path)
