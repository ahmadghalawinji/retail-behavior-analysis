"""
segment.py
----------
RFM (Recency, Frequency, Monetary) customer segmentation.

Segments (descending value):
  Champions | Loyal Customers | At-Risk Customers | Hibernating | Lost
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

CHARTS_DIR = Path("outputs/charts")
DPI = 150

N_QUANTILES = 5
THRESHOLDS = {"champions": 13, "loyal": 10, "at_risk": 7, "hibernating": 4}

SEGMENT_ORDER  = ["Champions", "Loyal Customers", "At-Risk Customers", "Hibernating", "Lost"]
SEGMENT_COLORS = {
    "Champions":         "#2ecc71",
    "Loyal Customers":   "#3498db",
    "At-Risk Customers": "#f39c12",
    "Hibernating":       "#e74c3c",
    "Lost":              "#95a5a6",
}


def _label(score: int) -> str:
    if score >= THRESHOLDS["champions"]:   return "Champions"
    if score >= THRESHOLDS["loyal"]:       return "Loyal Customers"
    if score >= THRESHOLDS["at_risk"]:     return "At-Risk Customers"
    if score >= THRESHOLDS["hibernating"]: return "Hibernating"
    return "Lost"


def compute_rfm(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    snapshot = df["InvoiceDate"].max() + pd.Timedelta(days=1)

    rfm = df.groupby("CustomerID").agg(
        Recency   = ("InvoiceDate",  lambda x: (snapshot - x.max()).days),
        Frequency = ("InvoiceNo",    "nunique"),
        Monetary  = ("TotalRevenue", "sum"),
    ).reset_index()

    q = N_QUANTILES
    rfm["R_Score"] = pd.qcut(rfm["Recency"], q=q, labels=range(q, 0, -1), duplicates="drop")
    rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), q=q, labels=range(1, q + 1))
    rfm["M_Score"] = pd.qcut(rfm["Monetary"].rank(method="first"),  q=q, labels=range(1, q + 1))

    rfm["RFM_Score"] = rfm[["R_Score", "F_Score", "M_Score"]].astype(int).sum(axis=1)
    rfm["Segment"]   = rfm["RFM_Score"].map(_label)

    total = rfm["Monetary"].sum()
    summary = (
        rfm.groupby("Segment")
        .agg(Customers=("CustomerID", "count"),
             AvgRecency=("Recency", "mean"),
             AvgFrequency=("Frequency", "mean"),
             TotalRevenue=("Monetary", "sum"))
        .round(1)
        .reindex([s for s in SEGMENT_ORDER if s in rfm["Segment"].unique()])
    )
    summary["RevenueShare%"] = (summary["TotalRevenue"] / total * 100).round(1)

    print("\nRFM Segment Summary:")
    print(summary.to_string())
    return rfm, summary


def plot_rfm(rfm: pd.DataFrame, summary: pd.DataFrame) -> None:
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    present = [s for s in SEGMENT_ORDER if s in summary.index]
    colors  = [SEGMENT_COLORS[s] for s in present]

    # Counts + revenue share
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    axes[0].bar(present, summary.loc[present, "Customers"],    color=colors, edgecolor="white")
    axes[0].set_title("Customer Count by Segment",  fontsize=13, fontweight="bold")
    axes[0].set_xticklabels(present, rotation=30, ha="right")

    axes[1].bar(present, summary.loc[present, "RevenueShare%"], color=colors, edgecolor="white")
    axes[1].set_title("Revenue Share % by Segment", fontsize=13, fontweight="bold")
    axes[1].set_xticklabels(present, rotation=30, ha="right")

    plt.tight_layout()
    path = CHARTS_DIR / "07_rfm_segments.png"
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")

    # Correlation heatmap
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.heatmap(rfm[["Recency", "Frequency", "Monetary"]].corr(),
                annot=True, fmt=".2f", cmap="coolwarm", square=True, ax=ax)
    ax.set_title("RFM Correlation Matrix", fontsize=13, fontweight="bold")
    plt.tight_layout()
    path = CHARTS_DIR / "08_rfm_correlation.png"
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


if __name__ == "__main__":
    from clean import load_and_clean
    df = load_and_clean()
    rfm, summary = compute_rfm(df)
    plot_rfm(rfm, summary)
