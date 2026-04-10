"""
run.py
------
Entry point — runs the full analysis pipeline end-to-end.

Usage:
    cd retail-behavior-analysis
    python analysis/run.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from clean   import load_and_clean
from explore import plot_all
from segment import compute_rfm, plot_rfm
from anomaly import plot_anomalies


def main():
    print("=== Retail Behaviour Analysis ===\n")

    print("[1/4] Loading and cleaning data...")
    df = load_and_clean()

    print("\n[2/4] Generating EDA charts...")
    plot_all(df)

    print("\n[3/4] RFM segmentation...")
    rfm, summary = compute_rfm(df)
    plot_rfm(rfm, summary)

    print("\n[4/4] Anomaly detection...")
    plot_anomalies(df, rfm)

    print("\nDone. Charts saved to outputs/charts/")


if __name__ == "__main__":
    main()
