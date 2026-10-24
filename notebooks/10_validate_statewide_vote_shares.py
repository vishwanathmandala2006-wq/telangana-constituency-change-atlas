
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

file_2018 = ROOT / "data" / "telangana_2018_raw.csv"
file_2023 = ROOT / "data" / "telangana_2023_candidates_clean.csv"

df18 = pd.read_csv(file_2018)
df23 = pd.read_csv(file_2023)

# Normalize party labels
def normalize_party(party, election_year):
    party = str(party).strip().upper()

    if election_year == 2018 and party == "TRS":
        return "BRS"

    if election_year == 2023 and party == "BHRS":
        return "BRS"

    if election_year == 2023 and party == "BRS":
        return "BAHUJANA RASHTRA SAMITHI"

    return party


# Standardize the party column
df18["Party_Normalized"] = df18["Party"].apply(
    lambda party: normalize_party(party, 2018)
)
df23["Party_Normalized"] = df23["PARTY"].apply(
    lambda party: normalize_party(party, 2023)
)

# Convert vote columns to numeric
df18["Votes"] = pd.to_numeric(df18["Votes"], errors="coerce")
df23["TOTAL"] = pd.to_numeric(df23["TOTAL"], errors="coerce")

# Exclude NOTA from political-party totals
# but retain NOTA in the overall vote denominator.
df18["Is_NOTA"] = df18["Party_Normalized"].eq("NOTA")
df23["Is_NOTA"] = df23["Party_Normalized"].eq("NOTA")

total_votes_2018 = df18.groupby("Constituency_No")["Votes"].sum()
total_votes_2023 = df23.groupby("AC NO.")["TOTAL"].sum()

print("=== CONSTITUENCY COVERAGE ===")
print("2018 constituencies:", total_votes_2018.index.nunique())
print("2023 constituencies:", total_votes_2023.index.nunique())

print("\n=== STATEWIDE VOTE TOTALS ===")
print("2018 total votes:", int(total_votes_2018.sum()))
print("2023 total votes:", int(total_votes_2023.sum()))

# Party totals, excluding NOTA
party_votes_2018 = (
    df18.loc[~df18["Is_NOTA"]]
    .groupby("Party_Normalized")["Votes"]
    .sum()
    .sort_values(ascending=False)
)

party_votes_2023 = (
    df23.loc[~df23["Is_NOTA"]]
    .groupby("Party_Normalized")["TOTAL"]
    .sum()
    .sort_values(ascending=False)
)

print("\n=== TOP 10 PARTIES: 2018 ===")
print(party_votes_2018.head(10).to_string())

print("\n=== TOP 10 PARTIES: 2023 ===")
print(party_votes_2023.head(10).to_string())

# Compare the major parties with the existing analysis
comparison_file = (
    ROOT / "outputs"
    / "telangana_statewide_party_vote_shares_2018_2023.csv"
)

if comparison_file.exists():
    existing = pd.read_csv(comparison_file)

    print("\n=== EXISTING STATEWIDE ANALYSIS ===")
    major_parties = existing[
        existing["Party"].isin(["INC", "BRS", "BJP", "AIMIM"])
    ]

    print(
        major_parties[
            [
                "Party",
                "Votes_2018",
                "Votes_2023",
                "Vote_Share_2018",
                "Vote_Share_2023",
                "Vote_Share_Change_pp",
            ]
        ].to_string(index=False)
    )

print("\nValidation script completed.")
