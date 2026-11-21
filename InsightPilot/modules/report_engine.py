"""
InsightPilot - Automatic Insights & Report Engine
Generates verified Python-computed business insights (performance, distributions,
correlations, data quality, and outliers) and produces downloadable HTML and CSV executive reports.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd
import numpy as np

from modules.data_analysis import (
    get_numeric_columns,
    get_categorical_columns,
    compute_rankings,
    compute_correlations
)


def generate_automatic_insights(df: pd.DataFrame) -> List[Dict[str, str]]:
    """
    Computes verified statistical insights across 5 dimensions:
    1. Data Quality & Completeness
    2. Category Performance (Top & Bottom)
    3. Metric Distribution & Scale
    4. Correlation Signals
    5. Potential Outliers / Anomalies
    """
    insights = []
    num_cols = get_numeric_columns(df)
    cat_cols = get_categorical_columns(df)
    row_count = len(df)

    # 1. DATA QUALITY INSIGHT
    total_missing = int(df.isnull().sum().sum())
    dup_rows = int(df.duplicated().sum())
    missing_pct = round((total_missing / (row_count * len(df.columns))) * 100, 2) if row_count > 0 else 0.0

    if total_missing == 0 and dup_rows == 0:
        insights.append({
            "type": "Data Quality",
            "icon": "✅",
            "fact": f"High data integrity: 0 missing values and 0 duplicate rows across {row_count:,} records.",
            "interpretation": "The dataset is clean and ready for statistical modeling and visualization without imputation.",
            "recommendation": "Maintain this upstream data ingestion quality."
        })
    else:
        insights.append({
            "type": "Data Quality",
            "icon": "⚠️",
            "fact": f"Detected {total_missing:,} missing cells ({missing_pct}% of total cells) and {dup_rows:,} duplicate rows.",
            "interpretation": "Missing data or duplicate records may introduce bias into aggregate statistics.",
            "recommendation": "Use the Data Cleaning tab to impute null values or deduplicate records before finalizing decisions."
        })

    # 2. CATEGORY PERFORMANCE (Top & Bottom performers)
    if cat_cols and num_cols:
        primary_cat = cat_cols[0]
        primary_num = num_cols[0]

        try:
            top_rank = compute_rankings(df, primary_cat, primary_num, top_n=1, ascending=False)
            bot_rank = compute_rankings(df, primary_cat, primary_num, top_n=1, ascending=True)

            top_item = top_rank["best_performer"]
            top_val = top_rank["best_value"]
            top_share = top_rank["share_percentage"]

            bot_item = bot_rank["best_performer"]
            bot_val = bot_rank["best_value"]

            insights.append({
                "type": "Performance Leader",
                "icon": "🏆",
                "fact": f"'{top_item}' leads in {primary_num} with {top_val:,.2f}, contributing {top_share}% of total {primary_num}.",
                "interpretation": f"Revenue or volume is concentrated in '{top_item}'.",
                "recommendation": f"Prioritize inventory and operational support for '{top_item}' to maintain top-line performance."
            })

            if top_item != bot_item:
                insights.append({
                    "type": "Growth Opportunity",
                    "icon": "📉",
                    "fact": f"'{bot_item}' recorded the lowest {primary_num} at {bot_val:,.2f}.",
                    "interpretation": f"This category is currently lagging in overall performance.",
                    "recommendation": f"Review pricing, marketing channel, or demand trends for '{bot_item}' to identify revival strategies."
                })
        except Exception:
            pass

    # 3. METRIC DISTRIBUTION
    if num_cols:
        col = num_cols[0]
        mean_val = float(df[col].mean())
        median_val = float(df[col].median())
        skew_note = "symmetrically distributed"
        if mean_val > median_val * 1.15:
            skew_note = "right-skewed (driven higher by high-value transactions)"
        elif mean_val < median_val * 0.85:
            skew_note = "left-skewed (concentrated at lower values)"

        insights.append({
            "type": "Distribution Profile",
            "icon": "📊",
            "fact": f"Average {col} is {mean_val:,.2f} with a median of {median_val:,.2f}.",
            "interpretation": f"The metric is {skew_note}.",
            "recommendation": "Use median for baseline benchmarks when high-value outliers are present."
        })

    # 4. CORRELATION SIGNALS
    if len(num_cols) >= 2:
        corr_matrix = compute_correlations(df)
        if corr_matrix is not None:
            cols = corr_matrix.columns
            pairs = []
            for i in range(len(cols)):
                for j in range(i + 1, len(cols)):
                    c1, c2 = cols[i], cols[j]
                    pairs.append((c1, c2, float(corr_matrix.loc[c1, c2])))
            if pairs:
                pairs.sort(key=lambda x: abs(x[2]), reverse=True)
                c1, c2, r_val = pairs[0]
                strength = "strong" if abs(r_val) >= 0.7 else ("moderate" if abs(r_val) >= 0.4 else "weak")
                direction = "positive" if r_val > 0 else "inverse"

                insights.append({
                    "type": "Correlation Signal",
                    "icon": "🔗",
                    "fact": f"Strongest relationship is between '{c1}' and '{c2}' (Pearson r = {r_val:.3f}).",
                    "interpretation": f"Shows a {strength} {direction} correlation.",
                    "recommendation": f"Monitor shifts in '{c1}' as an indicator for expected changes in '{c2}'."
                })

    # 5. OUTLIER DETECTION (IQR Method)
    if num_cols and row_count >= 5:
        col = num_cols[0]
        s = df[col].dropna()
        q1 = s.quantile(0.25)
        q3 = s.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = s[(s < lower_bound) | (s > upper_bound)]

        if len(outliers) > 0:
            insights.append({
                "type": "Anomaly Alert",
                "icon": "🚨",
                "fact": f"Found {len(outliers)} statistical outlier(s) in {col} outside the interval [{lower_bound:,.2f}, {upper_bound:,.2f}].",
                "interpretation": "These extreme values may represent high-value enterprise sales or data entry anomalies.",
                "recommendation": "Inspect outlier records individually to verify accuracy."
            })
        else:
            insights.append({
                "type": "Anomaly Check",
                "icon": "🛡️",
                "fact": f"No extreme statistical outliers detected in {col} based on standard 1.5x IQR bounds.",
                "interpretation": "Values fall within standard predictable ranges.",
                "recommendation": "Standard descriptive models can be safely applied."
            })

    return insights


def generate_html_report(
    df: pd.DataFrame,
    filename: str,
    insights: List[Dict[str, str]],
    custom_notes: str = ""
) -> str:
    """
    Generates a professional, self-contained, printable HTML executive report.
    """
    date_str = datetime.now().strftime("%B %d, %Y - %I:%M %p")
    num_cols = get_numeric_columns(df)
    stats_df = df[num_cols].describe().round(2) if num_cols else pd.DataFrame()

    # Generate insights HTML
    insights_html = ""
    for ins in insights:
        insights_html += f"""
        <div class="insight-card">
            <div class="insight-header">
                <span class="insight-icon">{ins['icon']}</span>
                <span class="insight-type">{ins['type']}</span>
            </div>
            <p><strong>Observed Fact:</strong> {ins['fact']}</p>
            <p><strong>Interpretation:</strong> {ins['interpretation']}</p>
            <p class="insight-rec"><strong>Recommendation:</strong> {ins['recommendation']}</p>
        </div>
        """

    # Generate stats table HTML
    stats_table_html = stats_df.to_html(classes="report-table", border=0) if not stats_df.empty else "<p>No numeric columns.</p>"

    # Generate preview table HTML
    preview_table_html = df.head(8).to_html(classes="report-table", border=0)

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>InsightPilot Analysis Report - {filename}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #f8fafc;
            color: #1e293b;
            margin: 0;
            padding: 40px;
        }}
        .container {{
            max-width: 960px;
            margin: 0 auto;
            background: #ffffff;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.1);
        }}
        .header {{
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .title {{
            font-size: 28px;
            font-weight: 800;
            color: #0f172a;
            margin: 0 0 8px 0;
        }}
        .subtitle {{
            font-size: 14px;
            color: #64748b;
            margin: 0;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 30px;
        }}
        .metric-box {{
            background: #f1f5f9;
            padding: 16px;
            border-radius: 8px;
            text-align: center;
        }}
        .metric-val {{
            font-size: 22px;
            font-weight: 700;
            color: #0284c7;
        }}
        .metric-lbl {{
            font-size: 12px;
            color: #64748b;
            margin-top: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        h2 {{
            font-size: 18px;
            font-weight: 700;
            color: #0f172a;
            margin-top: 32px;
            margin-bottom: 16px;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 8px;
        }}
        .insight-card {{
            background: #f8fafc;
            border-left: 4px solid #0284c7;
            padding: 16px 20px;
            border-radius: 6px;
            margin-bottom: 16px;
        }}
        .insight-header {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 8px;
        }}
        .insight-type {{
            font-weight: 700;
            font-size: 14px;
            color: #0369a1;
        }}
        .insight-card p {{
            margin: 6px 0;
            font-size: 13px;
            line-height: 1.5;
        }}
        .insight-rec {{
            color: #15803d;
        }}
        .report-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
            margin-top: 12px;
        }}
        .report-table th, .report-table td {{
            padding: 10px 12px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }}
        .report-table th {{
            background: #f1f5f9;
            font-weight: 600;
            color: #475569;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
            font-size: 11px;
            color: #94a3b8;
            text-align: center;
        }}
        @media print {{
            body {{ background: #fff; padding: 0; }}
            .container {{ box-shadow: none; padding: 20px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">📊 InsightPilot Executive Analysis Report</h1>
            <p class="subtitle">Dataset: <strong>{filename}</strong> | Generated: {date_str}</p>
        </div>

        <div class="metrics-grid">
            <div class="metric-box">
                <div class="metric-val">{len(df):,}</div>
                <div class="metric-lbl">Total Records</div>
            </div>
            <div class="metric-box">
                <div class="metric-val">{len(df.columns):,}</div>
                <div class="metric-lbl">Columns</div>
            </div>
            <div class="metric-box">
                <div class="metric-val">{int(df.isnull().sum().sum()):,}</div>
                <div class="metric-lbl">Missing Values</div>
            </div>
            <div class="metric-box">
                <div class="metric-val">{int(df.duplicated().sum()):,}</div>
                <div class="metric-lbl">Duplicate Rows</div>
            </div>
        </div>

        <h2>🧠 Automated Business Insights</h2>
        {insights_html}

        <h2>📈 Numeric Statistics Breakdown</h2>
        {stats_table_html}

        <h2>📋 Dataset Preview (First 8 Rows)</h2>
        {preview_table_html}

        <div class="footer">
            Generated locally by InsightPilot AI Data Analyst. No cloud API or external service was utilized.
        </div>
    </div>
</body>
</html>
"""
    return html_content


def generate_insights_csv(insights: List[Dict[str, str]]) -> str:
    """Exports insights list as CSV string."""
    insights_df = pd.DataFrame(insights)
    return insights_df.to_csv(index=False)

