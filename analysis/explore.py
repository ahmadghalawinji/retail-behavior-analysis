"""
explore.py
----------
Exploratory Data Analysis — generates and saves charts to outputs/charts/.

Chart standards applied across all plots:
  - Title font size 16, axis labels 13, tick labels 11
  - Revenue formatted as £1.2M / £450K (no raw 7-digit numbers)
  - Key moments annotated directly on the chart
"""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import pandas as pd

CHARTS_DIR = Path("outputs/charts")
DPI = 150
DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("husl")
plt.rcParams.update({"font.size": 11, "axes.titlesize": 16, "axes.labelsize": 13})


def _fmt_gbp(value, _=None) -> str:
    """Format a pound value as £1.2M or £450K."""
    if value >= 1_000_000:
        return f"£{value/1_000_000:.1f}M"
    if value >= 1_000:
        return f"£{value/1_000:.0f}K"
    return f"£{value:.0f}"


def _save(fig, name: str) -> Path:
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    path = CHARTS_DIR / f"{name}.png"
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")
    return path


def plot_monthly_revenue(df: pd.DataFrame) -> Path:
    monthly = df.groupby("YearMonth")["TotalRevenue"].sum().reset_index()
    monthly["label"] = monthly["YearMonth"].astype(str)

    peak_idx = monthly["TotalRevenue"].idxmax()
    peak_label = monthly.loc[peak_idx, "label"]
    peak_value = monthly.loc[peak_idx, "TotalRevenue"]

    fig, ax = plt.subplots(figsize=(13, 5))
    bars = ax.bar(monthly["label"], monthly["TotalRevenue"],
                  color="steelblue", edgecolor="white")

    # Highlight peak bar
    bars[peak_idx].set_color("darkorange")

    # Annotate peak
    ax.annotate(
        f"Peak: {_fmt_gbp(peak_value)}",
        xy=(peak_idx, peak_value),
        xytext=(peak_idx + 0.6, peak_value * 1.04),
        fontsize=10, color="darkorange", fontweight="bold",
        arrowprops=dict(arrowstyle="->", color="darkorange", lw=1.2),
    )

    ax.set_title("Monthly Revenue Trend (Dec 2010 – Dec 2011)", fontweight="bold")
    ax.set_xlabel("Month")
    ax.set_ylabel("Total Revenue (£)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(_fmt_gbp))
    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.tight_layout()
    return _save(fig, "01_monthly_revenue")


def plot_international_markets(df: pd.DataFrame) -> Path:
    intl = (
        df[df["Country"] != "United Kingdom"]
        .groupby("Country")["TotalRevenue"]
        .sum().sort_values(ascending=False).head(10)
    )

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = intl.plot(kind="bar", ax=ax, color="coral", edgecolor="white")

    # Label each bar with formatted value
    for bar in ax.patches:
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + intl.max() * 0.01,
            _fmt_gbp(bar.get_height()),
            ha="center", va="bottom", fontsize=9, fontweight="bold"
        )

    ax.set_title("Top 10 International Markets by Revenue", fontweight="bold")
    ax.set_xlabel("Country")
    ax.set_ylabel("Total Revenue (£)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(_fmt_gbp))
    plt.xticks(rotation=40, ha="right", fontsize=10)
    plt.tight_layout()
    return _save(fig, "02_international_markets")


def plot_top_products(df: pd.DataFrame) -> Path:
    top = df.groupby("Description")["TotalRevenue"].sum().sort_values(ascending=False).head(10)

    fig, ax = plt.subplots(figsize=(11, 5))
    top.plot(kind="barh", ax=ax, color="teal", edgecolor="white")

    # Label each bar
    for bar in ax.patches:
        ax.text(
            bar.get_width() + top.max() * 0.01,
            bar.get_y() + bar.get_height() / 2,
            _fmt_gbp(bar.get_width()),
            va="center", fontsize=9, fontweight="bold"
        )

    ax.set_title("Top 10 Products by Revenue", fontweight="bold")
    ax.set_xlabel("Total Revenue (£)")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(_fmt_gbp))
    ax.invert_yaxis()
    plt.tight_layout()
    return _save(fig, "03_top_products")


def plot_day_of_week(df: pd.DataFrame) -> Path:
    dow = df.groupby("DayName")["TotalRevenue"].sum().reindex(DAY_ORDER)
    peak_day = dow.idxmax()

    fig, ax = plt.subplots(figsize=(8, 4))
    colors = ["darkorange" if d == peak_day else "mediumpurple" for d in DAY_ORDER]
    dow.plot(kind="bar", ax=ax, color=colors, edgecolor="white")

    ax.annotate(
        f"Peak day",
        xy=(DAY_ORDER.index(peak_day), dow[peak_day]),
        xytext=(DAY_ORDER.index(peak_day) + 0.8, dow[peak_day] * 1.03),
        fontsize=10, color="darkorange", fontweight="bold",
        arrowprops=dict(arrowstyle="->", color="darkorange", lw=1.2),
    )

    ax.set_title("Total Revenue by Day of Week", fontweight="bold")
    ax.set_xlabel("Day of Week")
    ax.set_ylabel("Total Revenue (£)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(_fmt_gbp))
    plt.xticks(rotation=30, ha="right", fontsize=10)
    plt.tight_layout()
    return _save(fig, "04_day_of_week")


def plot_hour_of_day(df: pd.DataFrame) -> Path:
    hourly = df.groupby("Hour")["TotalRevenue"].sum()
    peak_hour = hourly.idxmax()

    fig, ax = plt.subplots(figsize=(10, 4))
    hourly.plot(kind="line", ax=ax, marker="o", color="darkorange", linewidth=2)

    # Shade peak window 10am–3pm
    ax.axvspan(10, 15, alpha=0.12, color="green", label="Peak window (10am–3pm)")

    ax.annotate(
        f"Peak: {_fmt_gbp(hourly[peak_hour])}",
        xy=(peak_hour, hourly[peak_hour]),
        xytext=(peak_hour + 1, hourly[peak_hour] * 1.05),
        fontsize=10, color="darkgreen", fontweight="bold",
        arrowprops=dict(arrowstyle="->", color="darkgreen", lw=1.2),
    )

    ax.set_title("Revenue by Hour of Day (24h)", fontweight="bold")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Total Revenue (£)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(_fmt_gbp))
    ax.set_xticks(range(0, 24))
    ax.legend(fontsize=10)
    plt.tight_layout()
    return _save(fig, "05_hour_of_day")


def plot_purchase_frequency(df: pd.DataFrame) -> Path:
    freq = df.groupby("CustomerID")["InvoiceNo"].nunique()
    capped = freq[freq <= 20]
    pct_low = (freq <= 5).sum() / len(freq) * 100

    fig, ax = plt.subplots(figsize=(9, 4))
    capped.hist(bins=20, ax=ax, color="steelblue", edgecolor="white")

    ax.annotate(
        f"{pct_low:.0f}% of customers\nplaced ≤ 5 orders",
        xy=(5, ax.get_ylim()[1] * 0.6),
        xytext=(9, ax.get_ylim()[1] * 0.7),
        fontsize=10, color="steelblue", fontweight="bold",
        arrowprops=dict(arrowstyle="->", color="steelblue", lw=1.2),
    )

    ax.set_title("Customer Purchase Frequency (≤ 20 orders shown)", fontweight="bold")
    ax.set_xlabel("Number of Orders per Customer")
    ax.set_ylabel("Number of Customers")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    plt.tight_layout()
    return _save(fig, "06_purchase_frequency")


def plot_all(df: pd.DataFrame) -> None:
    print("Generating EDA charts...")
    plot_monthly_revenue(df)
    plot_international_markets(df)
    plot_top_products(df)
    plot_day_of_week(df)
    plot_hour_of_day(df)
    plot_purchase_frequency(df)
    print("EDA complete.")


if __name__ == "__main__":
    from clean import load_and_clean
    plot_all(load_and_clean())
