import pandas as pd
from pathlib import Path

# --------------------------------------------------
# 1. Load the original candidate-level datasets
# --------------------------------------------------

df_2018 = pd.read_csv("data/telangana_2018_raw.csv")
df_2023 = pd.read_csv("data/telangana_2023_candidates_clean.csv")

# Convert vote columns to numeric
df_2018["Votes"] = pd.to_numeric(
    df_2018["Votes"], errors="coerce"
)

df_2018["Valid_Votes"] = pd.to_numeric(
    df_2018["Valid_Votes"], errors="coerce"
)

df_2023["TOTAL"] = pd.to_numeric(
    df_2023["TOTAL"], errors="coerce"
)

# --------------------------------------------------
# 2. Normalize party names
# --------------------------------------------------

def normalize_party(party, election_year):
    if pd.isna(party):
        return "UNKNOWN"

    party = str(party).strip().upper()

    if election_year == 2018 and party == "TRS":
        return "BRS"

    if election_year == 2023 and party == "BHRS":
        return "BRS"

    if election_year == 2023 and party == "BRS":
        return "BAHUJANA RASHTRA SAMITHI"

    return party


df_2018["Party_Normalized"] = df_2018["Party"].apply(
    lambda party: normalize_party(party, 2018)
)

df_2023["Party_Normalized"] = df_2023["PARTY"].apply(
    lambda party: normalize_party(party, 2023)
)

# --------------------------------------------------
# 3. Build 2018 constituency-level winner metrics
# --------------------------------------------------

results_2018 = []

for constituency_no, group in df_2018.groupby("Constituency_No"):

    group = group.dropna(subset=["Votes"]).copy()
    group = group.sort_values("Votes", ascending=False)

    total_votes = group["Votes"].sum()

    # Source provides the constituency's Valid_Votes value.
    reported_totals = group["Valid_Votes"].dropna().unique()

    if len(reported_totals) != 1:
        raise ValueError(
            f"Inconsistent Valid_Votes values in constituency "
            f"{constituency_no}"
        )

    reported_valid_votes = reported_totals[0]

    if abs(total_votes - reported_valid_votes) > 0.01:
        raise ValueError(
            f"Vote-total mismatch in 2018 constituency "
            f"{constituency_no}"
        )

    winner = group.iloc[0]
    runner_up = group.iloc[1]

    results_2018.append({
        "Constituency_No": int(constituency_no),
        "Constituency_Name_2018": winner["Constituency_Name"],
        "Winner_2018": winner["Candidate"],
        "Winner_Party_2018": winner["Party_Normalized"],
        "Winner_Votes_2018": winner["Votes"],
        "Total_Votes_2018": total_votes,
        "Winner_Share_2018": (
            winner["Votes"] / total_votes * 100
        ),
        "Margin_2018": (
            winner["Votes"] - runner_up["Votes"]
        ),
    })


results_2018 = pd.DataFrame(results_2018)

# --------------------------------------------------
# 4. Build 2023 constituency-level winner metrics
# --------------------------------------------------

results_2023 = []

for constituency_no, group in df_2023.groupby("AC NO."):

    group = group.dropna(subset=["TOTAL"]).copy()
    group = group.sort_values("TOTAL", ascending=False)

    total_votes = group["TOTAL"].sum()

    if len(group) < 2:
        raise ValueError(
            f"Fewer than two candidate records in "
            f"2023 constituency {constituency_no}"
        )

    winner = group.iloc[0]
    runner_up = group.iloc[1]

    results_2023.append({
        "Constituency_No": int(constituency_no),
        "Constituency_Name_2023": winner["AC NAME"],
        "Winner_2023": winner["CANDIDATE NAME"],
        "Winner_Party_2023": winner["Party_Normalized"],
        "Winner_Votes_2023": winner["TOTAL"],
        "Total_Votes_2023": total_votes,
        "Winner_Share_2023": (
            winner["TOTAL"] / total_votes * 100
        ),
        "Margin_2023": (
            winner["TOTAL"] - runner_up["TOTAL"]
        ),
    })


results_2023 = pd.DataFrame(results_2023)

# --------------------------------------------------
# 5. Merge both elections by constituency number
# --------------------------------------------------

comparison = results_2018.merge(
    results_2023,
    on="Constituency_No",
    how="outer",
    validate="one_to_one",
    indicator=True,
)

print("\n=== CONSTITUENCY MATCHING ===")
print(comparison["_merge"].value_counts().to_string())

if not (comparison["_merge"] == "both").all():
    raise ValueError(
        "Some constituencies did not match between elections."
    )

comparison = comparison.drop(columns=["_merge"])

# --------------------------------------------------
# 6. Calculate changes
# --------------------------------------------------

comparison["Winner_Share_Change_pp"] = (
    comparison["Winner_Share_2023"]
    - comparison["Winner_Share_2018"]
)

comparison["Winning_Margin_Change"] = (
    comparison["Margin_2023"]
    - comparison["Margin_2018"]
)

comparison["Winner_Party_Changed"] = (
    comparison["Winner_Party_2018"]
    != comparison["Winner_Party_2023"]
)

comparison["Winner_Share_Increased"] = (
    comparison["Winner_Share_Change_pp"] > 0
)

# --------------------------------------------------
# 7. Print summary statistics
# --------------------------------------------------

print("\n=== WINNER VOTE-SHARE SUMMARY ===")

print(
    "Average winner share in 2018:",
    round(comparison["Winner_Share_2018"].mean(), 2),
    "%"
)

print(
    "Average winner share in 2023:",
    round(comparison["Winner_Share_2023"].mean(), 2),
    "%"
)

print(
    "Average change in winner share:",
    round(comparison["Winner_Share_Change_pp"].mean(), 2),
    "percentage points"
)

print(
    "\nConstituencies where winner share increased:",
    int(comparison["Winner_Share_Increased"].sum())
)

print(
    "Constituencies where winner share decreased:",
    int((comparison["Winner_Share_Change_pp"] < 0).sum())
)

print(
    "Constituencies with effectively unchanged winner share:",
    int(
        (comparison["Winner_Share_Change_pp"].abs() < 0.01).sum()
    )
)

print(
    "Constituencies where winning party changed:",
    int(comparison["Winner_Party_Changed"].sum())
)

# --------------------------------------------------
# 8. Show the largest increases and decreases
# --------------------------------------------------

display_columns = [
    "Constituency_No",
    "Constituency_Name_2018",
    "Winner_Party_2018",
    "Winner_Party_2023",
    "Winner_Share_2018",
    "Winner_Share_2023",
    "Winner_Share_Change_pp",
]

print("\n=== 10 LARGEST INCREASES IN WINNER VOTE SHARE ===")

print(
    comparison.nlargest(
        10, "Winner_Share_Change_pp"
    )[display_columns].round(2).to_string(index=False)
)

print("\n=== 10 LARGEST DECREASES IN WINNER VOTE SHARE ===")

print(
    comparison.nsmallest(
        10, "Winner_Share_Change_pp"
    )[display_columns].round(2).to_string(index=False)
)

# --------------------------------------------------
# 9. Save results
# --------------------------------------------------

output_path = Path(
    "outputs/telangana_winner_vote_share_changes_2018_2023.csv"
)

output_path.parent.mkdir(parents=True, exist_ok=True)

comparison.to_csv(output_path, index=False)

print(f"\nSaved analysis to: {output_path}")
print("Total constituencies analyzed:", len(comparison))