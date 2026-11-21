"""
InsightPilot - Automatic Chart Engine
Intelligently recommends and renders 7+ chart types:
Bar, Horizontal Bar, Line, Scatter, Histogram, Box Plot, Pie/Donut, and Heatmap.
Ensures zero-crash compatibility, correct axis labels, no index-as-category bugs,
and handles duplicate aggregation cleanly.
"""

from typing import Dict, Any, Optional, List, Tuple
import io
import pandas as pd
import numpy as np
import streamlit as st

# Safe optional import of matplotlib for download exports and advanced plots
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Safe optional import of altair for native interactive arc / pie / donut charts
try:
    import altair as alt
    ALTAIR_AVAILABLE = True
except ImportError:
    ALTAIR_AVAILABLE = False


def render_pie_or_donut_chart(
    df_data: pd.DataFrame,
    cat_col: str,
    val_col: str,
    is_donut: bool = True
) -> None:
    """
    Renders an authentic, interactive circular Pie / Donut chart.
    Uses Altair mark_arc with hover tooltips and category legend,
    falling back to Matplotlib pie with dark-mode styling.
    """
    if df_data.empty or cat_col not in df_data.columns or val_col not in df_data.columns:
        st.info("No data available for Pie / Donut chart.")
        return

    # 1. Try Altair first (interactive Vega-Lite arc chart)
    if ALTAIR_AVAILABLE:
        try:
            inner_r = 45 if is_donut else 0
            chart = alt.Chart(df_data).mark_arc(
                innerRadius=inner_r,
                outerRadius=105,
                stroke="#070a13",
                strokeWidth=2
            ).encode(
                theta=alt.Theta(field=val_col, type="quantitative", stack=True),
                color=alt.Color(
                    field=cat_col,
                    type="nominal",
                    scale=alt.Scale(scheme="tableau10"),
                    legend=alt.Legend(title=cat_col, orient="bottom", columns=3)
                ),
                tooltip=[
                    alt.Tooltip(field=cat_col, type="nominal", title="Category"),
                    alt.Tooltip(field=val_col, type="quantitative", format=",.2f", title="Value"),
                    alt.Tooltip(field="Share (%)", type="quantitative", format=".1f", title="Share (%)") if "Share (%)" in df_data.columns else alt.Tooltip(field=val_col, type="quantitative", title="Value")
                ]
            ).properties(height=300)
            st.altair_chart(chart, use_container_width=True)
            return
        except Exception:
            pass

    # 2. Matplotlib fallback
    if MATPLOTLIB_AVAILABLE:
        try:
            fig, ax = plt.subplots(figsize=(5.5, 4.2), facecolor="none")
            colors = ["#38bdf8", "#818cf8", "#10b981", "#f59e0b", "#f43f5e", "#06b6d4", "#a855f7", "#ec4899", "#14b8a6", "#eab308"]
            wedges, texts, autotexts = ax.pie(
                df_data[val_col],
                labels=df_data[cat_col],
                autopct="%1.1f%%",
                pctdistance=0.72 if is_donut else 0.6,
                startangle=140,
                colors=colors[:len(df_data)],
                wedgeprops=dict(width=0.45 if is_donut else 1.0, edgecolor="#070a13", linewidth=2),
                textprops=dict(color="#f1f5f9", fontsize=9, weight="bold")
            )
            for at in autotexts:
                at.set_color("#070a13")
                at.set_fontsize(8)
                at.set_weight("bold")
            ax.axis("equal")
            st.pyplot(fig, transparent=True)
            return
        except Exception:
            pass

    # 3. Simple Table Fallback if graphics backend unavailable
    st.dataframe(df_data[[cat_col, val_col]], use_container_width=True)


CHART_TYPES = [
    "Bar Chart",
    "Horizontal Bar Chart (Ranking)",
    "Line Chart (Trend)",
    "Scatter Plot (Relationship)",
    "Histogram (Distribution)",
    "Box Plot",
    "Pie / Donut Chart",
    "Correlation Heatmap"
]


def recommend_chart_type(df: pd.DataFrame, x_col: Optional[str], y_col: Optional[str]) -> str:
    """
    Intelligently recommends the best chart type based on column data types.
    """
    if not x_col and not y_col:
        return "Bar Chart"

    if x_col and y_col:
        x_is_num = pd.api.types.is_numeric_dtype(df[x_col])
        y_is_num = pd.api.types.is_numeric_dtype(df[y_col])

        if x_is_num and y_is_num:
            return "Scatter Plot (Relationship)"

        if not x_is_num and y_is_num:
            unique_count = df[x_col].nunique()
            if unique_count <= 5:
                return "Pie / Donut Chart"
            elif unique_count > 15:
                return "Horizontal Bar Chart (Ranking)"
            return "Bar Chart"

    if y_col and pd.api.types.is_numeric_dtype(df[y_col]):
        return "Histogram (Distribution)"

    return "Bar Chart"


def render_chart_with_controls(
    df: pd.DataFrame,
    default_x: Optional[str] = None,
    default_y: Optional[str] = None,
    default_type: Optional[str] = None
):
    """
    Renders an interactive visualization studio with chart selector,
    axis switchers, aggregation controls, and chart export.
    """
    all_cols = list(df.columns)
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category", "string"]).columns.tolist()

    if not num_cols and not cat_cols:
        st.warning("No suitable columns found for visualization.")
        return

    # 1. Controls Row
    c1, c2, c3 = st.columns([1.5, 1.2, 1.2])

    with c1:
        # Determine initial chart type
        init_rec = default_type or recommend_chart_type(df, default_x, default_y)
        init_idx = CHART_TYPES.index(init_rec) if init_rec in CHART_TYPES else 0
        selected_chart = st.selectbox("Select Chart Type", CHART_TYPES, index=init_idx, key="studio_chart_type")

    with c2:
        if selected_chart in ["Correlation Heatmap"]:
            selected_x = None
            st.caption("Auto-analyzes all numeric columns")
        else:
            x_options = ["None"] + all_cols
            x_default = default_x if default_x in all_cols else (cat_cols[0] if cat_cols else all_cols[0])
            x_idx = x_options.index(x_default) if x_default in x_options else 0
            selected_x = st.selectbox("X-Axis (Category / Dimension)", x_options, index=x_idx, key="studio_x_axis")
            if selected_x == "None":
                selected_x = None

    with c3:
        if selected_chart in ["Correlation Heatmap"]:
            selected_y = None
        else:
            y_options = ["None"] + num_cols
            y_default = default_y if default_y in num_cols else (num_cols[0] if num_cols else "None")
            y_idx = y_options.index(y_default) if y_default in y_options else 0
            selected_y = st.selectbox("Y-Axis (Numeric Metric)", y_options, index=y_idx, key="studio_y_axis")
            if selected_y == "None":
                selected_y = None

    st.markdown("---")

    # 2. Render Chosen Chart
    chart_title = f"{selected_chart}: "
    if selected_x and selected_y:
        chart_title += f"{selected_y} by {selected_x}"
    elif selected_y:
        chart_title += f"{selected_y}"
    else:
        chart_title += "Dataset Overview"

    st.subheader(f"📊 {chart_title}")

    # =========================================================
    # BAR CHART & HORIZONTAL BAR CHART
    # =========================================================
    if selected_chart in ["Bar Chart", "Horizontal Bar Chart (Ranking)"]:
        if not selected_y:
            st.warning("Please select a numeric column for the Y-Axis.")
            return

        if selected_x:
            # Aggregate duplicates with sum; do not use DataFrame index as labels
            chart_data = (
                df.groupby(selected_x, as_index=False)[selected_y]
                .sum()
                .sort_values(by=selected_y, ascending=(selected_chart == "Horizontal Bar Chart (Ranking)"))
            )

            try:
                st.bar_chart(
                    data=chart_data,
                    x=selected_x,
                    y=selected_y,
                    x_label=selected_x,
                    y_label=f"Total {selected_y}",
                    use_container_width=True
                )
            except TypeError:
                st.bar_chart(
                    data=chart_data,
                    x=selected_x,
                    y=selected_y,
                    use_container_width=True
                )
            st.caption(f"X-Axis: {selected_x} | Y-Axis: Total {selected_y}")
        else:
            st.bar_chart(df[[selected_y]], y=selected_y, use_container_width=True)

    # =========================================================
    # LINE CHART (TREND)
    # =========================================================
    elif selected_chart == "Line Chart (Trend)":
        if not selected_y:
            st.warning("Please select a numeric column for the Y-Axis.")
            return

        if selected_x:
            line_data = df.groupby(selected_x, as_index=False)[selected_y].sum()
            try:
                st.line_chart(
                    data=line_data,
                    x=selected_x,
                    y=selected_y,
                    x_label=selected_x,
                    y_label=f"Total {selected_y}",
                    use_container_width=True
                )
            except TypeError:
                st.line_chart(data=line_data, x=selected_x, y=selected_y, use_container_width=True)
        else:
            st.line_chart(df[[selected_y]], y=selected_y, use_container_width=True)

    # =========================================================
    # SCATTER PLOT (RELATIONSHIP)
    # =========================================================
    elif selected_chart == "Scatter Plot (Relationship)":
        if not selected_x or not selected_y:
            st.warning("Scatter plot requires both an X-axis and Y-axis numeric column.")
            return

        scatter_data = df[[selected_x, selected_y]].dropna()
        try:
            st.scatter_chart(
                data=scatter_data,
                x=selected_x,
                y=selected_y,
                use_container_width=True
            )
        except Exception:
            # Fallback if scatter_chart not supported
            if MATPLOTLIB_AVAILABLE:
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.scatter(scatter_data[selected_x], scatter_data[selected_y], color="#4E79A7", alpha=0.8)
                ax.set_xlabel(selected_x)
                ax.set_ylabel(selected_y)
                ax.set_title(f"{selected_y} vs {selected_x}")
                st.pyplot(fig)
            else:
                st.line_chart(scatter_data, x=selected_x, y=selected_y, use_container_width=True)

    # =========================================================
    # HISTOGRAM (DISTRIBUTION)
    # =========================================================
    elif selected_chart == "Histogram (Distribution)":
        target = selected_y or (num_cols[0] if num_cols else None)
        if not target:
            st.warning("Histogram requires a numeric column.")
            return

        clean_vals = df[target].dropna()
        # Create binned frequency distribution in pandas (zero extra dependency)
        counts, bin_edges = np.histogram(clean_vals, bins=10)
        bin_labels = [f"{bin_edges[i]:.1f}-{bin_edges[i+1]:.1f}" for i in range(len(counts))]
        hist_df = pd.DataFrame({"Range": bin_labels, "Frequency": counts})

        try:
            st.bar_chart(hist_df, x="Range", y="Frequency", x_label=f"{target} Bins", y_label="Frequency", use_container_width=True)
        except TypeError:
            st.bar_chart(hist_df, x="Range", y="Frequency", use_container_width=True)
        st.caption(f"Frequency distribution for {target} (10 intervals)")

    # =========================================================
    # BOX PLOT
    # =========================================================
    elif selected_chart == "Box Plot":
        target = selected_y or (num_cols[0] if num_cols else None)
        if not target:
            st.warning("Box plot requires a numeric column.")
            return

        stats = df[target].describe()
        b_col1, b_col2, b_col3, b_col4, b_col5 = st.columns(5)
        b_col1.metric("Min", f"{stats['min']:,.2f}")
        b_col2.metric("25% (Q1)", f"{stats['25%']:,.2f}")
        b_col3.metric("Median", f"{stats['50%']:,.2f}")
        b_col4.metric("75% (Q3)", f"{stats['75%']:,.2f}")
        b_col5.metric("Max", f"{stats['max']:,.2f}")

        if MATPLOTLIB_AVAILABLE:
            fig, ax = plt.subplots(figsize=(6, 2.5))
            ax.boxplot(df[target].dropna(), vert=False, patch_artist=True, boxprops=dict(facecolor="#59A14F", color="#59A14F"))
            ax.set_title(f"Box Plot: {target}")
            ax.set_xlabel(target)
            st.pyplot(fig)

    # =========================================================
    # PIE / DONUT CHART
    # =========================================================
    elif selected_chart == "Pie / Donut Chart":
        cat = selected_x or (cat_cols[0] if cat_cols else None)
        num = selected_y or (num_cols[0] if num_cols else None)

        if not cat or not num:
            st.warning("Pie/Donut chart requires a Category column (X) and a Numeric column (Y).")
            return

        pie_data = df.groupby(cat, as_index=False)[num].sum().sort_values(by=num, ascending=False).head(8)
        total_sum = pie_data[num].sum()
        pie_data["Share (%)"] = (pie_data[num] / total_sum * 100).round(1)

        pcol1, pcol2 = st.columns([1.4, 1])
        with pcol1:
            render_pie_or_donut_chart(pie_data, cat, num, is_donut=True)
        with pcol2:
            st.write(f"**Proportion Breakdown ({cat}):**")
            st.dataframe(pie_data[[cat, num, "Share (%)"]], use_container_width=True)

    # =========================================================
    # CORRELATION HEATMAP
    # =========================================================
    elif selected_chart == "Correlation Heatmap":
        if len(num_cols) < 2:
            st.info("Correlation Heatmap requires at least two numeric columns.")
            return

        corr_df = df[num_cols].corr().round(3)
        st.write("**Pairwise Correlation Matrix Table:**")
        st.dataframe(corr_df.style.background_gradient(cmap="coolwarm", vmin=-1.0, vmax=1.0), use_container_width=True)

