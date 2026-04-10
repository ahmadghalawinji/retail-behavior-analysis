# retail-behavior-analysis

End-to-end consumer behaviour analysis pipeline for online retail transaction data — cleaning, EDA, RFM segmentation, and anomaly detection.

**Requirements:** Python 3.10+

---

## Dataset

| Attribute | Detail |
|-----------|--------|
| Source | [Kaggle — Online Retail](https://www.kaggle.com/datasets/vijayuv/onlineretail) |
| Period | December 2010 – December 2011 |
| Raw rows | ~541,909 transactions |
| Columns | InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country |
| Unique customers | ~4,373 (after cleaning) |
| Countries | 38 |
| Unique SKUs | ~3,900 |
| Missing CustomerID | ~25% of raw rows — dropped |
| Cancellations | ~2% of invoices (prefix "C") — excluded |
| Usable rows after cleaning | ~397,000 |

---

## EDA Highlights

| Chart | Key finding |
|-------|-------------|
| Monthly revenue trend | Grew from ~£500K (Jan 2011) to ~£1.1M peak in Nov 2011; December drop is data truncation, not a real decline |
| International markets | UK = ~82% of revenue; top international: Netherlands, Ireland, Germany, France, Australia |
| Top products | Seasonal gift and storage items dominate; no single SKU exceeds ~1.8% of total revenue |
| Day of week | Thursday is peak revenue day; weekends significantly lower — consistent with wholesale buying patterns |
| Hour of day | Peak activity 10am–3pm; sharp drop after 5pm |
| Purchase frequency | ~65% of customers placed 1–5 orders; a small high-frequency tail forms the Champions segment |

---

## Key Findings

- **Revenue concentration**: Champions segment drives ~70% of total revenue despite being ~22% of customers
- **Seasonal spike**: November peaked at 2,657 orders — the highest month in the dataset; December collapsed −55% vs. the 3-month rolling average
- **High-value outliers**: 425 customers exceed the IQR upper fence (£4K) and account for a disproportionate share of total revenue

---

## Project Structure

```
retail-behavior-analysis/
├── analysis/
│   ├── clean.py            # Load and clean raw data
│   ├── explore.py          # EDA charts
│   ├── segment.py          # RFM segmentation
│   ├── anomaly.py          # Anomaly detection
│   └── run.py              # Entry point — runs everything
├── data/                   # Place online_retail.csv here (git-ignored)
├── outputs/
│   └── charts/             # Generated charts (auto-created on first run)
├── requirements.txt
├── assessment_answers.md   # Detailed methodology and analysis rationale
├── report.md               # Full analysis report with charts and insights
└── README.md
```

---

## Setup

### 1 — Get the dataset

Download from [Kaggle — Online Retail](https://www.kaggle.com/datasets/vijayuv/onlineretail) and place the file at `data/online_retail.csv`.

The `data/` directory is git-ignored — the file is not included in the repository.

### 2 — Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3 — Run

```bash
# Full pipeline
python analysis/run.py

# Or run individual stages
python analysis/clean.py
python analysis/explore.py
python analysis/segment.py
python analysis/anomaly.py
```

Charts are saved to `outputs/charts/`.

---

## Taking This to Production

The analysis scripts work well for exploration and reporting. Moving to a real company environment requires changes across several areas:

### Data ingestion
- Replace the static CSV with a connection to the company's data warehouse (Snowflake, BigQuery, Redshift) via `sqlalchemy` or a cloud SDK
- Add incremental loading — process only new transactions since the last run
- Validate the incoming schema automatically and alert on unexpected nulls, new countries, or currency changes

### Scheduling & orchestration
- Wrap each script as a task in an orchestration tool (Airflow, Prefect, or Dagster) on a nightly or weekly schedule
- Add dependency tracking so anomaly detection only runs after segmentation completes successfully

### Configuration management
- Move hardcoded constants (thresholds, window sizes) into environment variables so they can be changed per environment (dev / staging / prod) without touching code

### Testing & validation
- Add unit tests for cleaning rules, RFM scoring logic, and IQR calculation
- Add data quality tests: assert row counts are within expected range and segment distribution hasn't shifted drastically vs. the prior run

### Output & monitoring
- Write results (RFM table, anomaly flags) back to the data warehouse rather than saving charts to disk only
- Connect outputs to a BI tool (Tableau, Looker, Power BI) for interactive stakeholder exploration
- Alert when the Champions segment shrinks by more than a set threshold week-over-week

### Security & compliance
- Pseudonymise CustomerID before storing results if the dataset falls under GDPR
- Apply role-based access control so only authorised teams can query customer-level RFM scores

### Scalability
- For millions of daily rows, replace pandas with PySpark or DuckDB for heavy aggregations
- Containerise with Docker for consistent execution across dev, CI, and production

---

## Author

Ahmad Ghalawinji
