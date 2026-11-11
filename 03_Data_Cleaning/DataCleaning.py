import pandas as pd
from pathlib import Path

# Find the Excel file automatically
excel_files = list(Path(".").glob("*.xlsx"))

if not excel_files:
    print("No Excel file found!")
    exit()

excel_file = excel_files[0]

print("Reading:", excel_file)

# Read Excel file
df = pd.read_excel(excel_file, engine="openpyxl")

print("Original number of rows:", len(df))

# Remove duplicate rows
df = df.drop_duplicates()

# Remove rows with missing values
df = df.dropna()

# Remove extra spaces from text columns
for column in df.select_dtypes(include="object").columns:
    df[column] = df[column].str.strip()

# Convert numeric columns
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
df["pH"] = pd.to_numeric(df["pH"], errors="coerce")
df["DO(mg/L)"] = pd.to_numeric(df["DO(mg/L)"], errors="coerce")
df["BOD(mg/L)"] = pd.to_numeric(df["BOD(mg/L)"], errors="coerce")
df["Conductivity(µS/cm)"] = pd.to_numeric(
    df["Conductivity(µS/cm)"], errors="coerce"
)

# Remove invalid values
df = df[
    (df["pH"] >= 0) &
    (df["pH"] <= 14) &
    (df["DO(mg/L)"] >= 0) &
    (df["BOD(mg/L)"] >= 0) &
    (df["Conductivity(µS/cm)"] >= 0)
]

# Save cleaned data
df.to_csv("cleandata.csv", index=False)

print("Data cleaning completed.")
print("Final number of rows:", len(df))
print("Cleaned file saved as cleandata.csv")