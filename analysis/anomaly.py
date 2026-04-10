"""
anomaly.py
----------
Two anomaly-detection methods:
  1. Volume anomalies  — months whose order count deviates from the rolling average.
  2. Spend outliers    — customers flagged by the IQR (Tukey) fence.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

CHARTS_DIR     = Path("outputs/charts")
DPI            = 150
ROLLING_WINDOW = 3
IQR_MULTIPLIER = 1.5

plt.rcParams.update({"font.size": 11, "axes.titlesize": 16, "axes.labelsize": 13})


def _fmt_gbp(value, _=None) -> str:
    if value >= 1_000_000:
        return f"£{value/1_000_000:.1f}M"
    if value >= 1_000:
        return f"£{value/1_000:.0f}K"
    return f"£{value:.0f}"


def detect_volume_anomalies(df: pd.DataFrame, top_n: int = 5):
    monthly = (
        df.groupby("YearMonth")["InvoiceNo"]
        .nunique().reset_index()
        .rename(columns={"InvoiceNo": "OrderCount"})
    )
    monthly["label"]        = monthly["YearMonth"].astype(str)
    monthly["RollingAvg"]   = monthly["OrderCount"].rolling(ROLLING_WINDOW, center=True, min_periods=1).mean()
    monthly["Deviation"]    = (monthly["OrderCount"] - monthly["RollingAvg"]).abs()
    monthly["DeviationPct"] = (monthly["Deviation"] / monthly["RollingAvg"] * 100).round(1)

    top = monthly.sort_values("Deviation", ascending=False).head(top_n)
    print("\nTop volume anomaly months:")
    print(top[["label", "OrderCount", "RollingAvg", "DeviationPct"]].to_string(index=False))
    return monthly, top


def detect_spend_outliers(rfm: pd.DataFrame):
    q1, q3 = rfm["Monetary"].quantile(0.25), rfm["Monetary"].quantile(0.75)
    upper   = q3 + IQR_MULTIPLIER * (q3 - q1)
    outliers = rfm[rfm["Monetary"] > upper].sort_values("Monetary", ascending=False)
    print(f"\nIQR upper fence: {_fmt_gbp(upper)} — {len(outliers)} outlier customers")
    return outliers, upper


def plot_anomalies(df: pd.DataFrame, rfm: pd.DataFrame) -> None:
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    monthly, top = detect_volume_anomalies(df)
    _, upper     = detect_spend_outliers(rfm)

    # ── Chart 1: volume with rolling average + annotations ────────────────────
    peak_idx   = monthly["OrderCount"].idxmax()
    peak_label = monthly.loc[peak_idx, "label"]
    peak_value = monthly.loc[peak_idx, "OrderCount"]

    fig, ax = plt.subplots(figsize=(13, 5))
    ax.plot(monthly["label"], monthly["OrderCount"],
            marker="o", label="Monthly Orders", color="steelblue", linewidth=2, markersize=5)
    ax.plot(monthly["label"], monthly["RollingAvg"],
            linestyle="--", label=f"{ROLLING_WINDOW}-Month Rolling Avg",
            color="tomato", linewidth=1.8)

    # Annotate the peak month
    ax.annotate(
        f"Peak: {peak_value:,} orders\n({peak_label})",
        xy=(peak_idx, peak_value),
        xytext=(peak_idx - 2.5, peak_value * 0.96),
        fontsize=10, color="steelblue", fontweight="bold",
        arrowprops=dict(arrowstyle="->", color="steelblue", lw=1.2),
    )

    # Annotate the largest deviation month (if different from peak)
    top1 = top.iloc[0]
    top1_idx = monthly[monthly["label"] == top1["label"]].index[0]
    if top1_idx != peak_idx:
        ax.annotate(
            f"+{top1['DeviationPct']:.0f}% vs avg",
            xy=(top1_idx, monthly.loc[top1_idx, "OrderCount"]),
            xytext=(top1_idx + 0.5, monthly.loc[top1_idx, "OrderCount"] * 1.04),
            fontsize=9, color="darkorange", fontweight="bold",
            arrowprops=dict(arrowstyle="->", color="darkorange", lw=1.0),
        )

    ax.set_title("Monthly Order Volume — Anomaly Detection", fontweight="bold")
    ax.set_xlabel("Month")
    ax.set_ylabel("Number of Orders")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.legend(fontsize=10)
    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.tight_layout()
    path = CHARTS_DIR / "09_volume_anomaly.png"
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")

    # ── Chart 2: spend boxplot with IQR fence annotation ─────────────────────
    plot_data = rfm[rfm["Monetary"] < rfm["Monetary"].quantile(0.99)]["Monetary"]
    n_outliers = (rfm["Monetary"] > upper).sum()

    fig, ax = plt.subplots(figsize=(9, 3))
    ax.boxplot(plot_data, vert=False, patch_artist=True,
               boxprops=dict(facecolor="lightsteelblue", color="steelblue"),
               medianprops=dict(color="tomato", linewidth=2),
               flierprops=dict(marker="o", markerfacecolor="orange", markersize=3, alpha=0.5))

    ax.axvline(upper, color="red", linestyle="--", linewidth=1.5,
               label=f"IQR upper fence: {_fmt_gbp(upper)}")

    ax.annotate(
        f"{n_outliers} high-value\noutlier customers →",
        xy=(upper, 1.15),
        xytext=(upper * 0.72, 1.32),
        fontsize=10, color="red", fontweight="bold",
        arrowprops=dict(arrowstyle="->", color="red", lw=1.2),
    )

    ax.set_title("Customer Lifetime Spend Distribution (excl. top 1%)", fontweight="bold")
    ax.set_xlabel("Total Customer Spend (£)")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(_fmt_gbp))
    ax.legend(fontsize=10)
    plt.tight_layout()
    path = CHARTS_DIR / "10_spend_outliers.png"
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


if __name__ == "__main__":
    from clean import load_and_clean
    from segment import compute_rfm
    df = load_and_clean()
    rfm, _ = compute_rfm(df)
    plot_anomalies(df, rfm)
