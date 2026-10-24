import pandas as pd
from pathlib import Path

# ==================================================
# 1. LOAD THE DATASETS
# ==================================================

df_2018 = pd.read_csv("data/telangana_2018_raw.csv")
df_2023 = pd.read_csv("data/telangana_2023_candidates_clean.csv")


# ==================================================
# 2. CLEAN VOTE COUNTS AND STANDARDIZE PARTY NAMES
# ==================================================

df_2018["Votes"] = pd.to_numeric(
    df_2018["Votes"], errors="coerce"
)

df_2018["Valid_Votes"] = pd.to_numeric(
    df_2018["Valid_Votes"], errors="coerce"
)

df_2023["TOTAL"] = pd.to_numeric(
    df_2023["TOTAL"], errors="coerce"
)


def normalize_party(party, election_year):
    party = str(party).strip().upper()

    # 2018: TRS refers to Bharat Rashtra Samithi's
    # predecessor, Telangana Rashtra Samithi.
    if election_year == 2018 and party == "TRS":
        return "BRS"

    # 2023: BHRS is the label used for Bharat
    # Rashtra Samithi in the source dataset.
    if election_year == 2023 and party == "BHRS":
        return "BRS"

    # In the 2023 source, the separate label BRS
    # identifies Bahujana Rashtra Samithi.
    if election_year == 2023 and party == "BRS":
        return "BAHUJANA RASHTRA SAMITHI"

    return party


df_2018["Party_Normalized"] = df_2018["Party"].apply(
    lambda party: normalize_party(party, 2018)
)

df_2023["Party_Normalized"] = df_2023["PARTY"].apply(
    lambda party: normalize_party(party, 2023)
)


# ==================================================
# 3. CALCULATE TOTAL VOTES PER CONSTITUENCY
# ==================================================

# 2018: validate summed candidate votes against
# the source's reported Valid_Votes field.

totals_2018 = (
    df_2018.groupby("Constituency_No", as_index=False)
    .agg(
        Total_Votes_2018=("Votes", "sum"),
        Reported_Valid_Votes=("Valid_Votes", "first"),
    )
)

totals_2018["Vote_Total_Difference"] = (
    totals_2018["Total_Votes_2018"]
    - totals_2018["Reported_Valid_Votes"]
)

if (
    totals_2018["Vote_Total_Difference"].abs() > 0.01
).any():
    raise ValueError(
        "2018 vote totals do not match reported Valid_Votes."
    )


# 2023: sum all candidate-record votes, including NOTA.

totals_2023 = (
    df_2023.groupby("AC NO.", as_index=False)
    .agg(
        Total_Votes_2023=("TOTAL", "sum")
    )
    .rename(columns={"AC NO.": "Constituency_No"})
)


# Check constituency counts.

print("\n=== DENOMINATOR VALIDATION ===")
print("2018 constituencies:", len(totals_2018))
print("2023 constituencies:", len(totals_2023))

if (
    len(totals_2018) != 119
    or len(totals_2023) != 119
):
    raise ValueError(
        "Expected 119 constituencies in each election."
    )

print("2018 vote-total mismatches: 0")
print("2023 missing vote totals:", totals_2023[
    "Total_Votes_2023"
].isna().sum())


# ==================================================
# 4. AGGREGATE PARTY VOTES BY CONSTITUENCY
# ==================================================

# Exclude NOTA from political-party results.
# NOTA remains included in constituency denominators.

party_votes_2018 = (
    df_2018[
        df_2018["Party_Normalized"] != "NOTA"
    ]
    .groupby(
        ["Constituency_No", "Party_Normalized"],
        as_index=False
    )
    .agg(
        Votes_2018=("Votes", "sum")
    )
    .rename(
        columns={"Party_Normalized": "Party"}
    )
)

party_votes_2023 = (
    df_2023[
        df_2023["Party_Normalized"] != "NOTA"
    ]
    .groupby(
        ["AC NO.", "Party_Normalized"],
        as_index=False
    )
    .agg(
        Votes_2023=("TOTAL", "sum")
    )
    .rename(
        columns={
            "AC NO.": "Constituency_No",
            "Party_Normalized": "Party"
        }
    )
)


# ==================================================
# 5. MERGE PARTY RESULTS ACROSS BOTH ELECTIONS
# ==================================================

comparison = party_votes_2018.merge(
    party_votes_2023,
    on=["Constituency_No", "Party"],
    how="outer",
    validate="one_to_one"
)

# Preserve whether the party contested each election.
comparison["Contested_2018"] = (
    comparison["Votes_2018"].notna()
)

comparison["Contested_2023"] = (
    comparison["Votes_2023"].notna()
)

# Zero votes when a party did not appear in that
# constituency's candidate records.
comparison["Votes_2018"] = (
    comparison["Votes_2018"].fillna(0)
)

comparison["Votes_2023"] = (
    comparison["Votes_2023"].fillna(0)
)


# Add constituency-level denominators.

comparison = comparison.merge(
    totals_2018[
        ["Constituency_No", "Total_Votes_2018"]
    ],
    on="Constituency_No",
    how="left",
    validate="many_to_one"
)

comparison = comparison.merge(
    totals_2023[
        ["Constituency_No", "Total_Votes_2023"]
    ],
    on="Constituency_No",
    how="left",
    validate="many_to_one"
)


# ==================================================
# 6. CALCULATE CONSTITUENCY-LEVEL PARTY VOTE SHARES
# ==================================================

comparison["Vote_Share_2018"] = (
    comparison["Votes_2018"]
    / comparison["Total_Votes_2018"]
    * 100
)

comparison["Vote_Share_2023"] = (
    comparison["Votes_2023"]
    / comparison["Total_Votes_2023"]
    * 100
)

comparison["Vote_Share_Change_pp"] = (
    comparison["Vote_Share_2023"]
    - comparison["Vote_Share_2018"]
)

comparison["Vote_Change"] = (
    comparison["Votes_2023"]
    - comparison["Votes_2018"]
)


# Add constituency names for easier interpretation.

constituency_names = (
    df_2023[
        ["AC NO.", "AC NAME"]
    ]
    .drop_duplicates()
    .rename(
        columns={
            "AC NO.": "Constituency_No",
            "AC NAME": "Constituency_Name"
        }
    )
)

comparison = comparison.merge(
    constituency_names,
    on="Constituency_No",
    how="left",
    validate="many_to_one"
)

comparison = comparison.sort_values(
    ["Constituency_No", "Party"]
)


# ==================================================
# 7. CALCULATE STATEWIDE PARTY VOTE SHARES
# ==================================================

# Aggregate each party's votes across all constituencies.

statewide_2018 = (
    party_votes_2018.groupby("Party", as_index=False)
    .agg(
        Votes_2018=("Votes_2018", "sum")
    )
)

statewide_2023 = (
    party_votes_2023.groupby("Party", as_index=False)
    .agg(
        Votes_2023=("Votes_2023", "sum")
    )
)

statewide = statewide_2018.merge(
    statewide_2023,
    on="Party",
    how="outer",
    validate="one_to_one"
)

statewide[["Votes_2018", "Votes_2023"]] = (
    statewide[["Votes_2018", "Votes_2023"]].fillna(0)
)

statewide_total_2018 = totals_2018[
    "Total_Votes_2018"
].sum()

statewide_total_2023 = totals_2023[
    "Total_Votes_2023"
].sum()

statewide["Vote_Share_2018"] = (
    statewide["Votes_2018"]
    / statewide_total_2018
    * 100
)

statewide["Vote_Share_2023"] = (
    statewide["Votes_2023"]
    / statewide_total_2023
    * 100
)

statewide["Vote_Share_Change_pp"] = (
    statewide["Vote_Share_2023"]
    - statewide["Vote_Share_2018"]
)

statewide["Vote_Change"] = (
    statewide["Votes_2023"]
    - statewide["Votes_2018"]
)

statewide = statewide.sort_values(
    "Votes_2023", ascending=False
)


# ==================================================
# 8. DISPLAY COMPARABLE CONSTITUENCY-LEVEL CHANGES
# ==================================================

for party in ["INC", "BRS", "BJP", "AIMIM"]:

    party_data = comparison[
        comparison["Party"] == party
    ].copy()

    # Compare vote-share changes only where the party
    # contested in both elections.
    comparable = party_data[
        party_data["Contested_2018"]
        & party_data["Contested_2023"]
    ].copy()

    print(f"\n=== {party}: LARGEST COMPARABLE INCREASES ===")

    print(
        comparable.nlargest(
            5, "Vote_Share_Change_pp"
        )[
            [
                "Constituency_Name",
                "Votes_2018",
                "Votes_2023",
                "Vote_Share_2018",
                "Vote_Share_2023",
                "Vote_Share_Change_pp",
            ]
        ].round(2).to_string(index=False)
    )

    print(f"\n=== {party}: LARGEST COMPARABLE DECREASES ===")

    print(
        comparable.nsmallest(
            5, "Vote_Share_Change_pp"
        )[
            [
                "Constituency_Name",
                "Votes_2018",
                "Votes_2023",
                "Vote_Share_2018",
                "Vote_Share_2023",
                "Vote_Share_Change_pp",
            ]
        ].round(2).to_string(index=False)
    )

    # Report contest entry and exit separately.
    entered = party_data[
        ~party_data["Contested_2018"]
        & party_data["Contested_2023"]
    ]

    exited = party_data[
        party_data["Contested_2018"]
        & ~party_data["Contested_2023"]
    ]

    print(f"\n=== {party}: CONSTITUENCIES ENTERED ===")
    print(
        entered["Constituency_Name"].tolist()
    )

    print(f"\n=== {party}: CONSTITUENCIES NOT CONTESTED IN 2023 ===")
    print(
        exited["Constituency_Name"].tolist()
    )


# ==================================================
# 9. SAVE OUTPUT FILES
# ==================================================

output_dir = Path("outputs")
output_dir.mkdir(parents=True, exist_ok=True)

comparison.to_csv(
    output_dir / "telangana_party_constituency_vote_shares_2018_2023.csv",
    index=False
)

statewide.to_csv(
    output_dir / "telangana_statewide_party_vote_shares_2018_2023.csv",
    index=False
)

print("\n=== OUTPUTS SAVED ===")
print(
    "Constituency-party analysis:",
    output_dir / "telangana_party_constituency_vote_shares_2018_2023.csv"
)

print(
    "Statewide party analysis:",
    output_dir / "telangana_statewide_party_vote_shares_2018_2023.csv"
)

print("\nConstituency-party rows:", len(comparison))
print("Statewide party rows:", len(statewide))
print("Analysis completed.")