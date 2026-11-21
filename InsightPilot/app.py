import streamlit as st
import pandas as pd
import requests
from datetime import datetime

from modules.data_loader import load_dataset_file, get_dataset_summary
from modules.data_analysis import (
    get_numeric_columns,
    get_categorical_columns,
    compute_column_metrics,
    compute_category_metrics,
    compute_grouped_aggregation,
    compute_rankings,
    compute_correlations
)
from modules.data_cleaning import (
    remove_duplicates,
    drop_columns,
    rename_columns,
    handle_missing_values,
    convert_column_dtype
)
from modules.question_engine import (
    parse_question_intent,
    execute_question,
    get_suggested_questions
)
from modules.llm_engine import (
    check_ollama_status,
    explain_findings,
    VoiceAssistantHook,
    DEFAULT_MODEL
)
from modules.chart_engine import render_chart_with_controls
from modules.report_engine import (
    generate_automatic_insights,
    generate_html_report,
    generate_insights_csv
)
from modules.voice_engine import render_voice_input_widget
from modules.dashboard_engine import render_powerbi_dashboard

# ==========================================
# INSIGHTPILOT - AI DATA ANALYST
# PowerBI-Style AI Executive Dashboard & Voice Studio
# ==========================================

st.set_page_config(
    page_title="InsightPilot - AI Data Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Catch any voice query from browser speech component and auto-trigger analysis
if "voice_query" in st.query_params:
    st.session_state["submitted_question"] = st.query_params["voice_query"]
    try:
        del st.query_params["voice_query"]
    except Exception:
        pass

# Ultra-Modern Executive Glassmorphism & Website Styling
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #0d1527 0%, #060913 70%, #04060c 100%);
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
    }

    /* Website Header / Navbar */
    .web-navbar {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(8, 12, 22, 0.95) 100%);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 16px;
        padding: 18px 26px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 16px;
        box-shadow: 0 10px 35px -10px rgba(0, 0, 0, 0.6), 0 0 20px rgba(56, 189, 248, 0.08);
        backdrop-filter: blur(16px);
    }
    .nav-brand-group {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .nav-logo-badge {
        width: 44px;
        height: 44px;
        background: linear-gradient(135deg, #0284c7 0%, #6366f1 100%);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        box-shadow: 0 4px 15px rgba(2, 132, 199, 0.4);
    }
    .nav-brand-title {
        font-size: 24px;
        font-weight: 800;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .nav-edition-pill {
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.4);
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 0.8px;
    }
    .nav-brand-sub {
        font-size: 13px;
        color: #94a3b8;
        margin-top: 2px;
    }
    .nav-status-group {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
    }
    .nav-status-pill {
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .nav-status-pill.online {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.35);
    }
    .nav-status-pill.private {
        background: rgba(56, 189, 248, 0.12);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }
    .nav-status-pill.voice {
        background: rgba(129, 140, 248, 0.15);
        color: #a5b4fc;
        border: 1px solid rgba(129, 140, 248, 0.35);
    }

    /* PowerBI KPI Cards */
    .pbi-kpi-card {
        background: linear-gradient(135deg, rgba(17, 24, 39, 0.85) 0%, rgba(11, 17, 30, 0.95) 100%);
        border: 1px solid rgba(56, 189, 248, 0.2);
        padding: 18px 16px;
        border-radius: 14px;
        text-align: left;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    .pbi-kpi-card:hover {
        transform: translateY(-3px);
        border-color: rgba(56, 189, 248, 0.5);
        box-shadow: 0 14px 30px -5px rgba(2, 132, 199, 0.3);
    }
    .pbi-kpi-sub {
        font-size: 11px;
        font-weight: 700;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 6px;
    }
    .pbi-kpi-val {
        font-size: 26px;
        font-weight: 800;
        line-height: 1.1;
        letter-spacing: -0.5px;
        margin-bottom: 8px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
    }
    .pbi-kpi-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
    }

    /* PowerBI Smart Narrative Card */
    .pbi-narrative-card {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.75) 100%);
        border: 1px solid rgba(99, 102, 241, 0.35);
        border-radius: 14px;
        padding: 20px 24px;
        box-shadow: 0 10px 30px -10px rgba(99, 102, 241, 0.25);
    }
    .pbi-ai-chip {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.25) 0%, rgba(139, 92, 246, 0.25) 100%);
        color: #a5b4fc;
        border: 1px solid rgba(129, 140, 248, 0.4);
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 0.6px;
    }
    .pbi-insight-box {
        background: rgba(11, 17, 30, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 12px 14px;
    }
    .pbi-insight-title {
        font-size: 11px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 4px;
    }
    .pbi-insight-text {
        font-size: 13px;
        color: #cbd5e1;
        line-height: 1.45;
    }

    /* PowerBI Chart Containers */
    .pbi-chart-box {
        background: linear-gradient(135deg, rgba(17, 24, 39, 0.7) 0%, rgba(11, 17, 30, 0.85) 100%);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 12px 12px 0 0;
        padding: 12px 16px;
        margin-bottom: 4px;
    }
    .pbi-chart-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .pbi-chart-title {
        font-size: 13px;
        font-weight: 700;
        color: #f1f5f9;
    }
    .pbi-chart-tag {
        font-size: 10px;
        font-weight: 700;
        color: #38bdf8;
        background: rgba(56, 189, 248, 0.15);
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 2px 8px;
        border-radius: 12px;
        text-transform: uppercase;
    }

    /* Chat Bubbles */
    .chat-bubble-user {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(51, 65, 85, 0.9) 100%);
        border-left: 4px solid #38bdf8;
        padding: 14px 18px;
        border-radius: 10px;
        margin-bottom: 14px;
        color: #f8fafc;
        font-size: 14px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    .chat-bubble-ai {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.7) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 24px;
        color: #e2e8f0;
        line-height: 1.6;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    .ai-badge {
        display: inline-block;
        background: rgba(99, 102, 241, 0.2);
        color: #a5b4fc;
        border: 1px solid rgba(99, 102, 241, 0.4);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 700;
        margin-bottom: 8px;
    }

    /* Modern Website Navigation Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(11, 17, 30, 0.7);
        padding: 6px 8px;
        border-radius: 14px;
        border: 1px solid rgba(56, 189, 248, 0.2);
        margin-bottom: 18px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 10px 18px;
        font-weight: 600;
        font-size: 13px;
        color: #94a3b8;
        background: transparent;
        border: none;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #38bdf8;
        background: rgba(56, 189, 248, 0.08);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(2, 132, 199, 0.45);
        font-weight: 700;
    }

    /* Primary Buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# WEBSITE TOP NAVBAR
# ==========================================

st.markdown("""
<div class="web-navbar">
    <div class="nav-brand-group">
        <div class="nav-logo-badge">⚡</div>
        <div>
            <div class="nav-brand-title">
                InsightPilot
                <span class="nav-edition-pill">POWERBI AI EDITION</span>
            </div>
            <div class="nav-brand-sub">Autonomous AI Business Intelligence • 100% Local Apple Silicon</div>
        </div>
    </div>
    <div class="nav-status-group">
        <span class="nav-status-pill online">🟢 Local Ollama Online</span>
        <span class="nav-status-pill private">🔒 100% Private & Air-Gapped</span>
        <span class="nav-status-pill voice">🎙️ EN & ML Voice Studio</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ==========================================
# SIDEBAR CONFIGURATION
# ==========================================

with st.sidebar:
    st.header("🤖 AI & Voice Configuration")

    ollama_online, installed_models, ollama_err = check_ollama_status()

    if ollama_online:
        st.success("🟢 Ollama Local AI Online")
        if installed_models:
            default_idx = (
                installed_models.index(DEFAULT_MODEL)
                if DEFAULT_MODEL in installed_models
                else 0
            )
            selected_model = st.selectbox(
                "Active AI Model",
                installed_models,
                index=default_idx
            )
        else:
            selected_model = DEFAULT_MODEL
            st.warning(f"No models found. Run `ollama pull {DEFAULT_MODEL}`.")
    else:
        st.error("🔴 Ollama is Offline")
        st.caption(ollama_err or "Run `ollama serve` in terminal.")
        selected_model = DEFAULT_MODEL

    st.caption("No paid APIs or API keys. Runs locally on Apple Silicon.")

    st.markdown("---")
    st.subheader("🌐 Language & Voice Studio")

    response_language = st.selectbox(
        "Response Language",
        ["English", "Malayalam (മലയാളം)", "Auto"]
    )

    is_ml_mode = "malayalam" in response_language.lower()

    if is_ml_mode:
        st.info("✨ **ലളിതമായ മലയാളം സജീവമാണ്** (Simple Malayalam Mode Active)")
    else:
        st.caption("🎙️ Speech Recognition: Web Speech API enabled for EN & ML")

    st.markdown("---")
    st.info("🔒 **100% Private & Local**\nYour data never leaves your computer.")


# ==========================================
# DATASET UPLOAD
# ==========================================

uploaded_file = st.file_uploader(
    "Upload your dataset (CSV or Excel)",
    type=["csv", "xlsx"]
)

import os
demo_dataset_path = os.path.join(os.path.dirname(__file__), "sample_sales.csv")

# Support demo dataset toggle
active_file = uploaded_file
active_filename = uploaded_file.name if uploaded_file is not None else None

if active_file is None and st.session_state.get("use_demo_dataset"):
    if os.path.exists(demo_dataset_path):
        active_file = open(demo_dataset_path, "rb")
        active_filename = "sample_sales.csv"

# ==========================================
# MAIN APPLICATION WORKFLOW
# ==========================================

if active_file is not None:

    try:
        raw_df, load_error = load_dataset_file(active_file)

        if st.session_state.get("use_demo_dataset") and uploaded_file is None:
            dm_col1, dm_col2 = st.columns([5, 1])
            with dm_col1:
                st.info("💡 **Active Mode: Demo Dataset (`sample_sales.csv`)** — PowerBI AI Dashboard is active.")
            with dm_col2:
                if st.button("✕ Close Demo", use_container_width=True):
                    st.session_state["use_demo_dataset"] = False
                    st.rerun()

        if load_error:
            st.error(load_error)
        elif raw_df is None or raw_df.empty:
            st.warning("The uploaded dataset is empty.")
        else:
            # Session State initialization
            if (
                "current_filename" not in st.session_state
                or st.session_state["current_filename"] != active_filename
            ):
                st.session_state["raw_dataset"] = raw_df.copy()
                st.session_state["cleaned_dataset"] = raw_df.copy()
                st.session_state["current_filename"] = active_filename
                st.session_state["cleaning_log"] = []
                st.session_state["active_question"] = ""
                st.session_state["chat_history"] = []

            # Working dataset
            df = st.session_state["cleaned_dataset"]
            summary = get_dataset_summary(df)
            numeric_columns = summary["numeric_columns"]
            categorical_columns = summary["categorical_columns"]
            auto_insights = generate_automatic_insights(df)

            # Notification if data cleaning was applied
            if st.session_state["cleaning_log"]:
                c_msg_col, c_btn_col = st.columns([4, 1])
                with c_msg_col:
                    st.info(
                        f"✨ Active dataset has cleaning modifications: "
                        f"{' | '.join(st.session_state['cleaning_log'])}"
                    )
                with c_btn_col:
                    if st.button("🔄 Reset to Original", use_container_width=True):
                        st.session_state["cleaned_dataset"] = st.session_state["raw_dataset"].copy()
                        st.session_state["cleaning_log"] = []
                        st.rerun()

            # ==========================================
            # MAIN APPLICATION TABS
            # ==========================================
            tab_dash, tab_explorer, tab_clean, tab_viz, tab_stats, tab_chat, tab_reports = st.tabs([
                "📊 PowerBI Executive Dashboard",
                "🔍 Dataset Explorer",
                "🧹 Data Cleaning",
                "📈 Visualizations Studio",
                "🔬 Statistical Deep-Dive",
                "💬 AI Analyst & Voice Chat",
                "📑 Reports & Export"
            ])

            # ------------------------------------------
            # TAB 1: EXECUTIVE DASHBOARD (POWERBI AI EDITION)
            # ------------------------------------------
            with tab_dash:
                render_powerbi_dashboard(
                    df,
                    active_filename,
                    auto_insights,
                    language=response_language
                )

            # ------------------------------------------
            # TAB 2: DATASET EXPLORER
            # ------------------------------------------
            with tab_explorer:
                st.subheader("Dataset Structure & Previews")
                exp_t1, exp_t2, exp_t3, exp_t4 = st.tabs([
                    "First 10 Rows (Head)",
                    "Last 10 Rows (Tail)",
                    "Random Sample",
                    "Columns & Data Types"
                ])
                with exp_t1:
                    st.dataframe(summary["head"], use_container_width=True)
                with exp_t2:
                    st.dataframe(summary["tail"], use_container_width=True)
                with exp_t3:
                    st.dataframe(summary["sample"], use_container_width=True)
                with exp_t4:
                    col_info = []
                    for col in df.columns:
                        col_info.append({
                            "Column": col,
                            "Type": summary["dtypes"].get(col, "Unknown"),
                            "Missing Count": summary["missing_per_column"].get(col, {}).get("count", 0),
                            "Missing %": f"{summary['missing_per_column'].get(col, {}).get('percentage', 0.0)}%"
                        })
                    st.dataframe(pd.DataFrame(col_info), use_container_width=True)

            # ------------------------------------------
            # TAB 3: DATA CLEANING
            # ------------------------------------------
            with tab_clean:
                st.subheader("Non-Destructive Data Cleaning Studio")
                cl_t1, cl_t2, cl_t3, cl_t4 = st.tabs([
                    "Handle Missing Values",
                    "Remove Duplicates",
                    "Drop / Rename Columns",
                    "Convert Data Types"
                ])

                with cl_t1:
                    st.write("##### Impute or Drop Missing Values")
                    if summary["total_missing"] == 0:
                        st.success("This dataset has zero missing values.")
                    else:
                        st.write("Missing values summary:", summary["missing_per_column"])

                    c_strat, c_col = st.columns(2)
                    with c_strat:
                        strategy_choice = st.selectbox(
                            "Cleaning Strategy",
                            [
                                "Remove rows with missing values",
                                "Fill numeric missing values with Mean",
                                "Fill numeric missing values with Median",
                                "Fill categorical missing values with Mode",
                                "Fill missing values with Custom Value"
                            ]
                        )
                    with c_col:
                        target_col_choice = st.selectbox(
                            "Target Column",
                            ["All Applicable Columns"] + list(df.columns)
                        )

                    custom_val = None
                    if "Custom Value" in strategy_choice:
                        custom_val = st.text_input("Enter replacement value", value="0")

                    if st.button("✨ Apply Missing Value Fix", key="clean_missing_btn"):
                        strat_map = {
                            "Remove rows with missing values": "drop_rows",
                            "Fill numeric missing values with Mean": "fill_mean",
                            "Fill numeric missing values with Median": "fill_median",
                            "Fill categorical missing values with Mode": "fill_mode",
                            "Fill missing values with Custom Value": "fill_custom"
                        }
                        chosen_strat = strat_map[strategy_choice]
                        chosen_c = None if target_col_choice == "All Applicable Columns" else target_col_choice

                        new_df, affected = handle_missing_values(df, strategy=chosen_strat, column=chosen_c, custom_value=custom_val)
                        st.session_state["cleaned_dataset"] = new_df
                        st.session_state["cleaning_log"].append(f"{strategy_choice} ({affected} affected)")
                        st.success(f"Applied fix to {affected} records.")
                        st.rerun()

                with cl_t2:
                    st.write("##### Deduplicate Records")
                    st.write(f"Current duplicate rows count: **{summary['duplicate_rows']}**")
                    if summary["duplicate_rows"] > 0:
                        if st.button("🗑️ Remove Duplicate Rows", key="clean_dup_btn"):
                            new_df, rem_cnt = remove_duplicates(df)
                            st.session_state["cleaned_dataset"] = new_df
                            st.session_state["cleaning_log"].append(f"Removed {rem_cnt} duplicates")
                            st.success(f"Removed {rem_cnt} duplicate rows.")
                            st.rerun()
                    else:
                        st.success("Zero duplicate rows detected.")

                with cl_t3:
                    st.write("##### Drop or Rename Columns")
                    cols_drop = st.multiselect("Select columns to drop", list(df.columns))
                    if st.button("🗑️ Drop Selected Columns", key="clean_drop_btn"):
                        if cols_drop:
                            st.session_state["cleaned_dataset"] = drop_columns(df, cols_drop)
                            st.session_state["cleaning_log"].append(f"Dropped {', '.join(cols_drop)}")
                            st.rerun()

                    st.markdown("---")
                    r_c1, r_c2 = st.columns(2)
                    with r_c1:
                        c_ren = st.selectbox("Column to rename", list(df.columns), key="clean_ren_sel")
                    with r_c2:
                        n_ren = st.text_input("New name", value=c_ren)
                    if st.button("✏️ Rename Column", key="clean_ren_btn"):
                        if n_ren.strip() and n_ren.strip() != c_ren:
                            st.session_state["cleaned_dataset"] = rename_columns(df, {c_ren: n_ren.strip()})
                            st.session_state["cleaning_log"].append(f"Renamed '{c_ren}' -> '{n_ren.strip()}'")
                            st.rerun()

                with cl_t4:
                    st.write("##### Cast Data Types")
                    tc1, tc2 = st.columns(2)
                    with tc1:
                        type_col = st.selectbox("Select Column", list(df.columns), key="clean_type_col")
                    with tc2:
                        target_t = st.selectbox("New Data Type", ["numeric", "string", "datetime", "boolean"])
                    if st.button("🔄 Convert Type", key="clean_cast_btn"):
                        new_df, err = convert_column_dtype(df, type_col, target_t)
                        if err:
                            st.error(err)
                        else:
                            st.session_state["cleaned_dataset"] = new_df
                            st.session_state["cleaning_log"].append(f"Cast '{type_col}' to {target_t}")
                            st.rerun()

            # ------------------------------------------
            # TAB 4: VISUALIZATIONS STUDIO
            # ------------------------------------------
            with tab_viz:
                default_cat = "Product" if "Product" in categorical_columns else (categorical_columns[0] if categorical_columns else None)
                default_num = "Sales" if "Sales" in numeric_columns else (numeric_columns[0] if numeric_columns else None)
                render_chart_with_controls(df, default_x=default_cat, default_y=default_num)

            # ------------------------------------------
            # TAB 5: STATISTICAL DEEP-DIVE
            # ------------------------------------------
            with tab_stats:
                st.subheader("Advanced Statistical Profiling")
                s_t1, s_t2, s_t3 = st.tabs(["Numeric Profiles", "Group-By Aggregator", "Correlation Matrix"])

                with s_t1:
                    if numeric_columns:
                        selected_stat_col = st.selectbox("Select numeric column", numeric_columns, key="stat_tab_sel")
                        col_stats = compute_column_metrics(df, selected_stat_col)

                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("Sum / Total", f"{col_stats['sum']:,.2f}")
                        m2.metric("Mean / Average", f"{col_stats['mean']:,.2f}")
                        m3.metric("Median (50%)", f"{col_stats['median']:,.2f}")
                        m4.metric("Std Deviation", f"{col_stats['std']:,.2f}")

                        m5, m6, m7, m8 = st.columns(4)
                        m5.metric("Minimum", f"{col_stats['min']:,.2f}")
                        m6.metric("25th Percentile", f"{col_stats['q25']:,.2f}")
                        m7.metric("75th Percentile", f"{col_stats['q75']:,.2f}")
                        m8.metric("Maximum", f"{col_stats['max']:,.2f}")
                    else:
                        st.info("No numeric columns available.")

                with s_t2:
                    if categorical_columns and numeric_columns:
                        gc1, gc2, gc3 = st.columns(3)
                        with gc1:
                            grp_c = st.selectbox("Group By", categorical_columns, key="tab_gc1")
                        with gc2:
                            grp_n = st.selectbox("Numeric Column", numeric_columns, key="tab_gc2")
                        with gc3:
                            grp_f = st.selectbox("Aggregation", ["Sum", "Average", "Count", "Min", "Max"], key="tab_gc3")
                        st.dataframe(compute_grouped_aggregation(df, grp_c, grp_n, agg_func=grp_f), use_container_width=True)
                    else:
                        st.info("Requires at least one category and one numeric column.")

                with s_t3:
                    if len(numeric_columns) >= 2:
                        st.dataframe(compute_correlations(df), use_container_width=True)
                    else:
                        st.info("Requires at least two numeric columns.")

            # ------------------------------------------
            # TAB 6: AI ANALYST & VOICE CHAT
            # ------------------------------------------
            with tab_chat:
                st.subheader("🎙️ Voice & Natural Language AI Analyst")

                # Prominent Voice Command Assistant Widget
                render_voice_input_widget(language=response_language)

                # Optional native audio recorder if supported by Streamlit
                if hasattr(st, "audio_input"):
                    with st.expander("🎧 Native Audio Recording Device", expanded=False):
                        rec_audio = st.audio_input("Record audio command")
                        if rec_audio:
                            st.info("Audio recorded successfully! Transcribe via Web Speech above for immediate text queries.")

                st.markdown("<br>", unsafe_allow_html=True)

                # Suggested Question Chips (Language-aware: English or Malayalam)
                suggested_queries = get_suggested_questions(df, language=response_language)
                st.write("**💡 Suggested questions (Click to execute immediately):**")
                sug_cols = st.columns(min(len(suggested_queries[:4]), 4))
                clicked_suggestion = None
                for i, q_sug in enumerate(suggested_queries[:4]):
                    if sug_cols[i].button(f"💬 {q_sug}", key=f"chat_sug_{i}", use_container_width=True):
                        clicked_suggestion = q_sug

                # Input bar
                q_col1, q_col2 = st.columns([4, 1])
                with q_col1:
                    placeholder_txt = (
                        "ചോദ്യം ഇവിടെ ചോദിക്കുക (ഉദാ: ആകെ Sales എത്രയാണ്? അല്ലെങ്കിൽ: ലാപ്ടോപ്പിന്റെ വിൽപ്പന എത്ര?)"
                        if is_ml_mode
                        else "Ask any question (e.g., Which Product generated highest Sales? Or: Explain this dataset)"
                    )
                    user_q = st.text_input(
                        "Your Analysis Question:",
                        key="chat_input_text",
                        placeholder=placeholder_txt
                    )
                with q_col2:
                    st.write("")
                    st.write("")
                    btn_label = "🚀 വിശകലനം (Analyze)" if is_ml_mode else "🚀 Analyze"
                    send_btn = st.button(btn_label, use_container_width=True)

                # Check if question was triggered via Suggested Click, Voice, or Manual Input
                query_to_run = None
                if clicked_suggestion:
                    query_to_run = clicked_suggestion
                elif st.session_state.get("submitted_question"):
                    query_to_run = st.session_state.pop("submitted_question")
                elif send_btn and user_q.strip():
                    query_to_run = user_q.strip()

                if query_to_run:
                    with st.spinner("Analyzing with verified Python math & local AI..."):
                        # Execute question with language awareness
                        q_res = execute_question(df, query_to_run, language=response_language)
                        ai_text = ""

                        if q_res["has_exact_answer"]:
                            if q_res.get("requires_ai_explanation") and q_res.get("context_for_ai"):
                                try:
                                    ai_text = explain_findings(
                                        df,
                                        query_to_run,
                                        verified_context=q_res["context_for_ai"],
                                        model=selected_model,
                                        language=response_language
                                    )
                                except Exception as err:
                                    ai_text = f"Explanation note: {err}"
                        else:
                            try:
                                ai_text = explain_findings(
                                    df,
                                    query_to_run,
                                    model=selected_model,
                                    language=response_language
                                )
                            except Exception as err:
                                ai_text = f"AI Error: {err}"

                        # Append to chat history
                        st.session_state["chat_history"].append({
                            "question": query_to_run,
                            "answer_text": q_res.get("answer_text", ""),
                            "computed_data": q_res.get("computed_data"),
                            "chart_config": q_res.get("chart_config"),
                            "ai_explanation": ai_text,
                            "language": response_language,
                            "timestamp": datetime.now().strftime("%I:%M %p")
                        })
                        st.session_state["active_question"] = ""

                # Render Chat Feed
                st.markdown("---")
                feed_head_col, clear_col = st.columns([4, 1])
                with feed_head_col:
                    st.write(f"**Session Analysis Feed ({len(st.session_state['chat_history'])} queries)**")
                with clear_col:
                    if st.session_state["chat_history"]:
                        if st.button("🗑️ Clear Chat History", use_container_width=True):
                            st.session_state["chat_history"] = []
                            st.rerun()

                if not st.session_state["chat_history"]:
                    st.info("Speak using the microphone above or type a question to begin analysis.")
                else:
                    for entry in reversed(st.session_state["chat_history"]):
                        # User question bubble
                        st.markdown(
                            f'<div class="chat-bubble-user">'
                            f'<strong>👤 User ({entry["timestamp"]}):</strong> {entry["question"]}'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                        # AI answer container
                        with st.container():
                            if entry.get("answer_text"):
                                st.success(f"**Verified Calculation:**\n\n{entry['answer_text']}")

                            if entry.get("computed_data") is not None:
                                st.dataframe(entry["computed_data"], use_container_width=True)

                            if entry.get("chart_config"):
                                cfg = entry["chart_config"]
                                try:
                                    st.bar_chart(
                                        data=entry["computed_data"],
                                        x=cfg["x"],
                                        y=cfg["y"],
                                        use_container_width=True
                                    )
                                except Exception:
                                    pass

                            if entry.get("ai_explanation"):
                                lang_tag = entry.get("language", "English")
                                st.markdown(
                                    f'<div class="chat-bubble-ai">'
                                    f'<div class="ai-badge">🤖 InsightPilot AI ({lang_tag})</div><br>'
                                    f'{entry["ai_explanation"]}'
                                    f'</div>',
                                    unsafe_allow_html=True
                                )

            # ------------------------------------------
            # TAB 7: REPORTS & EXPORT
            # ------------------------------------------
            with tab_reports:
                st.subheader("Executive Reports & Data Export")
                st.write("Generate and download comprehensive analysis packages based on verified findings.")

                rep_c1, rep_c2, rep_c3 = st.columns(3)

                html_report = generate_html_report(df, active_filename, auto_insights)
                insights_csv = generate_insights_csv(auto_insights)
                cleaned_csv = df.to_csv(index=False)

                with rep_c1:
                    st.download_button(
                        label="📥 Download HTML Report",
                        data=html_report,
                        file_name=f"InsightPilot_Report_{active_filename}.html",
                        mime="text/html",
                        use_container_width=True
                    )
                with rep_c2:
                    st.download_button(
                        label="📥 Download Insights (CSV)",
                        data=insights_csv,
                        file_name=f"InsightPilot_Insights_{active_filename}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                with rep_c3:
                    st.download_button(
                        label="📥 Download Cleaned Data (CSV)",
                        data=cleaned_csv,
                        file_name=f"Cleaned_{active_filename}",
                        mime="text/csv",
                        use_container_width=True
                    )

    except Exception as error:
        st.error(f"Error analyzing dataset: {error}")

else:
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(8, 12, 22, 0.95) 100%);
                border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 16px; padding: 36px 30px; text-align: center;
                box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5); margin-top: 10px;">
        <div style="font-size: 42px; margin-bottom: 12px;">📊 ⚡ 🎙️</div>
        <div style="font-size: 24px; font-weight: 800; color: #f1f5f9; letter-spacing: -0.5px; margin-bottom: 8px;">
            AI-Powered Business Intelligence at Apple Silicon Speed
        </div>
        <div style="font-size: 14px; color: #94a3b8; max-width: 680px; margin: 0 auto 24px auto; line-height: 1.6;">
            Upload your CSV or Excel dataset to generate an instant <strong>PowerBI-style Executive Dashboard</strong>,
            study data distributions with verified Python math, and interact with your numbers using speech in English or Malayalam.
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; text-align: left; margin-top: 24px;">
            <div style="background: rgba(11, 17, 30, 0.7); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 12px; padding: 18px;">
                <div style="font-size: 18px; margin-bottom: 6px;">📈</div>
                <div style="font-size: 14px; font-weight: 700; color: #38bdf8; margin-bottom: 4px;">PowerBI Visuals Grid</div>
                <div style="font-size: 12px; color: #94a3b8; line-height: 1.4;">Autonomous ranking, trend trajectories, share breakdowns, and multi-metric correlation.</div>
            </div>
            <div style="background: rgba(11, 17, 30, 0.7); border: 1px solid rgba(129, 140, 248, 0.2); border-radius: 12px; padding: 18px;">
                <div style="font-size: 18px; margin-bottom: 6px;">🧠</div>
                <div style="font-size: 14px; font-weight: 700; color: #a5b4fc; margin-bottom: 4px;">Smart Narrative Story</div>
                <div style="font-size: 12px; color: #94a3b8; line-height: 1.4;">AI studies category distributions to synthesize growth drivers, risk alerts, and executive actions.</div>
            </div>
            <div style="background: rgba(11, 17, 30, 0.7); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 12px; padding: 18px;">
                <div style="font-size: 18px; margin-bottom: 6px;">🎙️</div>
                <div style="font-size: 14px; font-weight: 700; color: #34d399; margin-bottom: 4px;">Bilingual Voice Studio</div>
                <div style="font-size: 12px; color: #94a3b8; line-height: 1.4;">Natural English and simple Malayalam (ലളിതമായ മലയാളം) speech recognition with automatic query execution.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    d_col1, d_col2, d_col3 = st.columns([1, 2, 1])
    with d_col2:
        if st.button("🚀 Explore Demo Dataset (`sample_sales.csv`)", use_container_width=True):
            st.session_state["use_demo_dataset"] = True
            st.rerun()
