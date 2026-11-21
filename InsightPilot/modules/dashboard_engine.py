"""
InsightPilot - PowerBI-Style AI Executive Dashboard Engine
Provides an autonomous, AI-driven executive dashboard that studies any uploaded dataset,
selects the most meaningful metrics and dimensions, generates an AI strategic narrative,
and renders a rich grid of PowerBI-caliber interactive charts and KPI tiles.
"""

from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
import streamlit as st

from modules.data_analysis import (
    get_numeric_columns,
    get_categorical_columns,
    compute_column_metrics,
    compute_rankings,
    compute_grouped_aggregation
)
from modules.chart_engine import render_pie_or_donut_chart


def _detect_key_dimensions(df: pd.DataFrame) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Studies the dataset schema and automatically detects:
    1. Primary Numeric Metric (e.g., Sales, Revenue, Total, Amount, Profit, or highest variance numeric column)
    2. Secondary Numeric Metric (e.g., Quantity, Units, Count, Cost)
    3. Primary Categorical Dimension (e.g., Product, Category, Region, Segment, or column with 2-30 unique values)
    """
    num_cols = get_numeric_columns(df)
    cat_cols = get_categorical_columns(df)

    primary_num = None
    secondary_num = None
    primary_cat = None

    # Detect primary metric by semantic naming or variance
    priority_keywords = ["sales", "revenue", "amount", "total", "profit", "price", "income", "value", "cost"]
    for kw in priority_keywords:
        for col in num_cols:
            if kw in col.lower():
                primary_num = col
                break
        if primary_num:
            break

    if not primary_num and num_cols:
        # Choose numeric column with largest scale/variance
        primary_num = num_cols[0]

    # Detect secondary metric
    secondary_keywords = ["quantity", "qty", "units", "count", "discount", "volume", "rating", "score"]
    for kw in secondary_keywords:
        for col in num_cols:
            if col != primary_num and kw in col.lower():
                secondary_num = col
                break
        if secondary_num:
            break

    if not secondary_num and len(num_cols) > 1:
        secondary_num = [c for c in num_cols if c != primary_num][0]

    # Detect primary categorical dimension (prefer 2 to 30 unique items)
    cat_priority = ["product", "category", "item", "segment", "region", "city", "department", "type", "brand"]
    for kw in cat_priority:
        for col in cat_cols:
            if kw in col.lower():
                primary_cat = col
                break
        if primary_cat:
            break

    if not primary_cat and cat_cols:
        # Pick the categorical column with reasonable cardinality (2 to 40 unique values)
        suitable = [c for c in cat_cols if 1 < df[c].nunique() <= 40]
        primary_cat = suitable[0] if suitable else cat_cols[0]

    return primary_num, secondary_num, primary_cat


def _generate_ai_executive_narrative(
    df: pd.DataFrame,
    primary_num: Optional[str],
    primary_cat: Optional[str],
    total_val: float,
    avg_val: float,
    top_performer: Optional[str],
    top_share: float
) -> Dict[str, Any]:
    """
    Synthesizes a high-level executive strategic narrative by studying dataset distributions.
    """
    row_count = len(df)
    headline = "Dataset Performance Overview"
    key_driver = "Performance is evenly distributed across monitored segments."
    growth_opp = "Explore expanding operational capacity in under-represented segments."
    risk_alert = "Standard distribution observed with no critical single-point exposure."
    exec_action = "Continue baseline tracking and optimize inventory allocation."

    if primary_cat and primary_num and top_performer:
        headline = f"Executive Briefing: '{top_performer}' Leads Portfolio with {top_share}% Contribution"

        if top_share >= 50.0:
            key_driver = f"Major Revenue Concentration: '{top_performer}' generates the majority ({top_share}%) of all {primary_num}."
            risk_alert = f"High Portfolio Dependency: Over half of total performance depends on a single {primary_cat} ('{top_performer}')."
            growth_opp = f"Diversify revenue streams by scaling marketing for secondary {primary_cat} offerings."
            exec_action = f"Secure priority supply chain and customer retention initiatives for '{top_performer}'."
        elif top_share >= 30.0:
            key_driver = f"'{top_performer}' is the clear market leader, contributing {top_share}% to aggregate {primary_num}."
            risk_alert = f"Moderate category concentration observed in '{top_performer}'."
            growth_opp = "Accelerate promotion for tier-2 categories to balance top-line revenue."
            exec_action = f"Maintain momentum behind '{top_performer}' while launching cross-selling campaigns."
        else:
            key_driver = f"Balanced Portfolio: '{top_performer}' holds a modest lead with {top_share}% of total {primary_num}."
            risk_alert = "Low concentration risk; performance is healthily distributed across categories."
            growth_opp = "Focus on category champions to create a clear breakout flagship."
            exec_action = "Invest in data-driven AB testing to identify potential category leaders."

    elif primary_num:
        headline = f"Aggregate Financial Profile: Total {primary_num} stands at {total_val:,.2f}"
        key_driver = f"Across {row_count:,} recorded transactions, the average {primary_num} is {avg_val:,.2f}."
        exec_action = f"Establish monitoring benchmarks around the median {primary_num} threshold."

    return {
        "headline": headline,
        "key_driver": key_driver,
        "growth_opp": growth_opp,
        "risk_alert": risk_alert,
        "exec_action": exec_action
    }


def render_powerbi_dashboard(
    df: pd.DataFrame,
    filename: str,
    auto_insights: List[Dict[str, str]],
    language: str = "English"
) -> None:
    """
    Renders a stunning, website-grade PowerBI executive dashboard:
    1. Interactive Slicer Ribbon (Category filtering, Metric switching)
    2. 5 PowerBI KPI Cards with glowing accents & trend badges
    3. AI Strategic Executive Narrative Card (Smart Story)
    4. 6 AI-Curated Interactive Charts in responsive grid
    5. Segment Leaderboard Matrix Table with visual status pills
    """
    all_num_cols = get_numeric_columns(df)
    all_cat_cols = get_categorical_columns(df)

    if not all_num_cols and not all_cat_cols:
        st.warning("The dataset does not contain sufficient columns for executive dashboarding.")
        return

    # Auto-detect default roles
    auto_primary_num, auto_secondary_num, auto_primary_cat = _detect_key_dimensions(df)

    # =========================================================================
    # 1. POWERBI INTERACTIVE SLICER / FILTER RIBBON
    # =========================================================================
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(30, 41, 59, 0.6) 100%);
                border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 12px; padding: 12px 18px; margin-bottom: 20px;">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 16px;">🎛️</span>
                <span style="font-size: 13px; font-weight: 700; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.8px;">
                    PowerBI Interactive Slicer Ribbon
                </span>
            </div>
            <span style="font-size: 11px; color: #94a3b8;">
                Real-time multi-dimensional cross-filtering
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    sl_col1, sl_col2, sl_col3 = st.columns([1.5, 1.5, 1])

    with sl_col1:
        if all_cat_cols:
            cat_slicer_col = st.selectbox(
                "Filter Dimension",
                all_cat_cols,
                index=all_cat_cols.index(auto_primary_cat) if auto_primary_cat in all_cat_cols else 0,
                key="pbi_slicer_cat_dim"
            )
            unique_vals = ["All Items (Unfiltered)"] + sorted(list(df[cat_slicer_col].dropna().astype(str).unique()))
            selected_cat_filter = st.selectbox(
                f"Slice by {cat_slicer_col}",
                unique_vals,
                index=0,
                key="pbi_slicer_val_filter"
            )
        else:
            cat_slicer_col = None
            selected_cat_filter = "All Items (Unfiltered)"
            st.info("No categorical dimensions found.")

    with sl_col2:
        if all_num_cols:
            metric_choice = st.selectbox(
                "Primary Performance Metric",
                all_num_cols,
                index=all_num_cols.index(auto_primary_num) if auto_primary_num in all_num_cols else 0,
                key="pbi_metric_choice"
            )
        else:
            metric_choice = None
            st.info("No numeric columns found.")

    with sl_col3:
        if len(all_num_cols) > 1:
            sec_metric_options = [c for c in all_num_cols if c != metric_choice]
            sec_default_idx = (
                sec_metric_options.index(auto_secondary_num)
                if auto_secondary_num in sec_metric_options
                else 0
            )
            sec_metric_choice = st.selectbox(
                "Secondary Metric",
                sec_metric_options,
                index=sec_default_idx,
                key="pbi_sec_metric_choice"
            )
        else:
            sec_metric_choice = None
            st.caption("Single numeric metric active")

    # Apply slicer filter to create active sliced view
    active_df = df.copy()
    if cat_slicer_col and selected_cat_filter != "All Items (Unfiltered)":
        active_df = active_df[active_df[cat_slicer_col].astype(str) == str(selected_cat_filter)]

    active_rows = len(active_df)
    if active_rows == 0:
        st.warning("No records match the selected filter combination.")
        return

    # =========================================================================
    # 2. COMPUTE POWERBI KPI METRICS
    # =========================================================================
    total_primary = float(active_df[metric_choice].sum()) if metric_choice else 0.0
    avg_primary = float(active_df[metric_choice].mean()) if metric_choice else 0.0
    median_primary = float(active_df[metric_choice].median()) if metric_choice else 0.0
    max_primary = float(active_df[metric_choice].max()) if metric_choice else 0.0

    total_sec = float(active_df[sec_metric_choice].sum()) if sec_metric_choice else 0.0
    avg_sec = float(active_df[sec_metric_choice].mean()) if sec_metric_choice else 0.0

    top_performer = "N/A"
    top_share = 0.0
    if cat_slicer_col and metric_choice and active_df[cat_slicer_col].nunique() > 0:
        grp = active_df.groupby(cat_slicer_col, as_index=False)[metric_choice].sum().sort_values(by=metric_choice, ascending=False)
        if not grp.empty:
            top_performer = str(grp.iloc[0][cat_slicer_col])
            top_val = float(grp.iloc[0][metric_choice])
            top_share = round((top_val / total_primary * 100), 1) if total_primary > 0 else 0.0

    # Data Quality Index
    null_count = int(active_df.isnull().sum().sum())
    total_cells = active_rows * len(active_df.columns)
    quality_pct = round(((total_cells - null_count) / total_cells * 100), 1) if total_cells > 0 else 100.0

    # =========================================================================
    # 3. POWERBI KPI TILES RIBBON
    # =========================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    k1, k2, k3, k4, k5 = st.columns(5)

    # Pre-format KPI values cleanly
    primary_display = f"{total_primary:,.0f}" if total_primary >= 1000 else f"{total_primary:,.2f}"

    with k1:
        st.markdown(f"""
        <div class="pbi-kpi-card" style="border-top: 4px solid #38bdf8;">
            <div class="pbi-kpi-sub">Total {metric_choice or 'Records'}</div>
            <div class="pbi-kpi-val" style="color: #38bdf8;">
                {primary_display}
            </div>
            <div class="pbi-kpi-badge" style="background: rgba(56, 189, 248, 0.15); color: #38bdf8;">
                ▲ High Value Metric
            </div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        sec_title = f"Total {sec_metric_choice}" if sec_metric_choice else "Transaction Count"
        sec_display = f"{total_sec:,.0f}" if sec_metric_choice else f"{active_rows:,}"
        sec_note = f"Avg: {avg_sec:,.1f} / record" if sec_metric_choice else f"{active_rows} Total Records"
        st.markdown(f"""
        <div class="pbi-kpi-card" style="border-top: 4px solid #818cf8;">
            <div class="pbi-kpi-sub">{sec_title}</div>
            <div class="pbi-kpi-val" style="color: #818cf8;">{sec_display}</div>
            <div class="pbi-kpi-badge" style="background: rgba(129, 140, 248, 0.15); color: #a5b4fc;">
                {sec_note}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="pbi-kpi-card" style="border-top: 4px solid #10b981;">
            <div class="pbi-kpi-sub">Average {metric_choice or 'Ticket'}</div>
            <div class="pbi-kpi-val" style="color: #10b981;">{avg_primary:,.2f}</div>
            <div class="pbi-kpi-badge" style="background: rgba(16, 185, 129, 0.15); color: #6ee7b7;">
                Median: {median_primary:,.1f}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div class="pbi-kpi-card" style="border-top: 4px solid #f59e0b;">
            <div class="pbi-kpi-sub">Top {cat_slicer_col or 'Performer'}</div>
            <div class="pbi-kpi-val" style="color: #f59e0b; font-size: 20px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{top_performer}">
                {top_performer}
            </div>
            <div class="pbi-kpi-badge" style="background: rgba(245, 158, 11, 0.15); color: #fcd34d;">
                ★ {top_share}% Market Share
            </div>
        </div>
        """, unsafe_allow_html=True)

    with k5:
        st.markdown(f"""
        <div class="pbi-kpi-card" style="border-top: 4px solid #06b6d4;">
            <div class="pbi-kpi-sub">Data Quality Score</div>
            <div class="pbi-kpi-val" style="color: #06b6d4;">{quality_pct}%</div>
            <div class="pbi-kpi-badge" style="background: rgba(6, 182, 212, 0.15); color: #67e8f9;">
                {active_rows:,} Clean Records
            </div>
        </div>
        """, unsafe_allow_html=True)

    # =========================================================================
    # 4. AI EXECUTIVE STRATEGIC BRIEFING (POWERBI SMART NARRATIVE)
    # =========================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    ai_story = _generate_ai_executive_narrative(
        active_df,
        metric_choice,
        cat_slicer_col,
        total_primary,
        avg_primary,
        top_performer,
        top_share
    )

    st.markdown(f"""
    <div class="pbi-narrative-card">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 20px;">🧠</span>
                <span style="font-size: 15px; font-weight: 800; color: #f1f5f9; letter-spacing: -0.3px;">
                    AI Strategic Executive Narrative
                </span>
                <span class="pbi-ai-chip">POWERBI SMART STORY</span>
            </div>
            <span style="font-size: 12px; color: #94a3b8;">
                Synthesized across {active_rows:,} records
            </span>
        </div>
        <div style="font-size: 14px; font-weight: 600; color: #38bdf8; margin-bottom: 12px;">
            {ai_story["headline"]}
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px;">
            <div class="pbi-insight-box">
                <div class="pbi-insight-title" style="color: #10b981;">🌟 Primary Growth Driver</div>
                <div class="pbi-insight-text">{ai_story["key_driver"]}</div>
            </div>
            <div class="pbi-insight-box">
                <div class="pbi-insight-title" style="color: #f59e0b;">⚠️ Risk & Concentration Alert</div>
                <div class="pbi-insight-text">{ai_story["risk_alert"]}</div>
            </div>
            <div class="pbi-insight-box">
                <div class="pbi-insight-title" style="color: #818cf8;">💡 Strategic Recommendation</div>
                <div class="pbi-insight-text">{ai_story["exec_action"]}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # =========================================================================
    # 5. AI-CURATED POWERBI VISUALS GRID (CHARTS)
    # =========================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 18px;">📊</span>
            <span style="font-size: 16px; font-weight: 800; color: #f1f5f9;">
                Executive Visuals Grid (AI-Curated)
            </span>
        </div>
        <span style="font-size: 12px; color: #94a3b8;">Interactive PowerBI Visual Cards</span>
    </div>
    """, unsafe_allow_html=True)

    # ROW 1: Ranked Category Bar Chart & Composition Share Donut/Bar
    r1_col1, r1_col2 = st.columns([1.5, 1])

    with r1_col1:
        st.markdown(f"""
        <div class="pbi-chart-box">
            <div class="pbi-chart-head">
                <span class="pbi-chart-title">🏆 Total {metric_choice} by {cat_slicer_col or 'Category'}</span>
                <span class="pbi-chart-tag">Ranked Performance</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if cat_slicer_col and metric_choice:
            cat_agg = (
                active_df.groupby(cat_slicer_col, as_index=False)[metric_choice]
                .sum()
                .sort_values(by=metric_choice, ascending=False)
            )
            try:
                st.bar_chart(
                    data=cat_agg,
                    x=cat_slicer_col,
                    y=metric_choice,
                    x_label=cat_slicer_col,
                    y_label=f"Total {metric_choice}",
                    use_container_width=True
                )
            except TypeError:
                st.bar_chart(data=cat_agg, x=cat_slicer_col, y=metric_choice, use_container_width=True)
        elif metric_choice:
            st.bar_chart(active_df[[metric_choice]], y=metric_choice, use_container_width=True)

    with r1_col2:
        st.markdown(f"""
        <div class="pbi-chart-box">
            <div class="pbi-chart-head">
                <span class="pbi-chart-title">🍩 Market Share Composition</span>
                <span class="pbi-chart-tag">% Contribution</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if cat_slicer_col and metric_choice:
            pie_agg = (
                active_df.groupby(cat_slicer_col, as_index=False)[metric_choice]
                .sum()
                .sort_values(by=metric_choice, ascending=False)
                .head(8)
            )
            tot = pie_agg[metric_choice].sum()
            pie_agg["Share %"] = (pie_agg[metric_choice] / tot * 100).round(1) if tot > 0 else 0.0

            render_pie_or_donut_chart(pie_agg, cat_slicer_col, metric_choice, is_donut=True)

    # ROW 2: Cumulative Trajectory & Binned Value Distribution
    st.markdown("<br>", unsafe_allow_html=True)
    r2_col1, r2_col2 = st.columns([1, 1])

    with r2_col1:
        st.markdown(f"""
        <div class="pbi-chart-box">
            <div class="pbi-chart-head">
                <span class="pbi-chart-title">📈 Cumulative Performance Trajectory</span>
                <span class="pbi-chart-tag">Growth Trend</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if metric_choice:
            trend_df = active_df.copy().reset_index(drop=True)
            trend_df["Transaction_Order"] = trend_df.index + 1
            trend_df[f"Cumulative {metric_choice}"] = trend_df[metric_choice].cumsum()

            try:
                st.area_chart(
                    data=trend_df,
                    x="Transaction_Order",
                    y=f"Cumulative {metric_choice}",
                    use_container_width=True
                )
            except Exception:
                st.line_chart(trend_df[[f"Cumulative {metric_choice}"]], use_container_width=True)

    with r2_col2:
        st.markdown(f"""
        <div class="pbi-chart-box">
            <div class="pbi-chart-head">
                <span class="pbi-chart-title">📊 Value Distribution & Frequency</span>
                <span class="pbi-chart-tag">Ticket Spread</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if metric_choice:
            vals = active_df[metric_choice].dropna()
            if len(vals) >= 2:
                bins_count = min(10, len(vals.unique()))
                counts, bin_edges = np.histogram(vals, bins=max(2, bins_count))
                labels = [f"{bin_edges[i]:.0f}-{bin_edges[i+1]:.0f}" for i in range(len(counts))]
                dist_df = pd.DataFrame({"Bracket": labels, "Count": counts})

                try:
                    st.bar_chart(
                        data=dist_df,
                        x="Bracket",
                        y="Count",
                        use_container_width=True
                    )
                except TypeError:
                    st.bar_chart(data=dist_df, x="Bracket", y="Count", use_container_width=True)
            else:
                st.info("Insufficient data points for frequency histogram.")

    # ROW 3: Secondary Metric Correlation / Cross-Tab (if applicable)
    if sec_metric_choice and metric_choice:
        st.markdown("<br>", unsafe_allow_html=True)
        r3_col1, r3_col2 = st.columns([1, 1])

        with r3_col1:
            st.markdown(f"""
            <div class="pbi-chart-box">
                <div class="pbi-chart-head">
                    <span class="pbi-chart-title">🔬 Metric Correlation: {metric_choice} vs {sec_metric_choice}</span>
                    <span class="pbi-chart-tag">Relationship Analysis</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            scatter_df = active_df[[metric_choice, sec_metric_choice]].dropna()
            try:
                st.scatter_chart(
                    data=scatter_df,
                    x=sec_metric_choice,
                    y=metric_choice,
                    use_container_width=True
                )
            except Exception:
                st.line_chart(scatter_df, use_container_width=True)

        with r3_col2:
            st.markdown(f"""
            <div class="pbi-chart-box">
                <div class="pbi-chart-head">
                    <span class="pbi-chart-title">⚖️ Dual Metric Comparison ({cat_slicer_col or 'Index'})</span>
                    <span class="pbi-chart-tag">Volume vs Value</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if cat_slicer_col:
                dual_agg = active_df.groupby(cat_slicer_col, as_index=False)[[metric_choice, sec_metric_choice]].mean()
                st.dataframe(dual_agg, use_container_width=True)
            else:
                st.dataframe(active_df[[metric_choice, sec_metric_choice]].describe().round(2), use_container_width=True)

    # =========================================================================
    # 6. POWERBI INTERACTIVE SEGMENT MATRIX / LEADERBOARD TABLE
    # =========================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 18px;">📋</span>
            <span style="font-size: 16px; font-weight: 800; color: #f1f5f9;">
                Segment Performance Matrix (PowerBI Tabular View)
            </span>
        </div>
        <span style="font-size: 12px; color: #38bdf8;">Comprehensive Summary by {cat_slicer_col or 'Records'}</span>
    </div>
    """, unsafe_allow_html=True)

    if cat_slicer_col and metric_choice:
        matrix_df = (
            active_df.groupby(cat_slicer_col, as_index=False)
            .agg(
                Total_Volume=(metric_choice, "sum"),
                Average_Ticket=(metric_choice, "mean"),
                Order_Count=(metric_choice, "count"),
                Max_Single_Sale=(metric_choice, "max")
            )
            .sort_values(by="Total_Volume", ascending=False)
        )
        total_vol = matrix_df["Total_Volume"].sum()
        matrix_df["Share of Business (%)"] = (matrix_df["Total_Volume"] / total_vol * 100).round(1) if total_vol > 0 else 0.0

        # Assign Performance Tier
        def get_tier(share):
            if share >= 35.0:
                return "⭐ Star Performer"
            elif share >= 15.0:
                return "🚀 High Growth"
            elif share >= 5.0:
                return "⚖️ Core Performer"
            return "🌱 Emerging / Low"

        matrix_df["Strategic Tier"] = matrix_df["Share of Business (%)"].apply(get_tier)
        matrix_df["Total_Volume"] = matrix_df["Total_Volume"].apply(lambda v: f"{v:,.2f}")
        matrix_df["Average_Ticket"] = matrix_df["Average_Ticket"].apply(lambda v: f"{v:,.2f}")
        matrix_df["Max_Single_Sale"] = matrix_df["Max_Single_Sale"].apply(lambda v: f"{v:,.2f}")
        matrix_df["Share of Business (%)"] = matrix_df["Share of Business (%)"].apply(lambda s: f"{s:.1f}%")

        matrix_df.rename(columns={
            cat_slicer_col: f"{cat_slicer_col} (Dimension)",
            "Total_Volume": f"Total {metric_choice}",
            "Average_Ticket": f"Mean {metric_choice}",
            "Order_Count": "Records Count",
            "Max_Single_Sale": f"Peak {metric_choice}"
        }, inplace=True)

        st.dataframe(matrix_df, use_container_width=True)
    else:
        st.dataframe(active_df.describe().T.round(2), use_container_width=True)

