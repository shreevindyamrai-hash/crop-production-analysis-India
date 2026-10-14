"""
Crop Production Analysis (India) - Pandas + SQL + Matplotlib

Usage:
    python crop_analysis.py crop_production.csv

Expected columns (Kaggle "Crop Production in India"):
    State_Name, District_Name, Crop_Year, Season, Crop, Area, Production
Outputs (in ./output):
    cleaned_data.csv, crops.db, 4 PNG charts, insights.md
"""
import sys, sqlite3
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path("output"); OUT.mkdir(exist_ok=True)

def load_and_clean(path):
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    rename = {"state_name": "state", "district_name": "district", "crop_year": "year"}
    df = df.rename(columns=rename)
    need = ["state", "district", "year", "season", "crop", "area", "production"]
    missing = [c for c in need if c not in df.columns]
    if missing:
        sys.exit(f"Missing columns: {missing}. Found: {list(df.columns)}")
    raw_rows = len(df)
    for c in ["state", "district", "season", "crop"]:
        df[c] = df[c].astype(str).str.strip().str.title()
    df["area"] = pd.to_numeric(df["area"], errors="coerce")
    df["production"] = pd.to_numeric(df["production"], errors="coerce")
    df = df.dropna(subset=["area", "production", "year"])
    df = df[(df["area"] > 0) & (df["production"] >= 0)].drop_duplicates()
    df["year"] = df["year"].astype(int)
    df["yield_per_ha"] = df["production"] / df["area"]
    # Drop extreme outliers in yield (above the 99.5th percentile) - documented in README
    cap = df["yield_per_ha"].quantile(0.995)
    df = df[df["yield_per_ha"] <= cap]
    print(f"Rows: {raw_rows} raw -> {len(df)} after cleaning")
    return df, raw_rows

def q(con, sql):
    return pd.read_sql_query(sql, con)

def main(path):
    df, raw_rows = load_and_clean(path)
    df.to_csv(OUT / "cleaned_data.csv", index=False)
    con = sqlite3.connect(OUT / "crops.db")
    df.to_sql("crops", con, if_exists="replace", index=False)

    top_crops = q(con, """SELECT crop, ROUND(SUM(production)) AS total_production
                          FROM crops GROUP BY crop ORDER BY total_production DESC LIMIT 10""")
    state_yield = q(con, """SELECT state, ROUND(AVG(yield_per_ha), 2) AS avg_yield
                            FROM crops GROUP BY state HAVING COUNT(*) >= 50
                            ORDER BY avg_yield DESC LIMIT 10""")
    yearly = q(con, """SELECT year, ROUND(SUM(production)) AS total_production, ROUND(SUM(area)) AS total_area
                       FROM crops GROUP BY year ORDER BY year""")
    season = q(con, """SELECT season, ROUND(SUM(production)) AS total_production
                       FROM crops GROUP BY season ORDER BY total_production DESC""")

    plt.rcParams.update({"figure.dpi": 130, "axes.spines.top": False, "axes.spines.right": False})
    def bar(data, x, y, title, fname, horizontal=True):
        fig, ax = plt.subplots(figsize=(7, 4))
        d = data.iloc[::-1] if horizontal else data
        (ax.barh if horizontal else ax.bar)(d[x], d[y], color="#2b6cb0")
        ax.set_title(title, loc="left", fontweight="bold"); fig.tight_layout()
        fig.savefig(OUT / fname); plt.close(fig)
    bar(top_crops, "crop", "total_production", "Top 10 crops by total production", "top_crops.png")
    bar(state_yield, "state", "avg_yield", "Top 10 states by average yield (production per hectare)", "state_yield.png")
    bar(season, "season", "total_production", "Production by season", "season.png", horizontal=False)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(yearly["year"], yearly["total_production"], marker="o", color="#2b6cb0")
    ax.set_title("Total production by year", loc="left", fontweight="bold"); fig.tight_layout()
    fig.savefig(OUT / "yearly_trend.png"); plt.close(fig)

    first, last = yearly.iloc[0], yearly.iloc[-1]
    change = (last.total_production - first.total_production) / first.total_production * 100
    lines = [
        "# Insights (computed from the data)",
        f"- Records analysed: {len(df):,} (from {raw_rows:,} raw rows after cleaning); years {int(first.year)}-{int(last.year)}.",
        f"- Highest-production crop: {top_crops.iloc[0].crop} ({top_crops.iloc[0].total_production:,.0f} total).",
        f"- Highest average yield state: {state_yield.iloc[0].state} ({state_yield.iloc[0].avg_yield} per hectare).",
        f"- Top season by production: {season.iloc[0].season}.",
        f"- Total production changed by {change:+.1f}% from {int(first.year)} to {int(last.year)} "
        "(check the chart: partial first/last years can distort this).",
    ]
    (OUT / "insights.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines)); print("Saved charts and files in ./output")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
