import pandas as pd
from pathlib import Path

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Input files
FILE_2018 = BASE_DIR / "data" / "telangana_2018_raw.csv"
FILE_2023 = BASE_DIR / "data" / "telangana_2023_candidates_clean.csv"

# Expected statewide party vote totals for cross-checking
# These are validation targets, not values to overwrite the data with.
EXPECTED_2018 = {
    "BRS": 9_700_749,
    "INC": 5_883_111,
    "BJP": 1_450_456,
}

EXPECTED_2023 = {
    "INC": 9_235_833,
    "BRS": 8_753_956,
    "BJP": 3_257_528,
    "AIMIM": 519_379,
}


def normalize_party(party, year):
    if pd.isna(party):
        return "UNKNOWN"

    party = str(party).strip().upper()

    # 2018 Telangana Rashtra Samithi became BRS.
    if year == 2018 and party == "TRS":
        return "BRS"

    # The 2023 dataset uses BHRS for Bharat Rashtra Samithi.
    if year == 2023 and party == "BHRS":
        return "BRS"

    # Keep the distinct Bahujana Rashtra Samithi separate.
    if year == 2023 and party == "BRS":
        return "BAHUJANA RASHTRA SAMITHI"

    return party


def validate_election(file_path, year, expected_party_votes):
    print(f"\n{'=' * 60}")
    print(f"VALIDATION: TELANGANA ASSEMBLY ELECTION {year}")
    print("=" * 60)

    df = pd.read_csv(file_path, low_memory=False)

    if year == 2018:
        constituency_col = "Constituency_No"
        votes_col = "Votes"
        party_col = "Party"
    else:
        constituency_col = "AC NO."
        votes_col = "TOTAL"
        party_col = "PARTY"

    # Check required columns
    required = [constituency_col, votes_col, party_col]
    missing = [col for col in required if col not in df.columns]

    if missing:
        print("ERROR: Required columns are missing:", missing)
        print("Available columns:", df.columns.tolist())
        return

    # Standardize numeric vote counts
    df[votes_col] = pd.to_numeric(df[votes_col], errors="coerce")

    missing_votes = df[votes_col].isna().sum()

    # Keep rows with valid constituency identifiers and vote counts
    valid = df.dropna(subset=[constituency_col, votes_col]).copy()
    valid[party_col] = valid[party_col].apply(
        lambda p: normalize_party(p, year)
    )

    # Total candidate-record votes include NOTA.
    total_votes = int(valid[votes_col].sum())
    constituency_count = valid[constituency_col].nunique()

    print(f"Rows in source file: {len(df):,}")
    print(f"Rows with valid constituency and votes: {len(valid):,}")
    print(f"Rows with missing/non-numeric votes: {missing_votes}")
    print(f"Unique constituencies: {constituency_count}")
    print(f"Total votes across candidate records: {total_votes:,}")

    # Party vote totals exclude NOTA and unknown party labels.
    party_rows = valid[
        ~valid[party_col].isin(["NOTA", "UNKNOWN", "NONE", "NAN"])
    ]

    party_totals = (
        party_rows.groupby(party_col)[votes_col]
        .sum()
        .sort_values(ascending=False)
    )

    party_vote_sum = int(party_totals.sum())

    print(f"Sum of party votes, excluding NOTA: {party_vote_sum:,}")
    print("\nTop 10 party vote totals:")
    print(party_totals.head(10).to_string())

    print("\nExpected-total cross-check:")
    for party, expected in expected_party_votes.items():
        actual = int(party_totals.get(party, 0))
        difference = actual - expected
        status = "PASS" if difference == 0 else "CHECK"

        print(
            f"{party:6} | actual={actual:>12,} | "
            f"expected={expected:>12,} | "
            f"difference={difference:>8,} | {status}"
        )

    # Verify that all 119 constituencies are represented.
    print("\nConstituency-count check:", 
          "PASS" if constituency_count == 119 else "CHECK")


validate_election(FILE_2018, 2018, EXPECTED_2018)
validate_election(FILE_2023, 2023, EXPECTED_2023)

print("\nValidation script finished.")