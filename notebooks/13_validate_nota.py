import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

FILES = {
    2018: {
        "path": BASE_DIR / "data" / "telangana_2018_raw.csv",
        "party_col": "Party",
        "votes_col": "Votes",
    },
    2023: {
        "path": BASE_DIR / "data" / "telangana_2023_candidates_clean.csv",
        "party_col": "PARTY",
        "votes_col": "TOTAL",
    },
}

for year, config in FILES.items():
    print(f"\n{'=' * 55}")
    print(f"NOTA AND EXCLUDED VOTE AUDIT — {year}")
    print("=" * 55)

    df = pd.read_csv(config["path"], low_memory=False)

    party_col = config["party_col"]
    votes_col = config["votes_col"]

    df[votes_col] = pd.to_numeric(df[votes_col], errors="coerce")
    df[party_col] = df[party_col].fillna("UNKNOWN").astype(str).str.strip()

    # Show every distinct label excluded from party vote totals.
    excluded_labels = ["NOTA", "UNKNOWN", "NONE", "NAN"]

    print("\nExcluded-category audit:")
    for label in excluded_labels:
        rows = df[df[party_col].str.upper() == label]
        print(
            f"{label:10} | records: {len(rows):4} | "
            f"votes: {rows[votes_col].sum():,.0f}"
        )

    nota_votes = df.loc[
        df[party_col].str.upper() == "NOTA", votes_col
    ].sum()

    total_votes = df[votes_col].sum()

    print(f"\nTotal candidate-record votes: {total_votes:,.0f}")
    print(f"NOTA votes: {nota_votes:,.0f}")

    print(
        "Total minus NOTA: "
        f"{total_votes - nota_votes:,.0f}"
    )

print("\nAudit complete.")