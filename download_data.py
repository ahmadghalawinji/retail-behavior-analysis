"""
download_data.py
----------------
Downloads the Online Retail dataset from the UCI ML Repository
and saves it to data/online_retail.csv.

Usage:
    python download_data.py
"""

import urllib.request
import pathlib
import sys

DATA_DIR = pathlib.Path("data")
OUT_PATH = DATA_DIR / "online_retail.csv"

# UCI ML Repository — Online Retail dataset (Excel format)
URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00352/Online%20Retail.xlsx"
XLSX_PATH = DATA_DIR / "online_retail.xlsx"


def download():
    DATA_DIR.mkdir(exist_ok=True)

    if OUT_PATH.exists():
        print(f"Already exists: {OUT_PATH} — skipping download.")
        return

    print(f"Downloading from UCI ML Repository...")
    try:
        urllib.request.urlretrieve(URL, XLSX_PATH, reporthook=_progress)
    except Exception as e:
        sys.exit(f"\nDownload failed: {e}")

    print(f"\nConverting xlsx → csv...")
    try:
        import pandas as pd
        df = pd.read_excel(XLSX_PATH, engine="openpyxl")
        df.to_csv(OUT_PATH, index=False, encoding="ISO-8859-1")
        XLSX_PATH.unlink()  # remove the intermediate xlsx
        print(f"Saved: {OUT_PATH} ({len(df):,} rows)")
    except ImportError:
        sys.exit("pandas / openpyxl not installed. Run: pip install pandas openpyxl")


def _progress(block, block_size, total):
    downloaded = block * block_size
    if total > 0:
        pct = min(downloaded / total * 100, 100)
        mb = downloaded / 1_048_576
        print(f"\r  {pct:.1f}%  ({mb:.1f} MB)", end="", flush=True)


if __name__ == "__main__":
    download()
