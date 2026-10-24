# Telangana Constituency Change Atlas

### Electoral competition and vote-share dynamics in the 2018 and 2023 Telangana Assembly elections

An interactive Streamlit dashboard exploring statewide party
performance, constituency-level winners, changes in winning-candidate
vote share, and the closeness of the 2023 contests.

## 🚀 Live Demo

**Explore the interactive dashboard:**  
[Telangana Constituency Change Atlas](https://telangana-constituency-change-atlas.streamlit.app/)

**Source code:** [GitHub Repository](https://github.com/vishwanathmandala2006-wq/telangana-constituency-change-atlas)

> **Scope:** This is a descriptive comparison of election results. It
> documents what changed between the two elections; it does not
> establish why voters changed their preferences.

## Project objectives

-   Compare statewide party vote shares between 2018 and 2023.
-   Compare the number of Assembly seats won by parties in both
    elections.
-   Identify constituencies where the winning party changed.
-   Examine how the winning candidate's vote share changed in each
    constituency.
-   Identify the closest contests in the 2023 election using winning
    margins.
-   Provide transparent definitions, source notes, and downloadable
    tables.

## Dashboard sections

1.  **Election overview** --- 119 constituencies, the count of
    constituencies with a different winning party, the years compared,
    and the largest net seat gain.
2.  **Statewide party vote share** --- comparison of major parties in
    2018 and 2023.
3.  **Statewide vote-share changes** --- largest party-level gains and
    losses in percentage points, with smaller-party details available
    separately.
4.  **Seats won by party** --- seat totals and seat changes between
    elections.
5.  **Constituency-level winner vote-share change** --- largest
    increases and decreases in the winning candidate's share.
6.  **2023 constituency competitiveness** --- closest contests ranked by
    winning margin.

## Key findings from the current analysis

-   The analysis covers **119 Assembly constituencies** in each
    election.
-   The INC won **19 seats in 2018** and **64 in 2023**, a change of
    **+45 seats**.
-   BRS won **88 seats in 2018** and **39 in 2023**, a change of **−49
    seats**.
-   BJP won **1 seat in 2018** and **8 in 2023**, a change of **+7
    seats**.
-   AIMIM won **7 seats in both elections**.
-   The current comparison identifies **64 constituencies where the
    winning party changed** and **55 where it remained the same**. This
    figure should be independently reconciled with official winner lists
    before being treated as a definitive published statistic.
-   The closest 2023 contest in the current analysis is Chevella, with a
    winning margin of **268 votes** and a margin of approximately
    **0.136%** using the project's recorded-vote denominator.

These are descriptive findings from the project's processed datasets.
The results should be cited with the source and denominator definitions
below.

## Data sources

-   **2023 Telangana Assembly election:** Election Commission of India
    statistical report and detailed results.
    -   ECI report landing page:
        https://www.eci.gov.in/telangana-legislative-election-2023-statistical-report
    -   Detailed results PDF:
        https://www.eci.gov.in/eci-backend/public/all_files/full-statistical-reports/telangana/2023/Detailed_Results.pdf
    -   Performance of political parties PDF:
        https://www.eci.gov.in/eci-backend/public/all_files/full-statistical-reports/telangana/2023/Performance_of_Political_Parties.pdf
-   **2018 Telangana Assembly election:** the project uses a Lok
    Dhaba/TCPD-style candidate-level CSV as its working source. The
    project should document the exact downloaded file URL, version/date,
    and any license or attribution terms in the repository before public
    release. Important statewide totals and conclusions should be
    cross-checked against official ECI records where available.

## Data processing and methodology

### Unit of analysis

The project standardizes candidate-level results into constituency-level
and party-level summaries. The Assembly contains 119 constituencies.

### Party-name normalization

Party labels are standardized across years only where the labels refer
to the same party: - 2018 `TRS` is normalized to `BRS` for historical
comparison. - 2023 `BHRS` is normalized to `BRS` where it represents
Bharat Rashtra Samithi. - The distinct 2023 party label `BRS` is
retained separately as **Bahujana Rashtra Samithi** and is not merged
into Bharat Rashtra Samithi.

Verify these mappings against the source files and official party names
when reproducing the analysis.

### Vote-share denominator

Party vote share is calculated using the sum of recorded candidate votes
in the constituency/statewide denominator, including NOTA, while NOTA
itself is not treated as a political party. Therefore, party vote shares
may not sum to exactly 100% when NOTA is included in the denominator.

### Winning candidate and margin

-   NOTA is excluded from candidate ranking when identifying the winner
    and runner-up.
-   The recorded-vote denominator includes NOTA for the project's
    percentage-margin calculation.
-   Vote-share changes for winners compare the winning candidate's own
    share in 2018 and 2023. This is **not the same measure as statewide
    party swing**.

### Seat change

Seat change is calculated as seats won in 2023 minus seats won in 2018.

### Interpretation

The dashboard describes election outcomes. It does not infer individual
voter behavior, causal explanations, or constituency-level voter
transitions from aggregate results.

## Project structure

``` text
Telangana Project/
├── app.py
├── requirements_dashboard.txt
├── data/
│   ├── telangana_2023_raw.xlsx
│   ├── telangana_2023_candidates_clean.csv
│   └── telangana_2018_raw.csv
├── notebooks/
│   ├── 02_analyze_margins.py
│   ├── 03_competition_metrics.py
│   ├── 05_build_2018_results.py
│   ├── 06_compare_elections.py
│   ├── 07_validate_vote_totals.py
│   ├── 08_analyze_vote_share_changes.py
│   ├── 09_analyze_party_vote_shares.py
│   └── 13_validate_nota.py
└── outputs/
    ├── telangana_2023_constituency_results.csv
    ├── telangana_2023_competition_metrics.csv
    ├── telangana_2018_constituency_results.csv
    ├── telangana_constituency_comparison_2018_2023.csv
    ├── telangana_party_seat_comparison_2018_2023.csv
    ├── telangana_party_constituency_vote_shares_2018_2023.csv
    ├── telangana_statewide_party_vote_shares_2018_2023.csv
    └── telangana_winner_vote_share_changes_2018_2023.csv
```

File names may differ slightly across working copies. Keep the README
synchronized with the actual repository before publishing.

## Run locally

Use Python 3.11 or a compatible Python version supported by the
installed packages. From the project root:

``` powershell
# Create and activate a virtual environment (if needed)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
python -m pip install -r requirements_dashboard.txt

# Launch the dashboard
python -m streamlit run app.py
```

Streamlit prints a local address in the terminal, typically
`http://localhost:8501`. Open that address in a browser.

The dashboard expects the processed CSV files to exist in the `outputs/`
directory relative to `app.py`. Keep the folder structure intact.

## Validation checklist before public release

-   [ ] Confirm every headline statistic against the latest output CSVs.
-   [ ] Reconcile the 64 changed-winning-party count against official
    constituency winner lists.
-   [ ] Verify the exact source URL and attribution details for the 2018
    dataset.
-   [ ] Run all validation scripts from a clean environment.
-   [ ] Launch the app and test filters, tables, and downloads.
-   [ ] Ensure `requirements_dashboard.txt` lists all packages imported
    by `app.py`.
-   [ ] Remove unnecessary personal paths, credentials, private data,
    and temporary files.
-   [ ] Add a dashboard screenshot to the repository if appropriate.
-   [ ] Add a license only after confirming the licensing status of the
    source data and project code.

## Limitations

-   Only the 2018 and 2023 Assembly elections are compared.
-   The 2018 and 2023 datasets come from different source formats and
    require standardization.
-   Party-name mapping must be checked carefully, particularly for
    similar party labels.
-   Vote-share comparisons depend on the denominator definition
    documented above.
-   Aggregate election results do not reveal individual voter
    transitions or explain the causes of electoral change.
-   The 64 constituency winner-change figure remains subject to final
    reconciliation against official winner lists.

## Acknowledgements

Election data sources are identified above. Credit the Election
Commission of India and the 2018 dataset provider in accordance with
their applicable terms. This project is an independent educational
analysis and is not an official Election Commission of India
publication.
