
import pandas as pd
from pathlib import Path

# 1. Load constituency-level results for both elections
results_2018 = pd.read_csv(
    "outputs/telangana_2018_constituency_results.csv"
)

results_2023 = pd.read_csv(
    "outputs/telangana_2023_constituency_results.csv"
)

# 2. Normalize party labels
def normalize_party(party, election_year):
    party = str(party).strip().upper()

    if election_year == 2018 and party == "TRS":
        return "BRS"

    if election_year == 2023 and party == "BHRS":
        return "BRS"

    if election_year == 2023 and party == "BRS":
        return "BAHUJANA RASHTRA SAMITHI"

    return party


results_2018["Winner Party"] = (
    results_2018["Winner Party"].apply(
        lambda party: normalize_party(party, 2018)
    )
)

results_2023["PARTY_1"] = (
    results_2023["PARTY_1"].apply(
        lambda party: normalize_party(party, 2023)
    )
)

# 3. Create one common constituency identifier
results_2018["Constituency ID"] = (
    results_2018["Constituency_No"].astype(int)
)

results_2023["Constituency ID"] = (
    results_2023["AC NO."].astype(int)
)

# 4. Compare winners and parties across years
comparison = results_2018.merge(
    results_2023,
    on="Constituency ID",
    how="outer",
    suffixes=("_2018", "_2023"),
    indicator=True,
    validate="one_to_one",
)

print("=== DATASET MATCHING ===")
print("2018 constituencies:", len(results_2018))
print("2023 constituencies:", len(results_2023))
print("\nMatch status:")
print(comparison["_merge"].value_counts().to_string())

# 5. Identify constituencies where the winning party changed
comparison["Party Changed"] = (
    comparison["Winner Party"] != comparison["PARTY_1"]
)

changed = comparison[comparison["Party Changed"]].copy()

print("\n=== CONSTITUENCIES WHERE WINNING PARTY CHANGED ===")
print("Count:", len(changed))

print(
    changed[
        [
            "Constituency_Name",
            "Winner Party",
            "PARTY_1",
        ]
    ].to_string(index=False)
)

# 6. Calculate seats won by each party
seats_2018 = (
    results_2018["Winner Party"]
    .value_counts()
    .rename("Seats_2018")
)

seats_2023 = (
    results_2023["PARTY_1"]
    .value_counts()
    .rename("Seats_2023")
)

party_comparison = pd.concat(
    [seats_2018, seats_2023],
    axis=1,
).fillna(0)

party_comparison["Seats_2018"] = (
    party_comparison["Seats_2018"].astype(int)
)

party_comparison["Seats_2023"] = (
    party_comparison["Seats_2023"].astype(int)
)

party_comparison["Seat Change"] = (
    party_comparison["Seats_2023"]
    - party_comparison["Seats_2018"]
)

party_comparison = party_comparison.sort_values(
    "Seats_2023",
    ascending=False,
)

print("\n=== PARTY SEAT COMPARISON ===")
print(party_comparison.to_string())

# 7. Save the comparison outputs
output_dir = Path("outputs")
output_dir.mkdir(parents=True, exist_ok=True)

comparison.to_csv(
    output_dir / "telangana_constituency_comparison_2018_2023.csv",
    index=False,
)

party_comparison.to_csv(
    output_dir / "telangana_party_seat_comparison_2018_2023.csv",
)

print("\nSaved both comparison files successfully.")


# 8. Audit the party-change count and build a transition table

print("\n=== PARTY CHANGE AUDIT ===")

print("Total matched constituencies:", len(comparison))
print("Constituencies with party changes:", comparison["Party Changed"].sum())
print("Constituencies with same winning party:", (~comparison["Party Changed"]).sum())

# Show how winning parties transitioned from 2018 to 2023
transition_table = pd.crosstab(
    comparison["Winner Party"],
    comparison["PARTY_1"],
    margins=True,
)

print("\n=== WINNING PARTY TRANSITIONS: 2018 TO 2023 ===")
print(transition_table.to_string())

# Inspect constituencies where the winning party stayed the same
unchanged = comparison[~comparison["Party Changed"]]

print("\n=== CONSTITUENCIES WITH THE SAME WINNING PARTY ===")
print(
    unchanged[
        [
            "Constituency_Name",
            "Winner Party",
            "PARTY_1",
        ]
    ].to_string(index=False)
)
