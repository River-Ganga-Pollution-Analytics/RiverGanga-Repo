"""
GANGA GUARD - RIVER GANGA POLLUTION ANALYSIS
Dataset-specific Python analysis script.

Works with the uploaded dataset:
    River Ganga Pollution Dataset(1).csv
or:
    GangaGuard(2020 - 2026) rawdata.xlsx

Expected columns:
    Year
    Location
    pH
    DO(mg/L)
    BOD(mg/L)
    Conductivity(µS/cm)
    Pollution Level

Run from the project folder:
    python data_analysis.py

Optional: specify another CSV/XLSX file:
    python data_analysis.py "your_dataset.xlsx"
"""

from pathlib import Path
import sys
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "analysis_output"

DEFAULT_DATASET = BASE_DIR / "River Ganga Pollution Dataset.csv"

REQUIRED_COLUMNS = [
    "Year",
    "Location",
    "pH",
    "DO(mg/L)",
    "BOD(mg/L)",
    "Conductivity(µS/cm)",
    "Pollution Level",
]

NUMERIC_COLUMNS = [
    "Year",
    "pH",
    "DO(mg/L)",
    "BOD(mg/L)",
    "Conductivity(µS/cm)",
]


def load_dataset(file_path):
    """Load either the supplied CSV or Excel dataset."""
    file_path = Path(file_path)

    if not file_path.is_absolute():
        file_path = (Path.cwd() / file_path).resolve()

    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {file_path}\n"
            "Place the CSV/XLSX file in the project folder or pass its path."
        )

    extension = file_path.suffix.lower()

    if extension == ".csv":
        data = pd.read_csv(file_path, encoding="utf-8-sig")
    elif extension in (".xlsx", ".xls"):
        # The uploaded workbook contains the GangaGuard_Data sheet.
        data = pd.read_excel(file_path, sheet_name="GangaGuard_Data")
    else:
        raise ValueError("Supported dataset formats are CSV, XLSX and XLS.")

    data.columns = [str(column).strip() for column in data.columns]

    missing = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError(
            "Required columns missing: "
            + ", ".join(missing)
            + "\nColumns found: "
            + ", ".join(data.columns)
        )

    return data[REQUIRED_COLUMNS].copy()


def clean_dataset(data):
    """Clean the exact fields used by the Ganga Guard dataset."""
    df = data.copy()

    df["Location"] = df["Location"].astype("string").str.strip()
    df["Pollution Level"] = (
        df["Pollution Level"].astype("string").str.strip().str.title()
    )

    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    original_count = len(df)

    df = df.dropna(subset=REQUIRED_COLUMNS)
    df = df[
        df["Location"].ne("")
        & df["Pollution Level"].ne("")
    ].copy()

    df["Year"] = df["Year"].astype(int)

    removed_count = original_count - len(df)

    if df.empty:
        raise ValueError("No valid records found after cleaning.")

    return df, removed_count


def save_csv(data, filename):
    data.to_csv(OUTPUT_DIR / filename, index=True if data.index.name else False)


def analyse_kpis(df):
    """Create overall project KPIs."""
    kpis = pd.DataFrame({
        "Metric": [
            "Total Records",
            "Number of Locations",
            "Number of Years",
            "Start Year",
            "End Year",
            "Average pH",
            "Average Dissolved Oxygen (mg/L)",
            "Average Biochemical Oxygen Demand (mg/L)",
            "Average Conductivity (µS/cm)",
            "Good Pollution Records",
            "Moderate Pollution Records",
            "Poor Pollution Records",
        ],
        "Value": [
            len(df),
            df["Location"].nunique(),
            df["Year"].nunique(),
            df["Year"].min(),
            df["Year"].max(),
            round(df["pH"].mean(), 2),
            round(df["DO(mg/L)"].mean(), 2),
            round(df["BOD(mg/L)"].mean(), 2),
            round(df["Conductivity(µS/cm)"].mean(), 2),
            int((df["Pollution Level"] == "Good").sum()),
            int((df["Pollution Level"] == "Moderate").sum()),
            int((df["Pollution Level"] == "Poor").sum()),
        ],
    })

    kpis.to_csv(OUTPUT_DIR / "01_kpi_summary.csv", index=False)
    return kpis


def analyse_location(df):
    """Calculate water-quality averages for all 23 locations."""
    location = (
        df.groupby("Location")
        .agg(
            Record_Count=("Year", "count"),
            Average_pH=("pH", "mean"),
            Average_DO=("DO(mg/L)", "mean"),
            Average_BOD=("BOD(mg/L)", "mean"),
            Average_Conductivity=("Conductivity(µS/cm)", "mean"),
        )
        .round(2)
        .reset_index()
    )

    location.to_csv(OUTPUT_DIR / "02_location_wise_analysis.csv", index=False)

    location.sort_values("Average_BOD", ascending=False).to_csv(
        OUTPUT_DIR / "03_locations_ranked_by_bod.csv", index=False
    )

    location.sort_values("Average_DO", ascending=False).to_csv(
        OUTPUT_DIR / "04_locations_ranked_by_do.csv", index=False
    )

    return location


def analyse_yearly_trends(df):
    """Calculate annual average water-quality measurements."""
    yearly = (
        df.groupby("Year")
        .agg(
            Average_pH=("pH", "mean"),
            Average_DO=("DO(mg/L)", "mean"),
            Average_BOD=("BOD(mg/L)", "mean"),
            Average_Conductivity=("Conductivity(µS/cm)", "mean"),
            Total_Records=("Location", "count"),
        )
        .round(2)
        .reset_index()
    )

    yearly.to_csv(OUTPUT_DIR / "05_yearly_trends.csv", index=False)
    return yearly


def analyse_pollution(df):
    """Calculate Good, Moderate and Poor record counts and percentages."""
    result = (
        df["Pollution Level"]
        .value_counts()
        .reindex(["Good", "Moderate", "Poor"], fill_value=0)
        .rename_axis("Pollution Level")
        .reset_index(name="Record Count")
    )

    result["Percentage"] = (
        result["Record Count"] / len(df) * 100
    ).round(2)

    result.to_csv(OUTPUT_DIR / "06_pollution_distribution.csv", index=False)
    return result


def analyse_state(df):
    """Extract state names from the supplied 'Location, State' values."""
    state_df = df.copy()
    state_df["State"] = state_df["Location"].str.rsplit(",", n=1).str[-1].str.strip()

    result = (
        state_df.groupby("State")
        .agg(
            Total_Records=("Location", "count"),
            Average_BOD=("BOD(mg/L)", "mean"),
            Average_DO=("DO(mg/L)", "mean"),
            Average_pH=("pH", "mean"),
            Average_Conductivity=("Conductivity(µS/cm)", "mean"),
        )
        .round(2)
        .reset_index()
        .sort_values("Total_Records", ascending=False)
    )

    result.to_csv(OUTPUT_DIR / "07_state_wise_analysis.csv", index=False)
    return result


def analyse_correlations(df):
    """Calculate correlations among numeric water-quality parameters."""
    columns = [
        "pH",
        "DO(mg/L)",
        "BOD(mg/L)",
        "Conductivity(µS/cm)",
    ]

    correlation = df[columns].corr().round(3)
    correlation.to_csv(OUTPUT_DIR / "08_correlation_matrix.csv")
    return correlation


def create_charts(df, yearly, pollution, location):
    """Generate charts for the project report and presentation."""

    # 1. Average BOD by location
    chart_data = location.sort_values("Average_BOD", ascending=True)
    plt.figure(figsize=(12, 8))
    plt.barh(chart_data["Location"], chart_data["Average_BOD"])
    plt.title("Average BOD by Ganga Location")
    plt.xlabel("Average BOD (mg/L)")
    plt.ylabel("Location")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "01_average_bod_by_location.png", dpi=300)
    plt.close()

    # 2. Average DO by location
    chart_data = location.sort_values("Average_DO", ascending=True)
    plt.figure(figsize=(12, 8))
    plt.barh(chart_data["Location"], chart_data["Average_DO"])
    plt.title("Average Dissolved Oxygen by Ganga Location")
    plt.xlabel("Average DO (mg/L)")
    plt.ylabel("Location")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "02_average_do_by_location.png", dpi=300)
    plt.close()

    # 3. Pollution level distribution
    plt.figure(figsize=(8, 7))
    plt.pie(
        pollution["Record Count"],
        labels=pollution["Pollution Level"],
        autopct="%1.1f%%",
        startangle=90,
    )
    plt.title("River Ganga Pollution Level Distribution")
    plt.axis("equal")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "03_pollution_distribution.png", dpi=300)
    plt.close()

    # 4. Yearly BOD trend
    plt.figure(figsize=(10, 6))
    plt.plot(
        yearly["Year"],
        yearly["Average_BOD"],
        marker="o",
        linewidth=2,
    )
    plt.title("Yearly Average BOD Trend (2020–2026)")
    plt.xlabel("Year")
    plt.ylabel("Average BOD (mg/L)")
    plt.xticks(yearly["Year"])
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "04_yearly_bod_trend.png", dpi=300)
    plt.close()

    # 5. Yearly DO trend
    plt.figure(figsize=(10, 6))
    plt.plot(
        yearly["Year"],
        yearly["Average_DO"],
        marker="o",
        linewidth=2,
    )
    plt.title("Yearly Average Dissolved Oxygen Trend (2020–2026)")
    plt.xlabel("Year")
    plt.ylabel("Average DO (mg/L)")
    plt.xticks(yearly["Year"])
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "05_yearly_do_trend.png", dpi=300)
    plt.close()

    # 6. pH versus BOD
    plt.figure(figsize=(9, 6))
    plt.scatter(df["pH"], df["BOD(mg/L)"], alpha=0.6)
    plt.title("Relationship Between pH and BOD")
    plt.xlabel("pH")
    plt.ylabel("BOD (mg/L)")
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "06_ph_vs_bod.png", dpi=300)
    plt.close()

    # 7. Conductivity versus BOD
    plt.figure(figsize=(9, 6))
    plt.scatter(
        df["Conductivity(µS/cm)"],
        df["BOD(mg/L)"],
        alpha=0.6,
    )
    plt.title("Relationship Between Conductivity and BOD")
    plt.xlabel("Conductivity (µS/cm)")
    plt.ylabel("BOD (mg/L)")
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "07_conductivity_vs_bod.png", dpi=300)
    plt.close()


def create_report(df, kpis, pollution, yearly, location, correlation):
    """Save a readable summary report."""
    worst_bod = location.loc[location["Average_BOD"].idxmax()]
    best_do = location.loc[location["Average_DO"].idxmax()]
    highest_pollution = pollution.loc[pollution["Record Count"].idxmax()]

    lines = [
        "GANGA GUARD - RIVER GANGA POLLUTION ANALYSIS",
        "=" * 55,
        "",
        "DATASET OVERVIEW",
        f"Total records: {len(df)}",
        f"Locations: {df['Location'].nunique()}",
        f"Years: {df['Year'].min()} to {df['Year'].max()}",
        "",
        "OVERALL WATER QUALITY AVERAGES",
        f"Average pH: {df['pH'].mean():.2f}",
        f"Average DO: {df['DO(mg/L)'].mean():.2f} mg/L",
        f"Average BOD: {df['BOD(mg/L)'].mean():.2f} mg/L",
        f"Average Conductivity: {df['Conductivity(µS/cm)'].mean():.2f} µS/cm",
        "",
        "POLLUTION DISTRIBUTION",
    ]

    for _, row in pollution.iterrows():
        lines.append(
            f"{row['Pollution Level']}: {row['Record Count']} records "
            f"({row['Percentage']:.2f}%)"
        )

    lines.extend([
        "",
        "LOCATION HIGHLIGHTS",
        f"Highest average BOD: {worst_bod['Location']} "
        f"({worst_bod['Average_BOD']:.2f} mg/L)",
        f"Highest average DO: {best_do['Location']} "
        f"({best_do['Average_DO']:.2f} mg/L)",
        f"Most frequent pollution category: {highest_pollution['Pollution Level']}",
        "",
        "YEARLY AVERAGES",
        yearly.to_string(index=False),
        "",
        "CORRELATION MATRIX",
        correlation.to_string(),
        "",
        "Interpretation note: Correlation indicates association, not causation.",
        "Pollution Level values are analysed as provided in the dataset; "
        "no new category thresholds are assumed.",
    ])

    (OUTPUT_DIR / "09_analysis_report.txt").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    dataset_path = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else DEFAULT_DATASET
    )

    print("\nGANGA GUARD - DATA ANALYSIS")
    print("=" * 45)
    print(f"Reading dataset: {dataset_path}")

    raw_df = load_dataset(dataset_path)
    df, removed = clean_dataset(raw_df)

    print(f"Original records : {len(raw_df)}")
    print(f"Valid records    : {len(df)}")
    print(f"Removed records  : {removed}")
    print(f"Unique locations : {df['Location'].nunique()}")
    print(f"Year range       : {df['Year'].min()} - {df['Year'].max()}")

    df.to_csv(OUTPUT_DIR / "00_cleaned_dataset.csv", index=False)

    kpis = analyse_kpis(df)
    location = analyse_location(df)
    yearly = analyse_yearly_trends(df)
    pollution = analyse_pollution(df)
    analyse_state(df)
    correlation = analyse_correlations(df)

    create_charts(df, yearly, pollution, location)
    create_report(df, kpis, pollution, yearly, location, correlation)

    print("\nPROJECT KPI SUMMARY")
    print(kpis.to_string(index=False))

    print("\nPOLLUTION LEVEL DISTRIBUTION")
    print(pollution.to_string(index=False))

    print("\nANALYSIS COMPLETED SUCCESSFULLY")
    print(f"Output folder: {OUTPUT_DIR}")
    print("CSV summaries, charts and text report have been generated.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nANALYSIS FAILED: {exc}")
        sys.exit(1)
