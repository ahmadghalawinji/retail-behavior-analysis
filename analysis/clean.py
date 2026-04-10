"""
clean.py
--------
Load and clean the Online Retail dataset.
"""

import pandas as pd


DATA_PATH = "data/online_retail.csv"


def load_and_clean(path: str = DATA_PATH) -> pd.DataFrame:
    suffix = path.rsplit(".", 1)[-1].lower()
    if suffix == "xlsx":
        df = pd.read_excel(path, engine="openpyxl")
    else:
        df = pd.read_csv(path, encoding="ISO-8859-1")

    # Drop rows we cannot use
    df = df.dropna(subset=["CustomerID", "Description"])
    df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]   # cancellations
    df = df[(df["Quantity"] >= 1) & (df["UnitPrice"] >= 0.01)]
    df = df.drop_duplicates()

    # Fix types
    df["CustomerID"] = df["CustomerID"].astype(int)
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

    # Derived columns
    df["TotalRevenue"] = df["Quantity"] * df["UnitPrice"]
    df["YearMonth"]    = df["InvoiceDate"].dt.to_period("M")
    df["DayName"]      = df["InvoiceDate"].dt.strftime("%A")
    df["Hour"]         = df["InvoiceDate"].dt.hour

    print(f"Loaded {len(df):,} rows after cleaning.")
    return df


if __name__ == "__main__":
    df = load_and_clean()
    print(df.head())
