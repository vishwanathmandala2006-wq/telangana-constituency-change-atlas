
import pandas as pd

file_path = "outputs/telangana_2023_constituency_results.csv"
df = pd.read_csv(file_path)

# 10 closest contests: smallest winning margins
closest = df.sort_values("Winning Margin").head(10)

print("\n=== 10 CLOSEST CONTESTS ===")
print(
    closest[
        [
            "AC NAME",
            "CANDIDATE NAME_1",
            "PARTY_1",
            "CANDIDATE NAME_2",
            "PARTY_2",
            "Winning Margin",
        ]
    ].to_string(index=False)
)

# 10 largest winning margins
largest = df.sort_values(
    "Winning Margin", ascending=False
).head(10)

print("\n=== 10 LARGEST WINNING MARGINS ===")
print(
    largest[
        [
            "AC NAME",
            "CANDIDATE NAME_1",
            "PARTY_1",
            "CANDIDATE NAME_2",
            "PARTY_2",
            "Winning Margin",
        ]
    ].to_string(index=False)
)

# Count seats won by each party
party_seats = df["PARTY_1"].value_counts()

print("\n=== SEATS WON BY PARTY ===")
print(party_seats.to_string())
