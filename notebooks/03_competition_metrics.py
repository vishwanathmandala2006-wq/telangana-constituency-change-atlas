
import pandas as pd

candidates = pd.read_csv(
    "data/telangana_2023_candidates_clean.csv"
)

results = pd.read_csv(
    "outputs/telangana_2023_constituency_results.csv"
)

# Sum votes for every candidate record, including NOTA,
# to estimate total votes polled in each constituency.
votes_polled = (
    candidates.groupby(["AC NO.", "AC NAME"], as_index=False)
    ["TOTAL"].sum()
    .rename(columns={"TOTAL": "Total Votes Polled"})
)

# Attach total votes polled to the winner/runner-up results.
analysis = results.merge(
    votes_polled,
    on=["AC NO.", "AC NAME"],
    how="left",
    validate="one_to_one"
)

analysis["Margin Percentage"] = (
    analysis["Winning Margin"]
    / analysis["Total Votes Polled"]
    * 100
)

# Closest contests relative to total votes polled.
closest = analysis.sort_values(
    "Margin Percentage"
).head(10)

print("\n=== 10 MOST COMPETITIVE CONSTITUENCIES ===")
print(
    closest[
        [
            "AC NAME",
            "PARTY_1",
            "PARTY_2",
            "Winning Margin",
            "Total Votes Polled",
            "Margin Percentage",
        ]
    ].round({"Margin Percentage": 3}).to_string(index=False)
)

# Data-quality checks
print("\n=== VALIDATION ===")
print("Constituencies:", analysis["AC NO."].nunique())
print("Missing total votes:", analysis["Total Votes Polled"].isna().sum())
print("Missing margin percentages:", analysis["Margin Percentage"].isna().sum())

analysis.to_csv(
    "outputs/telangana_2023_competition_metrics.csv",
    index=False
)

print("\nSaved competition metrics successfully.")
