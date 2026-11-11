# ============================================================
# GANGAGUARD - DATA VISUALISATION
# ============================================================

import pandas as pd
import plotly.express as px
from pathlib import Path

# 1. LOAD DATASET
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "River Ganga Pollution Dataset.csv"
OUTPUT_DIR = BASE_DIR / "outputs" / "charts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_FILE)
df.columns = df.columns.str.strip()

print("Dataset loaded successfully!")
print("\nFirst 5 rows:")
print(df.head())

print("\nDataset shape:", df.shape)
print("\nColumn names:")
print(df.columns.tolist())

# Check required columns
required_columns = [
    "Year",
    "Location",
    "pH",
    "DO(mg/L)",
    "BOD(mg/L)",
    "Conductivity(µS/cm)",
    "Pollution Level"
]

missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    raise ValueError(f"Missing columns: {missing_columns}")

# Convert numeric columns
numeric_columns = [
    "Year",
    "pH",
    "DO(mg/L)",
    "BOD(mg/L)",
    "Conductivity(µS/cm)"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df["Location"] = df["Location"].astype("string").str.strip()
df["Pollution Level"] = (
    df["Pollution Level"].astype("string").str.strip()
)

df = df.dropna(
    subset=required_columns
).copy()

df = df[
    df["Location"].ne("")
    & df["Pollution Level"].ne("")
]

print("\nValid records:", len(df))


# Function to display and save each chart
def show_chart(fig, filename):
    fig.show()
    fig.write_html(
        str(OUTPUT_DIR / filename),
        include_plotlyjs=True
    )
    print("Saved:", OUTPUT_DIR / filename)


# ============================================================
# 2. BAR CHART - AVERAGE BOD BY LOCATION
# ============================================================

location_bod = (
    df.groupby("Location", as_index=False)["BOD(mg/L)"]
    .mean()
    .sort_values("BOD(mg/L)", ascending=False)
    .head(20)
)

fig = px.bar(
    location_bod,
    x="Location",
    y="BOD(mg/L)",
    title="Top 20 Locations by Average BOD",
    labels={
        "Location": "Location",
        "BOD(mg/L)": "Average BOD (mg/L)"
    },
    hover_data={"BOD(mg/L)": ":.2f"}
)

fig.update_layout(
    xaxis_tickangle=-45,
    template="plotly_white"
)

show_chart(fig, "01_average_bod_by_location.html")


# ============================================================
# 3. BAR CHART - AVERAGE WATER QUALITY BY YEAR
# ============================================================

yearly_data = (
    df.groupby("Year", as_index=False)[
        ["pH", "DO(mg/L)", "BOD(mg/L)",
         "Conductivity(µS/cm)"]
    ]
    .mean()
    .round(2)
)

yearly_long = yearly_data.melt(
    id_vars="Year",
    var_name="Parameter",
    value_name="Average Value"
)

fig = px.line(
    yearly_long,
    x="Year",
    y="Average Value",
    color="Parameter",
    markers=True,
    title="Year-wise Water Quality Trends",
    labels={
        "Year": "Year",
        "Average Value": "Average Measurement",
        "Parameter": "Water Quality Parameter"
    }
)

fig.update_layout(
    template="plotly_white",
    hovermode="x unified"
)

show_chart(fig, "02_yearly_water_quality_trends.html")


# ============================================================
# 4. INTERACTIVE PIE CHART - POLLUTION LEVEL DISTRIBUTION
# ============================================================

pollution_counts = (
    df["Pollution Level"]
    .value_counts()
    .rename_axis("Pollution Level")
    .reset_index(name="Count")
)

fig = px.pie(
    pollution_counts,
    names="Pollution Level",
    values="Count",
    title="Distribution of Ganga Pollution Levels",
    hole=0.4
)

fig.update_traces(
    textinfo="percent+label",
    hovertemplate=(
        "Pollution Level: %{label}<br>"
        "Records: %{value}<br>"
        "Percentage: %{percent}<extra></extra>"
    )
)

fig.update_layout(template="plotly_white")

show_chart(fig, "03_pollution_level_distribution.html")


# ============================================================
# 5. HISTOGRAM - BOD DISTRIBUTION
# ============================================================

fig = px.histogram(
    df,
    x="BOD(mg/L)",
    nbins=30,
    title="Distribution of Biochemical Oxygen Demand (BOD)",
    labels={
        "BOD(mg/L)": "BOD (mg/L)",
        "count": "Number of Records"
    },
    marginal="box"
)

fig.update_layout(template="plotly_white")

show_chart(fig, "04_bod_histogram.html")


# ============================================================
# 6. BOX PLOT - BOD BY POLLUTION LEVEL
# ============================================================

fig = px.box(
    df,
    x="Pollution Level",
    y="BOD(mg/L)",
    color="Pollution Level",
    points="outliers",
    title="BOD Distribution by Pollution Level",
    labels={
        "Pollution Level": "Pollution Category",
        "BOD(mg/L)": "BOD (mg/L)"
    }
)

fig.update_layout(
    template="plotly_white",
    showlegend=False
)

show_chart(fig, "05_bod_boxplot_by_pollution.html")


# ============================================================
# 7. SCATTER PLOT - DO VS BOD
# ============================================================

fig = px.scatter(
    df,
    x="DO(mg/L)",
    y="BOD(mg/L)",
    color="Pollution Level",
    hover_name="Location",
    hover_data=["Year", "pH", "Conductivity(µS/cm)"],
    title="Dissolved Oxygen vs Biochemical Oxygen Demand",
    labels={
        "DO(mg/L)": "Dissolved Oxygen (mg/L)",
        "BOD(mg/L)": "Biochemical Oxygen Demand (mg/L)",
        "Pollution Level": "Pollution Category"
    }
)

fig.update_layout(template="plotly_white")

show_chart(fig, "06_do_vs_bod_scatter.html")


# ============================================================
# 8. BAR CHART - AVERAGE MEASUREMENTS BY POLLUTION LEVEL
# ============================================================

pollution_averages = (
    df.groupby("Pollution Level", as_index=False)[
        ["pH", "DO(mg/L)", "BOD(mg/L)",
         "Conductivity(µS/cm)"]
    ]
    .mean()
    .round(2)
)

pollution_long = pollution_averages.melt(
    id_vars="Pollution Level",
    var_name="Parameter",
    value_name="Average Value"
)

fig = px.bar(
    pollution_long,
    x="Pollution Level",
    y="Average Value",
    color="Parameter",
    barmode="group",
    title="Average Water Quality Measurements by Pollution Level",
    labels={
        "Pollution Level": "Pollution Category",
        "Average Value": "Average Measurement",
        "Parameter": "Parameter"
    }
)

fig.update_layout(template="plotly_white")

show_chart(fig, "07_water_quality_by_pollution.html")


# ============================================================
# 9. CORRELATION HEATMAP
# ============================================================

correlation_columns = [
    "pH",
    "DO(mg/L)",
    "BOD(mg/L)",
    "Conductivity(µS/cm)"
]

correlation_matrix = df[
    correlation_columns
].corr()

print("\nCorrelation Matrix:")
print(correlation_matrix.round(3))

fig = px.imshow(
    correlation_matrix,
    text_auto=".2f",
    aspect="auto",
    color_continuous_scale="RdBu_r",
    zmin=-1,
    zmax=1,
    title="Correlation Between Water Quality Parameters",
    labels={
        "x": "Water Quality Parameter",
        "y": "Water Quality Parameter",
        "color": "Correlation"
    }
)

fig.update_layout(template="plotly_white")

show_chart(fig, "08_water_quality_correlation.html")


# ============================================================
# 10. 3D SCATTER PLOT - WATER QUALITY
# ============================================================

fig = px.scatter_3d(
    df,
    x="pH",
    y="DO(mg/L)",
    z="BOD(mg/L)",
    color="Pollution Level",
    hover_name="Location",
    hover_data=["Year"],
    title="3D Water Quality Visualization",
    labels={
        "pH": "pH Level",
        "DO(mg/L)": "Dissolved Oxygen (mg/L)",
        "BOD(mg/L)": "BOD (mg/L)",
        "Pollution Level": "Pollution Category"
    }
)

fig.update_layout(template="plotly_white")

show_chart(fig, "09_3d_water_quality.html")


# ============================================================
# 11. BAR CHART - POLLUTION RECORD COUNTS BY YEAR
# ============================================================

year_pollution = (
    df.groupby(["Year", "Pollution Level"])
    .size()
    .reset_index(name="Record Count")
)

fig = px.bar(
    year_pollution,
    x="Year",
    y="Record Count",
    color="Pollution Level",
    barmode="group",
    title="Pollution Level Comparison Across Years",
    labels={
        "Year": "Year",
        "Record Count": "Number of Records",
        "Pollution Level": "Pollution Category"
    }
)

fig.update_layout(template="plotly_white")

show_chart(fig, "10_pollution_by_year.html")


# ============================================================
# 12. EXPORT SUMMARY TABLES
# ============================================================

summary = df[
    ["pH", "DO(mg/L)", "BOD(mg/L)", "Conductivity(µS/cm)"]
].describe().round(2)

summary.to_csv(
    OUTPUT_DIR / "summary_statistics.csv"
)

yearly_data.to_csv(
    OUTPUT_DIR / "yearly_averages.csv",
    index=False
)

location_bod.to_csv(
    OUTPUT_DIR / "location_bod.csv",
    index=False
)

pollution_counts.to_csv(
    OUTPUT_DIR / "pollution_counts.csv",
    index=False
)

print("\n========================================")
print("GANGAGUARD VISUALIZATION COMPLETED")
print("========================================")
print("Total records analysed:", len(df))
print("Charts saved in:", OUTPUT_DIR)
print("Summary tables saved successfully.")
print("========================================")