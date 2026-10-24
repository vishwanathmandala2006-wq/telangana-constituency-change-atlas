from pathlib import Path
import pandas as pd
import streamlit as st
import altair as alt

BASE_DIR = Path(__file__).resolve().parent
OUTPUTS = BASE_DIR / "outputs"

st.set_page_config(page_title="Telangana Constituency Change Atlas", page_icon="🗳️", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
:root {
  --atlas-orange: #FF7900;
  --atlas-amber: #FFB45B;
  --atlas-cream: #FFE0B2;
  --atlas-rust: #8E3200;
  --atlas-bg: #101114;
}
.stApp { background: var(--atlas-bg); }
.block-container { max-width: none !important; width: 100% !important; padding: 1.25rem 2rem 2.5rem 2rem; }\ndiv[data-testid="stMainBlockContainer"] { max-width: none !important; }\n@media (max-width: 900px) { .block-container { padding-left: 1rem; padding-right: 1rem; } }
section[data-testid="stSidebar"] { border-right: 1px solid rgba(255,145,45,.22); }
.hero {
  padding: 1.5rem 1.7rem; border-radius: 16px;
  background: linear-gradient(112deg, #321506 0%, #7A2C05 44%, #FF7900 100%);
  color: #fff; margin-bottom: 1rem;
  border: 1px solid rgba(255,180,91,.35);
  box-shadow: 0 10px 32px rgba(255,121,0,.10);
}
.hero h1 { color: #fff; margin: 0 0 .4rem 0; letter-spacing: -.025em; }
.hero p { color: #FFF0DF; margin: 0; }
div[data-testid="stMetric"] {
  background: linear-gradient(145deg, rgba(255,121,0,.075), rgba(255,255,255,.025));
  border: 1px solid rgba(255,145,45,.28); padding: 14px 15px; border-radius: 12px;
}
div[data-testid="stMetric"] label { color: #E8D6C6 !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #FFB45B !important; }
h1, h2, h3 { letter-spacing: -.015em; }
a { color: #FFB45B !important; }
button[kind="primary"] { background: #FF7900; border-color: #FF7900; }

hr { border-color: rgba(255,145,45,.22) !important; }
div[data-testid="stExpander"] { border-color: rgba(255,145,45,.28); border-radius: 10px; }
.stCaption, [data-testid="stCaptionContainer"] { color: #A9A9AE; }
</style>
<div class="hero"><h1>Telangana Constituency Change Atlas</h1>
<p>Electoral competition and vote-share dynamics · Assembly elections 2018–2023</p></div>
""", unsafe_allow_html=True)
st.write("Explore statewide party performance, constituency winners, and the closeness of 2023 contests.")
st.caption("Descriptive election results show what changed; they do not establish why voters changed.")

@st.cache_data
def load_csv(filename):
    path = OUTPUTS / filename
    if not path.exists():
        return None
    try:
        return pd.read_csv(path, low_memory=False)
    except Exception as exc:
        st.error(f"Could not read {filename}: {exc}")
        return None

def find_col(df, candidates):
    if df is None:
        return None
    normalized = {str(c).strip().lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate.lower() in normalized:
            return normalized[candidate.lower()]
    for candidate in candidates:
        for key, original in normalized.items():
            if candidate.lower() in key:
                return original
    return None

def numeric(df, cols):
    for col in cols:
        if col and col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

statewide = load_csv("telangana_statewide_party_vote_shares_2018_2023.csv")
seat_path = OUTPUTS / "telangana_party_seat_comparison_2018_2023.csv"
if seat_path.exists():
    try:
        seats = pd.read_csv(seat_path, index_col=0).reset_index()
        seats = seats.rename(columns={seats.columns[0]: "Party"})
    except Exception as exc:
        st.error(f"Could not read seat comparison file: {exc}")
        seats = None
else:
    seats = None
winner_changes = load_csv("telangana_winner_vote_share_changes_2018_2023.csv")
competition = load_csv("telangana_2023_competition_metrics.csv")
constituency_comparison = load_csv("telangana_constituency_comparison_2018_2023.csv")

st.sidebar.header("Explore the data")
st.sidebar.caption("Filters update the party comparisons and constituency-level winner-share tables.")
parties = sorted(statewide["Party"].dropna().astype(str).unique()) if isinstance(statewide, pd.DataFrame) and "Party" in statewide else []
selected_party = st.sidebar.selectbox("Party", ["All parties"] + parties)
constituency_name_col = find_col(winner_changes, ["Constituency_Name_2018", "Constituency_Name", "AC NAME", "Constituency"])
constituencies = sorted(winner_changes[constituency_name_col].dropna().astype(str).unique()) if isinstance(winner_changes, pd.DataFrame) and constituency_name_col else []
selected_constituency = st.sidebar.selectbox("Constituency", ["All constituencies"] + constituencies)

changed_count = None
if isinstance(winner_changes, pd.DataFrame):
    p18 = find_col(winner_changes, ["Winner_Party_2018"])
    p23 = find_col(winner_changes, ["Winner_Party_2023"])
    if p18 and p23:
        changed_count = int((winner_changes[p18].fillna("").astype(str).str.strip() != winner_changes[p23].fillna("").astype(str).str.strip()).sum())
largest_gain = "—"
if isinstance(seats, pd.DataFrame):
    change_col = find_col(seats, ["Seat Change", "Seats_Change", "Seat_Change"])
    if change_col:
        tmp = numeric(seats.copy(), [change_col])
        if tmp[change_col].notna().any():
            row = tmp.loc[tmp[change_col].idxmax()]
            largest_gain = f"{row['Party']} (+{int(row[change_col])})"

st.subheader("Election overview")
k1,k2,k3,k4 = st.columns(4)
k1.metric("Assembly constituencies", "119")
k2.metric("Winning party changed", str(changed_count) if changed_count is not None else "—")
k3.metric("Elections compared", "2018 → 2023")
k4.metric("Largest net seat gain", largest_gain)
st.divider()

st.subheader("Statewide party vote share")
st.caption("Party vote share uses total candidate-record votes, including NOTA, as the denominator.")
if isinstance(statewide, pd.DataFrame):
    needed = ["Party","Vote_Share_2018","Vote_Share_2023","Vote_Share_Change_pp"]
    missing = [c for c in needed if c not in statewide.columns]
    if missing:
        st.error(f"Statewide CSV missing columns: {missing}")
        st.write(statewide.columns.tolist())
    else:
        vote = numeric(statewide.copy(), needed[1:])
        if selected_party != "All parties":
            vote = vote[vote["Party"].astype(str) == selected_party]
        vote = vote.sort_values("Vote_Share_2023", ascending=False)
        if selected_party == "All parties":
            main = vote[vote["Party"].isin(["INC","BRS","BJP","AIMIM"])].copy()
            other = vote[~vote["Party"].isin(["INC","BRS","BJP","AIMIM"])].copy()
        else:
            main, other = vote.copy(), vote.iloc[0:0].copy()
        if not main.empty:
            long = main.melt(id_vars="Party", value_vars=["Vote_Share_2018","Vote_Share_2023"], var_name="Election", value_name="Vote share (%)")
            long["Election"] = long["Election"].map({"Vote_Share_2018":"2018","Vote_Share_2023":"2023"})
            chart = alt.Chart(long).mark_bar(cornerRadiusEnd=4).encode(
                x=alt.X("Party:N", title=None, sort=["INC","BRS","BJP","AIMIM"], axis=alt.Axis(labelAngle=0, labelLimit=120)),
                xOffset=alt.XOffset("Election:N", sort=["2018","2023"]),
                y=alt.Y("Vote share (%):Q", title="Vote share (%)", scale=alt.Scale(domain=[0, max(5, float(long["Vote share (%)"].max())*1.15)]), axis=alt.Axis(format=".1f")),
                color=alt.Color("Election:N", scale=alt.Scale(domain=["2018","2023"], range=["#FFBE69","#FF7900"])),
                tooltip=["Party","Election",alt.Tooltip("Vote share (%):Q",format=".2f")]
            ).properties(height=360, padding={"left": 10, "right": 10, "top": 12, "bottom": 8}, title=alt.TitleParams(
                text="Vote share by party and election",
                subtitle="Hover over a bar for the exact share"
            ))
            st.altair_chart(chart, use_container_width=True)
        if selected_party == "All parties" and not vote.empty:
            st.markdown("#### Change in statewide vote share")
            st.caption("Percentage-point change from 2018 to 2023. Positive values indicate a higher share in 2023.")
            positive = vote[vote["Vote_Share_Change_pp"] > 0].nlargest(10, "Vote_Share_Change_pp")
            negative = vote[vote["Vote_Share_Change_pp"] < 0].nsmallest(10, "Vote_Share_Change_pp")
            change_df = pd.concat([positive, negative]).drop_duplicates(subset=["Party"]).copy()
            change_df["Direction"] = change_df["Vote_Share_Change_pp"].apply(
                lambda value: "Increase" if value > 0 else ("Decrease" if value < 0 else "No change")
            )
            change_df = change_df.sort_values("Vote_Share_Change_pp", ascending=True)
            st.markdown("#### Largest statewide vote-share gains and losses")
            st.caption("Top 10 increases and top 10 decreases, measured in percentage points. Use the table below for every party.")
            change_chart = alt.Chart(change_df).mark_bar(cornerRadiusEnd=3).encode(
                y=alt.Y("Party:N", sort=alt.SortField(field="Vote_Share_Change_pp", order="ascending"), title=None, axis=alt.Axis(labelLimit=150, labelFontSize=11)),
                x=alt.X("Vote_Share_Change_pp:Q", title="Change (percentage points)", axis=alt.Axis(format="+.1f"), scale=alt.Scale(zero=True)),
                color=alt.Color("Direction:N", scale=alt.Scale(
                    domain=["Increase", "Decrease", "No change"],
                    range=["#FF7900", "#FFBE69", "#A7A7A7"]
                ), legend=alt.Legend(title="Change")),
                tooltip=[
                    alt.Tooltip("Party:N", title="Party"),
                    alt.Tooltip("Vote_Share_Change_pp:Q", title="Change (pp)", format="+.3f"),
                    alt.Tooltip("Vote_Share_2018:Q", title="2018 share (%)", format=".2f"),
                    alt.Tooltip("Vote_Share_2023:Q", title="2023 share (%)", format=".2f")
                ]
            ).properties(height=max(300, 28 * len(change_df)))
            st.altair_chart(change_chart, use_container_width=True)
        if not other.empty:
            with st.expander("Explore smaller parties"):
                other_view = other[needed].rename(columns={"Vote_Share_2018":"2018 share (%)","Vote_Share_2023":"2023 share (%)","Vote_Share_Change_pp":"Change (pp)"}).round(2)
                st.dataframe(other_view, use_container_width=True, hide_index=True)
                st.download_button(
                    "Download smaller-party vote-share data",
                    data=other_view.to_csv(index=False).encode("utf-8"),
                    file_name="telangana_smaller_party_vote_shares_2018_2023.csv",
                    mime="text/csv"
                )
        with st.expander("View statewide vote-share table"):
            statewide_view = vote[needed].rename(columns={"Vote_Share_2018":"2018 share (%)","Vote_Share_2023":"2023 share (%)","Vote_Share_Change_pp":"Change (pp)"}).round(3)
            st.dataframe(statewide_view, use_container_width=True, hide_index=True, height=360)
            st.download_button(
                "Download statewide vote-share data",
                data=statewide_view.to_csv(index=False).encode("utf-8"),
                file_name="telangana_statewide_party_vote_shares_2018_2023.csv",
                mime="text/csv"
            )
else:
    st.warning("Statewide vote-share CSV is missing from outputs.")

st.divider()
st.subheader("Seats won by party")
st.caption("The chart uses a horizontal scale from 0 to 119 seats.")
if isinstance(seats, pd.DataFrame):
    pcol = find_col(seats, ["Party"])
    s18 = find_col(seats, ["Seats_2018"])
    s23 = find_col(seats, ["Seats_2023"])
    if all([pcol,s18,s23]):
        seat_df = numeric(seats.copy(), [s18,s23])
        seat_df[pcol] = seat_df[pcol].astype(str).str.strip()
        if selected_party != "All parties":
            seat_df = seat_df[seat_df[pcol] == selected_party]
        seat_df = seat_df.sort_values(s23, ascending=False)
        long = seat_df[[pcol,s18,s23]].melt(id_vars=pcol, value_vars=[s18,s23], var_name="Election", value_name="Seats")
        long["Election"] = long["Election"].map({s18:"2018",s23:"2023"})
        chart = alt.Chart(long).mark_bar(cornerRadiusEnd=4).encode(
            y=alt.Y(f"{pcol}:N", title=None, sort=seat_df[pcol].tolist()),
            x=alt.X("Seats:Q", title="Seats won", scale=alt.Scale(domain=[0,119]), axis=alt.Axis(tickMinStep=10, format="d")),
            yOffset=alt.YOffset("Election:N", sort=["2018","2023"]),
            color=alt.Color("Election:N", scale=alt.Scale(domain=["2018","2023"], range=["#FFBE69","#FF7900"])),
            tooltip=[alt.Tooltip(f"{pcol}:N",title="Party"),"Election",alt.Tooltip("Seats:Q",format="d")]
        ).properties(height=max(250, 40*seat_df[pcol].nunique()))
        st.altair_chart(chart, use_container_width=True)
        show = seat_df.rename(columns={pcol:"Party",s18:"Seats in 2018",s23:"Seats in 2023"})
        st.dataframe(show, use_container_width=True, hide_index=True)
        st.download_button(
            "Download party seat comparison",
            data=show.to_csv(index=False).encode("utf-8"),
            file_name="telangana_party_seat_comparison_2018_2023.csv",
            mime="text/csv"
        )
    else:
        st.error(f"Unexpected seat columns: {seats.columns.tolist()}")
else:
    st.warning("Party seat comparison CSV is missing from outputs.")

st.divider()
st.subheader("Constituency-level winner vote-share change")
st.caption("Winning-candidate share change is not the same as statewide party swing.")
if isinstance(winner_changes, pd.DataFrame):
    df = winner_changes.copy()
    name_col = find_col(df, ["Constituency_Name_2018","Constituency_Name","AC NAME","Constituency"])
    p18 = find_col(df, ["Winner_Party_2018"])
    p23 = find_col(df, ["Winner_Party_2023"])
    sh18 = find_col(df, ["Winner_Share_2018"])
    sh23 = find_col(df, ["Winner_Share_2023"])
    ch = find_col(df, ["Winner_Share_Change_pp"])
    if all([name_col,p18,p23,sh18,sh23,ch]):
        df = numeric(df, [sh18,sh23,ch])
        if selected_constituency != "All constituencies":
            df = df[df[name_col].astype(str) == selected_constituency]
        if selected_party != "All parties":
            df = df[(df[p18].astype(str) == selected_party) | (df[p23].astype(str) == selected_party)]
        cols = [name_col,p18,p23,sh18,sh23,ch]
        labels = ["Constituency","Winner 2018","Winner 2023","Share 2018 (%)","Share 2023 (%)","Change (pp)"]
        left,right = st.columns(2)
        with left:
            st.markdown("**Largest increases**")
            view = df.nlargest(10,ch)[cols].copy()
            view.columns = labels
            st.dataframe(view.round(2), use_container_width=True, hide_index=True, height=390)
        with right:
            st.markdown("**Largest decreases**")
            view = df.nsmallest(10,ch)[cols].copy()
            view.columns = labels
            st.dataframe(view.round(2), use_container_width=True, hide_index=True, height=390)
        with st.expander("Explore all selected constituencies"):
            view = df[cols].sort_values(ch).copy()
            view.columns = labels
            view = view.round(2)
            st.dataframe(view, use_container_width=True, hide_index=True, height=420)
            st.download_button(
                "Download selected constituency winner-share changes",
                data=view.to_csv(index=False).encode("utf-8"),
                file_name="telangana_constituency_winner_share_changes.csv",
                mime="text/csv"
            )
    else:
        st.error(f"Unexpected winner-share columns: {df.columns.tolist()}")
else:
    st.warning("Winner vote-share change CSV is missing from outputs.")

st.divider()
st.subheader("2023 constituency competitiveness")
st.caption("Smaller winning margins indicate closer contests; the percentage denominator includes NOTA.")
if isinstance(competition, pd.DataFrame):
    df = competition.copy()
    margin = find_col(df, ["Winning_Margin","Margin","Winning Margin","Margin_Votes"])
    pct = find_col(df, ["Margin_Percentage","Margin_Percent","Margin_Pct","Winning_Margin_Percentage"])
    name = find_col(df, ["Constituency_Name","AC NAME","Constituency"])
    if margin and name:
        df = numeric(df,[margin,pct])
        cols = [name,margin] + ([pct] if pct else [])
        closest = df.nsmallest(10, pct if pct else margin)[cols].copy()
        if pct:
            chart_df = closest[[name, pct]].copy()
            chart_df.columns = ["Constituency", "Margin (%)"]
            chart_df["Margin (%)"] = pd.to_numeric(chart_df["Margin (%)"], errors="coerce")
            margin_chart = alt.Chart(chart_df).mark_bar(color="#FF7900", cornerRadiusEnd=4).encode(
                y=alt.Y("Constituency:N", sort="-x", title=None, axis=alt.Axis(labelLimit=180)),
                x=alt.X("Margin (%):Q", title="Winning margin (% of recorded votes)", axis=alt.Axis(format=".2f")),
                tooltip=["Constituency", alt.Tooltip("Margin (%):Q", format=".3f")]
            ).properties(height=330)
            st.altair_chart(margin_chart, use_container_width=True)
        closest = df.nsmallest(10, pct if pct else margin)[cols].copy()
        closest.columns = ["Constituency","Winning margin (votes)"] + (["Margin / total votes (%)"] if pct else [])
        st.dataframe(closest.round(3), use_container_width=True, hide_index=True)
        with st.expander("View all constituencies by margin"):
            all_rows = df.sort_values(margin)[cols].copy()
            all_rows.columns = ["Constituency","Winning margin (votes)"] + (["Margin / total votes (%)"] if pct else [])
            all_rows = all_rows.round(3)
            st.dataframe(all_rows, use_container_width=True, hide_index=True, height=420)
            st.download_button(
                "Download constituency competitiveness data",
                data=all_rows.to_csv(index=False).encode("utf-8"),
                file_name="telangana_2023_constituency_competitiveness.csv",
                mime="text/csv"
            )
    else:
        st.error(f"Unexpected competition columns: {df.columns.tolist()}")
else:
    st.warning("2023 competition metrics CSV is missing from outputs.")

with st.expander("Data sources and methodological notes"):
    st.markdown("""
    - 2018 candidate-level results: the project's supplied Lok Dhaba/TCPD-style CSV.
    - 2023 candidate-level results: cleaned candidate records derived from the Election Commission of India detailed results.
    - 2018 TRS and 2023 BHRS are standardized to BRS for cross-election comparison.
    - The distinct 2023 Bahujana Rashtra Samithi label is kept separate.
    - Party vote-share denominators include NOTA; party vote numerators exclude NOTA.
    - The statewide vote-share change chart displays the 10 largest gains and 10 largest losses to remain readable; the complete party list is available in the expandable data table.
    - Winner vote-share change compares each constituency's winning candidate share; it is not statewide party vote-share change.
    - Descriptive results do not establish voter motivations or causal explanations.
    """)
st.caption("Telangana Constituency Change Atlas · Electoral data analysis · 2018–2023")
