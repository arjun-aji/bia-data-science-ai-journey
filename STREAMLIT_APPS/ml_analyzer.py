"""
ML Analyzer & AutoML Studio
===========================
A complete Streamlit application for end-to-end Machine Learning:
- File Upload (CSV, Excel) & Built-in Benchmark Datasets
- Data Exploration & Statistical Profiling
- Exploratory Data Analysis (EDA) with Interactive Visualizations
- Basic & Advanced Data Cleaning (Missing Values, Duplicates, Encoding, Scaling)
- Train/Test Split & K-Fold Cross Validation
- Supervised Machine Learning Studio:
    * Classification: Logistic Regression, Decision Tree, Random Forest, KNN, SVM, Naive Bayes
    * Regression: Linear Regression, Ridge, Lasso, Decision Tree, Random Forest, KNN, SVR
    * Multi-Model Leaderboard Comparison Table & Best Model Recommender
    * In-depth Diagnostics: Confusion Matrix, Classification Report, ROC-AUC, Residuals, Feature Importance
- Unsupervised Clustering:
    * K-Means with Elbow Curve & Silhouette Analysis
    * Hierarchical (Agglomerative) Clustering with Dendrogram
- Time Series Forecasting:
    * Stationarity Testing (ADF Test), Rolling Statistics
    * ARIMA and SARIMA Forecasting with Future Projections
"""

import streamlit as st
import pandas as pd
import numpy as np
import io
import os
import time
import zipfile
import warnings
warnings.filterwarnings('ignore')

# Visualizations
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# Machine Learning - Scikit-Learn
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, confusion_matrix,
    classification_report, roc_curve, auc,
    r2_score, mean_squared_error, mean_absolute_error
)

# Classification Models
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB

# Regression Models
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR

# Clustering
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.decomposition import PCA

# Hierarchical Clustering Dendrogram
try:
    from scipy.cluster.hierarchy import dendrogram, linkage
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

# Time Series
try:
    from statsmodels.tsa.stattools import adfuller
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False


# ==========================================
# PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="ML Analyzer & AutoML Studio",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished interface
st.markdown("""
<style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2563EB;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .best-badge {
        background-color: #10B981;
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding-top: 10px;
        padding-bottom: 10px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if "raw_df" not in st.session_state:
    st.session_state.raw_df = None
if "df" not in st.session_state:
    st.session_state.df = None
if "file_name" not in st.session_state:
    st.session_state.file_name = None
if "model_results" not in st.session_state:
    st.session_state.model_results = None
if "trained_models" not in st.session_state:
    st.session_state.trained_models = {}
if "last_task_type" not in st.session_state:
    st.session_state.last_task_type = None


# ==========================================
# HELPER FUNCTIONS & BUILT-IN DATASETS
# ==========================================
@st.cache_data
def load_sample_dataset(name: str) -> pd.DataFrame:
    """Provides standard benchmark datasets for quick exploration."""
    if name == "Titanic Survival (Classification)":
        local_path = os.path.join(os.path.dirname(__file__), "data", "train.csv")
        if os.path.exists(local_path):
            return pd.read_csv(local_path)
        try:
            return pd.read_csv("https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv")
        except Exception:
            from sklearn.datasets import fetch_openml
            return fetch_openml('titanic', version=1, as_frame=True, parser='auto').frame
    elif name == "Iris (Classification)":
        from sklearn.datasets import load_iris
        raw = load_iris(as_frame=True)
        df = raw.frame
        df['target'] = df['target'].map({0: 'setosa', 1: 'versicolor', 2: 'virginica'})
        return df
    elif name == "Wine Quality (Classification)":
        from sklearn.datasets import load_wine
        raw = load_wine(as_frame=True)
        df = raw.frame
        df['target'] = df['target'].map({0: 'class_0', 1: 'class_1', 2: 'class_2'})
        return df
    elif name == "Diabetes (Regression)":
        from sklearn.datasets import load_diabetes
        raw = load_diabetes(as_frame=True)
        return raw.frame
    elif name == "California Housing (Regression)":
        from sklearn.datasets import fetch_california_housing
        raw = fetch_california_housing(as_frame=True)
        # Sample 1500 rows for swift execution
        return raw.frame.sample(1500, random_state=42).reset_index(drop=True)
    elif name == "Monthly Airline Passengers (Time Series)":
        # Standard Box-Jenkins Airline Passenger series (1949-1960)
        dates = pd.date_range(start="1949-01-01", periods=144, freq="MS")
        # Base trend + seasonal component + noise
        t = np.arange(144)
        trend = 100 + 2.5 * t
        season = 30 * np.sin(2 * np.pi * t / 12) + 15 * np.cos(2 * np.pi * t / 12)
        noise = np.random.RandomState(42).normal(0, 5, 144)
        passengers = (trend + season + noise).astype(int)
        return pd.DataFrame({"Date": dates, "Passengers": passengers})
    return pd.DataFrame()


def reset_to_original():
    """Resets the working dataframe back to the raw uploaded file."""
    if st.session_state.raw_df is not None:
        st.session_state.df = st.session_state.raw_df.copy()
        st.session_state.model_results = None
        st.session_state.trained_models = {}
        st.toast("Data reset to original version!", icon="🔄")


# ==========================================
# SIDEBAR: DATA INGESTION & CONTROLS
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/8618/8618881.png", width=65)
    st.title("ML Studio Hub")
    st.caption("Upload your data or select a preloaded benchmark.")

    source_type = st.radio(
        "Data Source",
        ["📁 Upload File", "🧪 Preloaded Benchmark"],
        index=0
    )

    if source_type == "📁 Upload File":
        uploaded_file = st.file_uploader(
            "Upload CSV, Excel or ZIP archive",
            type=["csv", "xlsx", "xls", "zip"],
            help="Supports CSV, Excel workbooks, and ZIP archives containing CSVs (e.g. titanic.zip)"
        )
        if uploaded_file is not None:
            file_ext = os.path.splitext(uploaded_file.name)[-1].lower()
            if file_ext == ".zip":
                try:
                    with zipfile.ZipFile(uploaded_file) as z:
                        csv_names = [f for f in z.namelist() if f.endswith(('.csv', '.xlsx', '.xls')) and not f.startswith(('__MACOSX/', '.'))]
                        if not csv_names:
                            st.error("No CSV or Excel files found inside the uploaded ZIP archive.")
                        else:
                            # Prefer 'train.csv' if available
                            default_idx = 0
                            for i, cn in enumerate(csv_names):
                                if "train" in cn.lower():
                                    default_idx = i
                                    break
                            selected_inner = st.selectbox("Select file inside ZIP", csv_names, index=default_idx)
                            file_key = f"{uploaded_file.name}:{selected_inner}"
                            if st.session_state.file_name != file_key:
                                with z.open(selected_inner) as zf:
                                    if selected_inner.endswith('.csv'):
                                        df_loaded = pd.read_csv(zf)
                                    else:
                                        df_loaded = pd.read_excel(zf)
                                st.session_state.raw_df = df_loaded.copy()
                                st.session_state.df = df_loaded.copy()
                                st.session_state.file_name = file_key
                                st.session_state.model_results = None
                                st.session_state.trained_models = {}
                                st.success(f"Loaded: `{selected_inner}` from `{uploaded_file.name}`")
                except Exception as e:
                    st.error(f"Failed to process ZIP archive: {e}")
            else:
                if st.session_state.file_name != uploaded_file.name:
                    try:
                        if file_ext == ".csv":
                            df_loaded = pd.read_csv(uploaded_file)
                        else:
                            df_loaded = pd.read_excel(uploaded_file)
                        
                        st.session_state.raw_df = df_loaded.copy()
                        st.session_state.df = df_loaded.copy()
                        st.session_state.file_name = uploaded_file.name
                        st.session_state.model_results = None
                        st.session_state.trained_models = {}
                        st.success(f"Loaded: {uploaded_file.name}")
                    except Exception as e:
                        st.error(f"Failed to load file: {e}")
    else:
        sample_choice = st.selectbox(
            "Select Benchmark Dataset",
            [
                "Titanic Survival (Classification)",
                "Iris (Classification)",
                "Wine Quality (Classification)",
                "Diabetes (Regression)",
                "California Housing (Regression)",
                "Monthly Airline Passengers (Time Series)"
            ]
        )
        if st.button("Load Dataset", type="primary", use_container_width=True):
            df_loaded = load_sample_dataset(sample_choice)
            st.session_state.raw_df = df_loaded.copy()
            st.session_state.df = df_loaded.copy()
            st.session_state.file_name = sample_choice
            st.session_state.model_results = None
            st.session_state.trained_models = {}
            st.success(f"Loaded: {sample_choice}")

    st.divider()

    # Reset button & session info
    if st.session_state.df is not None:
        st.write(f"**Active File:** `{st.session_state.file_name}`")
        st.write(f"**Shape:** {st.session_state.df.shape[0]} rows × {st.session_state.df.shape[1]} cols")
        
        if st.button("🔄 Reset to Original Data", use_container_width=True):
            reset_to_original()
            st.rerun()

        # Download active dataset
        csv_buffer = io.StringIO()
        st.session_state.df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="💾 Download Active CSV",
            data=csv_buffer.getvalue(),
            file_name=f"processed_{st.session_state.file_name or 'dataset'}.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.markdown("---")
    st.caption("Engineered for Rapid Data Exploration & AutoML benchmarking.")


# ==========================================
# MAIN APPLICATION BODY
# ==========================================
st.markdown('<div class="main-title">🤖 Machine Learning Analyzer & AutoML Studio</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Explore, clean, benchmark, and deploy machine learning models '
    'with automated cross-validation, hyperparameter reporting, clustering, and time series forecasting.</div>',
    unsafe_allow_html=True
)

if st.session_state.df is None:
    st.info("👈 **To get started**, upload a CSV or Excel file from the sidebar, or select one of the preloaded benchmark datasets.")
    
    # Feature showcase cards
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        ### 🔍 Data Exploration & EDA
        - Comprehensive column summary & null diagnostics
        - Interactive histograms, boxplots, and correlation heatmaps
        - Categorical distributions and scatter plots
        """)
    with c2:
        st.markdown("""
        ### 🧹 Data Cleaning Suite
        - Impute missing numerical & categorical values
        - Deduplication & column dropping
        - One-hot & label encoding with standard scalers
        """)
    with c3:
        st.markdown("""
        ### ⚡ Supervised & Unsupervised ML
        - **Classification & Regression**: Compare 7+ algorithms in one click
        - Confusion matrices, ROC curves, Residual plots
        - **K-Means & Hierarchical Clustering** + **ARIMA / SARIMA**
        """)
    st.stop()

# Active dataframe pointer
df = st.session_state.df

# Create main navigation tabs
tab_explore, tab_eda, tab_clean, tab_supervised, tab_cluster, tab_timeseries = st.tabs([
    "📁 Data Exploration",
    "📊 EDA Visualizer",
    "🧹 Data Cleaning",
    "🎯 Supervised ML Studio",
    "🧬 Clustering",
    "📈 Time Series"
])


# ==========================================
# TAB 1: DATA EXPLORATION
# ==========================================
with tab_explore:
    st.subheader("📋 Dataset Overview & Structural Profiling")
    
    # Key Summary Metric Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{int(df.shape[0]):,}</div><div class="metric-label">Total Rows</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{int(df.shape[1]):,}</div><div class="metric-label">Total Columns</div></div>', unsafe_allow_html=True)
    with col3:
        num_cols_cnt = int(len(df.select_dtypes(include=[np.number]).columns))
        st.markdown(f'<div class="metric-card"><div class="metric-value">{num_cols_cnt}</div><div class="metric-label">Numeric Cols</div></div>', unsafe_allow_html=True)
    with col4:
        missing_total = int(df.isna().sum().sum())
        missing_pct = float((missing_total / (df.shape[0] * df.shape[1])) * 100) if (df.shape[0] * df.shape[1]) > 0 else 0.0
        st.markdown(f'<div class="metric-card"><div class="metric-value">{missing_total:,} ({missing_pct:.1f}%)</div><div class="metric-label">Missing Cells</div></div>', unsafe_allow_html=True)
    with col5:
        dups_cnt = int(df.duplicated().sum())
        st.markdown(f'<div class="metric-card"><div class="metric-value">{dups_cnt:,}</div><div class="metric-label">Duplicate Rows</div></div>', unsafe_allow_html=True)

    st.write("")
    
    # Data Preview
    st.markdown("#### 🔍 Data Preview")
    preview_mode = st.radio("Display slice", ["Head (first 10)", "Tail (last 10)", "Random Sample (10 rows)"], horizontal=True)
    if preview_mode == "Head (first 10)":
        st.dataframe(df.head(10), use_container_width=True)
    elif preview_mode == "Tail (last 10)":
        st.dataframe(df.tail(10), use_container_width=True)
    else:
        sample_size = min(10, len(df))
        st.dataframe(df.sample(sample_size, random_state=42), use_container_width=True)

    st.markdown("---")

    # Column Details Table
    st.markdown("#### 🏷️ Column-wise Schema & Missing Value Diagnostic")
    col_info = []
    for col in df.columns:
        s = df[col]
        null_count = s.isna().sum()
        null_pct = (null_count / len(df)) * 100
        unique_count = s.nunique(dropna=True)
        sample_val = str(s.dropna().iloc[0]) if len(s.dropna()) > 0 else "N/A"
        col_info.append({
            "Column Name": col,
            "Data Type": str(s.dtype),
            "Non-Null Count": len(s) - null_count,
            "Missing Count": null_count,
            "Missing (%)": f"{null_pct:.2f}%",
            "Unique Values": unique_count,
            "Sample Value": sample_val[:35]
        })
    df_col_info = pd.DataFrame(col_info)
    st.dataframe(df_col_info, use_container_width=True)

    # Numerical & Categorical Summaries
    st.markdown("#### 📐 Statistical Summary")
    sub_tab1, sub_tab2 = st.tabs(["Numerical Features", "Categorical Features"])
    
    with sub_tab1:
        num_df = df.select_dtypes(include=[np.number])
        if not num_df.empty:
            summary_stats = num_df.describe().T
            summary_stats["skewness"] = num_df.skew()
            st.dataframe(summary_stats.style.format("{:.3f}"), use_container_width=True)
        else:
            st.info("No numerical columns detected.")

    with sub_tab2:
        cat_df = df.select_dtypes(include=['object', 'category', 'bool'])
        if not cat_df.empty:
            st.dataframe(cat_df.describe().T, use_container_width=True)
        else:
            st.info("No categorical/object columns detected.")


# ==========================================
# TAB 2: EXPLORATORY DATA ANALYSIS (EDA)
# ==========================================
with tab_eda:
    st.subheader("📊 Exploratory Data Analysis (EDA)")
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
    all_cols = df.columns.tolist()

    eda_chart_type = st.selectbox(
        "Choose Visualization Type",
        [
            "Numeric Distribution (Histogram & KDE)",
            "Boxplot & Outlier Inspector",
            "Categorical Value Counts (Bar Chart)",
            "Bivariate Scatter Plot",
            "Correlation Heatmap",
            "Line Chart (Trend / Time Series)"
        ]
    )

    if eda_chart_type == "Numeric Distribution (Histogram & KDE)":
        if not numeric_cols:
            st.warning("No numeric columns available to plot.")
        else:
            col_x, col_bins = st.columns([3, 1])
            with col_x:
                selected_num = st.selectbox("Select Numeric Column", numeric_cols)
            with col_bins:
                num_bins = st.slider("Bins", min_value=5, max_value=80, value=25)

            fig, ax = plt.subplots(figsize=(9, 4.5))
            series_data = df[selected_num].dropna()
            ax.hist(series_data, bins=num_bins, color='#3B82F6', edgecolor='black', alpha=0.7, density=True)
            
            # Kernel density approximation
            if len(series_data) > 1 and series_data.std() > 0:
                try:
                    from scipy.stats import gaussian_kde
                    density = gaussian_kde(series_data)
                    xs = np.linspace(series_data.min(), series_data.max(), 200)
                    ax.plot(xs, density(xs), color='#DC2626', linewidth=2.5, label='KDE')
                    ax.legend()
                except Exception:
                    pass
            ax.set_title(f"Distribution of {selected_num}", fontsize=13, fontweight='bold')
            ax.set_xlabel(selected_num)
            ax.set_ylabel("Density")
            ax.grid(True, linestyle='--', alpha=0.4)
            st.pyplot(fig)
            plt.close(fig)

    elif eda_chart_type == "Boxplot & Outlier Inspector":
        if not numeric_cols:
            st.warning("No numeric columns available.")
        else:
            c_box1, c_box2 = st.columns(2)
            with c_box1:
                box_col = st.selectbox("Select Numeric Feature", numeric_cols)
            with c_box2:
                cat_group = st.selectbox("Group By Categorical Feature (Optional)", ["None"] + categorical_cols)

            fig, ax = plt.subplots(figsize=(9, 4.5))
            if cat_group == "None":
                clean_data = pd.to_numeric(df[box_col], errors='coerce').dropna().values
                if len(clean_data) > 0:
                    ax.boxplot(clean_data, vert=False, patch_artist=True,
                               boxprops=dict(facecolor='#93C5FD', color='#1D4ED8'),
                               medianprops=dict(color='#DC2626', linewidth=2))
                    ax.set_xlabel(box_col)
                    ax.set_title(f"Boxplot of {box_col}", fontsize=13, fontweight='bold')
                else:
                    st.warning(f"No numeric values available in '{box_col}'.")
            else:
                top_cats = df[cat_group].dropna().value_counts().head(10).index
                filtered = df[df[cat_group].isin(top_cats)].copy()
                filtered[box_col] = pd.to_numeric(filtered[box_col], errors='coerce')
                filtered = filtered.dropna(subset=[box_col])
                
                valid_groups = []
                valid_labels = []
                for cat in top_cats:
                    sub_vals = filtered[filtered[cat_group] == cat][box_col].values
                    if len(sub_vals) > 0:
                        valid_groups.append(sub_vals)
                        valid_labels.append(str(cat)[:15])
                
                if valid_groups:
                    ax.boxplot(valid_groups, vert=True, patch_artist=True,
                               boxprops=dict(facecolor='#A7F3D0', color='#047857'),
                               medianprops=dict(color='#B91C1C', linewidth=2))
                    ax.set_xticks(range(1, len(valid_labels) + 1))
                    ax.set_xticklabels(valid_labels, rotation=30, ha='right')
                    ax.set_ylabel(box_col)
                    ax.set_xlabel(cat_group)
                    ax.set_title(f"{box_col} Grouped by {cat_group}", fontsize=13, fontweight='bold')
                else:
                    st.warning("No valid numeric data found for the selected grouping.")
            ax.grid(True, linestyle='--', alpha=0.3)
            st.pyplot(fig)
            plt.close(fig)

    elif eda_chart_type == "Categorical Value Counts (Bar Chart)":
        if not categorical_cols:
            st.info("No categorical columns detected. You can also pick a discrete numeric column below.")
            cat_pick = st.selectbox("Select Column", all_cols)
        else:
            cat_pick = st.selectbox("Select Categorical Column", categorical_cols + numeric_cols)

        top_n = st.slider("Max Unique Categories to Show", min_value=3, max_value=30, value=10)
        vc = df[cat_pick].astype(str).value_counts().head(top_n)
        
        fig, ax = plt.subplots(figsize=(9, 4.5))
        labels_str = [str(x)[:20] for x in vc.index]
        bars = ax.bar(labels_str, vc.values, color='#6366F1', edgecolor='black', alpha=0.8)
        ax.set_title(f"Frequency Count: {cat_pick} (Top {top_n})", fontsize=13, fontweight='bold')
        ax.set_ylabel("Count")
        ax.set_xticks(range(len(labels_str)))
        ax.set_xticklabels(labels_str, rotation=35, ha='right')
        # Value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=9)
        ax.grid(True, linestyle='--', alpha=0.3, axis='y')
        st.pyplot(fig)
        plt.close(fig)

    elif eda_chart_type == "Bivariate Scatter Plot":
        if len(numeric_cols) < 2:
            st.warning("Need at least 2 numerical columns for a scatter plot.")
        else:
            s_c1, s_c2, s_c3 = st.columns(3)
            with s_c1:
                x_axis = st.selectbox("X-Axis", numeric_cols, index=0)
            with s_c2:
                y_axis = st.selectbox("Y-Axis", numeric_cols, index=min(1, len(numeric_cols)-1))
            with s_c3:
                color_col = st.selectbox("Color By (Optional)", ["None"] + all_cols)

            fig, ax = plt.subplots(figsize=(9, 5))
            if color_col != "None":
                color_series = df[color_col]
                if color_series.dtype == 'object' or color_series.nunique() <= 10:
                    unique_vals = color_series.dropna().unique()
                    colors = plt.cm.tab10(np.linspace(0, 1, len(unique_vals)))
                    for val, c in zip(unique_vals, colors):
                        subset = df[df[color_col] == val]
                        ax.scatter(subset[x_axis], subset[y_axis], label=str(val), color=c, alpha=0.7, edgecolors='none', s=45)
                    ax.legend(title=color_col, bbox_to_anchor=(1.05, 1), loc='upper left')
                else:
                    scatter = ax.scatter(df[x_axis], df[y_axis], c=df[color_col], cmap='viridis', alpha=0.7, edgecolors='none', s=45)
                    fig.colorbar(scatter, ax=ax, label=color_col)
            else:
                ax.scatter(df[x_axis], df[y_axis], color='#2563EB', alpha=0.6, edgecolors='none', s=45)

            ax.set_xlabel(x_axis, fontweight='bold')
            ax.set_ylabel(y_axis, fontweight='bold')
            ax.set_title(f"{x_axis} vs {y_axis}", fontsize=13, fontweight='bold')
            ax.grid(True, linestyle='--', alpha=0.3)
            st.pyplot(fig)
            plt.close(fig)

    elif eda_chart_type == "Correlation Heatmap":
        if len(numeric_cols) < 2:
            st.warning("At least two numerical columns are required for correlation analysis.")
        else:
            corr = df[numeric_cols].corr()
            fig, ax = plt.subplots(figsize=(max(7, len(numeric_cols)*0.8), max(6, len(numeric_cols)*0.7)))
            cax = ax.matshow(corr, cmap='coolwarm', vmin=-1, vmax=1)
            fig.colorbar(cax)
            ax.set_xticks(range(len(numeric_cols)))
            ax.set_yticks(range(len(numeric_cols)))
            ax.set_xticklabels(numeric_cols, rotation=45, ha='left')
            ax.set_yticklabels(numeric_cols)
            
            # Print correlation values inside cells
            for i in range(len(numeric_cols)):
                for j in range(len(numeric_cols)):
                    val = corr.iloc[i, j]
                    ax.text(j, i, f"{val:.2f}", ha='center', va='center',
                            color="white" if abs(val) > 0.5 else "black", fontsize=9)
            ax.set_title("Feature Correlation Matrix", fontsize=14, fontweight='bold', pad=20)
            st.pyplot(fig)
            plt.close(fig)

    elif eda_chart_type == "Line Chart (Trend / Time Series)":
        l_c1, l_c2 = st.columns(2)
        with l_c1:
            line_x = st.selectbox("X-Axis (Date or Order)", all_cols)
        with l_c2:
            line_y = st.selectbox("Y-Axis (Numeric Value)", numeric_cols)

        fig, ax = plt.subplots(figsize=(10, 4.5))
        sorted_df = df.sort_values(by=line_x) if line_x else df
        ax.plot(sorted_df[line_x], sorted_df[line_y], color='#2563EB', linewidth=2, marker='o', markersize=3, alpha=0.8)
        ax.set_xlabel(line_x, fontweight='bold')
        ax.set_ylabel(line_y, fontweight='bold')
        ax.set_title(f"Trend Plot: {line_y} over {line_x}", fontsize=13, fontweight='bold')
        plt.xticks(rotation=30, ha='right')
        ax.grid(True, linestyle='--', alpha=0.3)
        st.pyplot(fig)
        plt.close(fig)


# ==========================================
# TAB 3: BASIC DATA CLEANING
# ==========================================
with tab_clean:
    st.subheader("🧹 Basic Data Cleaning & Feature Transformation")
    st.caption("Apply transformations directly to the working dataset. Changes are saved across tabs.")

    clean_c1, clean_c2 = st.columns(2)

    # 1. Missing Values Handler
    with clean_c1:
        st.markdown("#### 1. Handle Missing Values")
        null_cols = [c for c in df.columns if df[c].isna().sum() > 0]
        
        if not null_cols:
            st.success("🎉 No missing values detected in the current dataset!")
        else:
            st.warning(f"Detected {len(null_cols)} columns with missing entries: {', '.join(null_cols[:6])}")
            impute_strategy = st.selectbox(
                "Imputation Strategy for Numerical Missing Values",
                ["Mean", "Median", "Constant (0)", "Drop Rows with any NaN", "Drop Columns with >50% NaN"]
            )
            cat_impute_strategy = st.selectbox(
                "Imputation Strategy for Categorical Missing Values",
                ["Mode (Most Frequent)", "Constant ('Missing')", "Drop Rows"]
            )

            if st.button("Apply Missing Value Treatment", type="primary"):
                df_clean = df.copy()
                
                # Drop operations
                if impute_strategy == "Drop Rows with any NaN" or cat_impute_strategy == "Drop Rows":
                    df_clean.dropna(inplace=True)
                elif impute_strategy == "Drop Columns with >50% NaN":
                    thresh = len(df_clean) * 0.5
                    df_clean.dropna(thresh=thresh, axis=1, inplace=True)
                else:
                    # Impute Numerical
                    num_missing = df_clean.select_dtypes(include=[np.number]).columns
                    for col in num_missing:
                        if df_clean[col].isna().sum() > 0:
                            if impute_strategy == "Mean":
                                df_clean[col].fillna(df_clean[col].mean(), inplace=True)
                            elif impute_strategy == "Median":
                                df_clean[col].fillna(df_clean[col].median(), inplace=True)
                            elif impute_strategy == "Constant (0)":
                                df_clean[col].fillna(0, inplace=True)

                    # Impute Categorical
                    cat_missing = df_clean.select_dtypes(include=['object', 'category']).columns
                    for col in cat_missing:
                        if df_clean[col].isna().sum() > 0:
                            if cat_impute_strategy == "Mode (Most Frequent)":
                                mode_val = df_clean[col].mode()
                                if not mode_val.empty:
                                    df_clean[col].fillna(mode_val[0], inplace=True)
                            elif cat_impute_strategy == "Constant ('Missing')":
                                df_clean[col].fillna("Missing", inplace=True)

                st.session_state.df = df_clean
                st.success("Missing values imputed successfully!")
                st.rerun()

    # 2. Duplicate Removal & Column Dropper
    with clean_c2:
        st.markdown("#### 2. Deduplication & Drop Columns")
        dup_count = int(df.duplicated().sum())
        st.write(f"**Duplicate records found:** `{dup_count}`")
        if st.button("Remove Duplicate Rows", disabled=bool(dup_count == 0)):
            df_dedup = df.drop_duplicates()
            st.session_state.df = df_dedup
            st.success(f"Removed {dup_count} duplicate rows!")
            st.rerun()

        st.markdown("##### Drop Unwanted Columns")
        cols_to_drop = st.multiselect("Select columns to permanently drop", df.columns.tolist())
        if st.button("Drop Selected Columns", disabled=bool(len(cols_to_drop) == 0)):
            df_dropped = df.drop(columns=cols_to_drop)
            st.session_state.df = df_dropped
            st.success(f"Dropped columns: {', '.join(cols_to_drop)}")
            st.rerun()

    st.markdown("---")
    
    # 3. Categorical Encoding & Feature Scaling
    st.markdown("#### 3. Encoding & Feature Scaling")
    enc_col1, enc_col2 = st.columns(2)
    
    with enc_col1:
        st.markdown("##### Categorical Encoding")
        cat_cols_available = df.select_dtypes(include=['object', 'category']).columns.tolist()
        if not cat_cols_available:
            st.info("No categorical columns available to encode.")
        else:
            enc_target_cols = st.multiselect(
                "Select columns to encode",
                cat_cols_available,
                default=[],
                help="Select columns to transform. High-cardinality ID columns should use Label Encoding."
            )
            enc_method = st.radio("Encoding Method", ["Label Encoding (Single column integer)", "One-Hot Encoding (Dummies)"])
            
            # High cardinality safety check
            high_card_selected = [c for c in enc_target_cols if df[c].nunique() > 50]
            limit_top_n = False
            top_n_cats = 10
            
            if enc_method.startswith("One-Hot") and high_card_selected:
                st.error(
                    f"⚠️ **High Cardinality Alert**: "
                    f"{', '.join([f'`{c}` ({df[c].nunique()} unique)' for c in high_card_selected])} "
                    f"contain too many unique values for One-Hot Encoding. "
                    "Encoding them would generate tens of thousands of columns and freeze the browser. "
                    "Please switch to **Label Encoding** or drop ID columns."
                )
                limit_top_n = st.checkbox("Or group all categories outside Top 10 into 'Other'?", value=False)
                if limit_top_n:
                    top_n_cats = st.slider("Keep Top N Categories", min_value=3, max_value=25, value=10)

            # Determine if safe to encode
            can_encode = len(enc_target_cols) > 0 and (
                not enc_method.startswith("One-Hot") or not high_card_selected or limit_top_n
            )
            
            if st.button("Apply Categorical Encoding", disabled=not bool(can_encode)):
                df_enc = df.copy()
                if enc_method.startswith("Label"):
                    le = LabelEncoder()
                    for c in enc_target_cols:
                        df_enc[c] = le.fit_transform(df_enc[c].astype(str))
                else:
                    for c in enc_target_cols:
                        if limit_top_n and df_enc[c].nunique() > top_n_cats:
                            top_cats = df_enc[c].value_counts().head(top_n_cats).index
                            df_enc[c] = df_enc[c].apply(lambda x: x if x in top_cats else "Other")
                    df_enc = pd.get_dummies(df_enc, columns=enc_target_cols, drop_first=True)
                
                st.session_state.df = df_enc
                st.success(f"Encoded columns successfully with {enc_method}!")
                st.rerun()

    with enc_col2:
        st.markdown("##### Feature Scaling")
        num_cols_for_scale = df.select_dtypes(include=[np.number]).columns.tolist()
        if not num_cols_for_scale:
            st.info("No numeric columns available to scale.")
        else:
            scale_cols = st.multiselect("Select numerical columns to scale", num_cols_for_scale)
            scaler_choice = st.selectbox("Scaling Method", ["StandardScaler (Z-Score)", "MinMaxScaler (0 to 1)", "RobustScaler (Median & IQR)"])
            
            if st.button("Apply Feature Scaling", disabled=bool(len(scale_cols) == 0)):
                df_scaled = df.copy()
                if scaler_choice.startswith("Standard"):
                    scaler = StandardScaler()
                elif scaler_choice.startswith("MinMax"):
                    scaler = MinMaxScaler()
                else:
                    scaler = RobustScaler()
                
                df_scaled[scale_cols] = scaler.fit_transform(df_scaled[scale_cols])
                st.session_state.df = df_scaled
                st.success(f"Scaled {len(scale_cols)} columns with {scaler_choice}!")
                st.rerun()


# ==========================================
# TAB 4: SUPERVISED ML STUDIO
# ==========================================
with tab_supervised:
    st.subheader("🎯 Supervised Machine Learning Studio")
    st.caption("Train, evaluate, and benchmark multiple ML algorithms with train/test split and K-Fold cross validation.")

    # Target variable selection
    all_columns = df.columns.tolist()
    default_target_idx = len(all_columns) - 1
    
    col_tgt, col_task, col_split = st.columns([2, 1.5, 1.5])
    with col_tgt:
        target_col = st.selectbox("🎯 Select Target Variable (Y)", all_columns, index=default_target_idx)
    
    # Auto-detect task type
    target_series = df[target_col].dropna()
    is_numeric = np.issubdtype(target_series.dtype, np.number)
    unique_vals_count = target_series.nunique()
    
    suggested_task = "Classification" if (not is_numeric or unique_vals_count <= 10) else "Regression"
    
    with col_task:
        task_type = st.selectbox("Task Type", ["Classification", "Regression"], index=0 if suggested_task == "Classification" else 1)
        st.caption(f"Auto-suggested: **{suggested_task}** (Uniques: {unique_vals_count})")

    with col_split:
        test_ratio = st.slider("Test Size Ratio", min_value=0.1, max_value=0.4, value=0.2, step=0.05)

    # Feature selection
    possible_features = [c for c in all_columns if c != target_col]
    selected_features = st.multiselect("Select Feature Columns (X)", possible_features, default=possible_features)

    # Validation options
    c_kf1, c_kf2 = st.columns(2)
    with c_kf1:
        use_kfold = st.checkbox("Enable K-Fold Cross Validation", value=True)
    with c_kf2:
        k_folds = st.slider("Number of Folds (K)", min_value=2, max_value=10, value=5) if use_kfold else 5

    st.markdown("---")

    # Algorithm Checklists
    if task_type == "Classification":
        available_models = {
            "Logistic Regression": LogisticRegression(max_iter=500),
            "Decision Tree Classifier": DecisionTreeClassifier(random_state=42),
            "Random Forest Classifier": RandomForestClassifier(n_estimators=100, random_state=42),
            "K-Nearest Neighbors (KNN)": KNeighborsClassifier(),
            "Support Vector Machine (SVC)": SVC(probability=True, random_state=42),
            "Gaussian Naive Bayes": GaussianNB(),
            "Gradient Boosting Classifier": GradientBoostingClassifier(random_state=42)
        }
    else:
        available_models = {
            "Linear Regression": LinearRegression(),
            "Ridge Regression": Ridge(),
            "Lasso Regression": Lasso(),
            "Decision Tree Regressor": DecisionTreeRegressor(random_state=42),
            "Random Forest Regressor": RandomForestRegressor(n_estimators=100, random_state=42),
            "K-Nearest Neighbors (KNN)": KNeighborsRegressor(),
            "Support Vector Regressor (SVR)": SVR(),
            "Gradient Boosting Regressor": GradientBoostingRegressor(random_state=42)
        }

    st.markdown("#### ⚡ Select Algorithms to Benchmark")
    col_sel_all, _ = st.columns([2, 6])
    with col_sel_all:
        select_all_models = st.checkbox("Select All Algorithms", value=True)
    
    if select_all_models:
        selected_model_names = list(available_models.keys())
    else:
        selected_model_names = st.multiselect(
            "Choose Algorithms",
            list(available_models.keys()),
            default=list(available_models.keys())[:3]
        )

    # RUN BENCHMARK BUTTON
    run_btn = st.button("🚀 Run Models & Generate Leaderboard", type="primary", use_container_width=True)

    if run_btn:
        if not selected_features:
            st.error("Please select at least one feature column (X).")
        elif not selected_model_names:
            st.error("Please select at least one algorithm to run.")
        else:
            with st.spinner("Preparing data and training models..."):
                # Clean missing rows for target and prepare features
                data_subset = df[selected_features + [target_col]].dropna(subset=[target_col]).copy()
                if len(data_subset) < 10:
                    st.error("Insufficient samples remaining with non-null target values.")
                    st.stop()

                X = data_subset[selected_features].copy()
                y = data_subset[target_col].copy()

                # Automatically impute missing feature values if not cleaned earlier
                num_missing_in_x = X.select_dtypes(include=[np.number]).columns
                for col in num_missing_in_x:
                    if X[col].isna().sum() > 0:
                        X[col] = X[col].fillna(X[col].median())

                cat_missing_in_x = X.select_dtypes(include=['object', 'category', 'bool']).columns
                for col in cat_missing_in_x:
                    if X[col].isna().sum() > 0:
                        m_val = X[col].mode()
                        X[col] = X[col].fillna(m_val[0] if not m_val.empty else "Missing")

                # Handle non-numeric categorical features automatically for modeling
                cat_cols_in_x = X.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
                if len(cat_cols_in_x) > 0:
                    high_card_features = [c for c in cat_cols_in_x if X[c].nunique() > 50]
                    low_card_features = [c for c in cat_cols_in_x if X[c].nunique() <= 50]

                    # LabelEncode high cardinality features to avoid exploding dimensions
                    if high_card_features:
                        st.info(f"High-cardinality features ({', '.join(high_card_features)}) were LabelEncoded to prevent dimensional explosion.")
                        for c in high_card_features:
                            X[c] = LabelEncoder().fit_transform(X[c].astype(str))

                    if low_card_features:
                        X = pd.get_dummies(X, columns=low_card_features, drop_first=True)

                # Encode target if classification and non-numeric
                target_encoder = None
                if task_type == "Classification":
                    if y.dtype == 'object' or not np.issubdtype(y.dtype, np.number):
                        target_encoder = LabelEncoder()
                        y = target_encoder.fit_transform(y.astype(str))

                # Standard Train-Test Split
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=test_ratio, random_state=42,
                    stratify=y if task_type == "Classification" and len(np.unique(y)) > 1 else None
                )

                # Feature scaling for distance & linear models
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)

                results = []
                trained_store = {}

                prog_bar = st.progress(0)
                for idx, name in enumerate(selected_model_names):
                    model = available_models[name]
                    
                    # Some models benefit heavily from scaling
                    use_scaled = name in ["Logistic Regression", "K-Nearest Neighbors (KNN)", "Support Vector Machine (SVC)", "Support Vector Regressor (SVR)", "Linear Regression", "Ridge Regression", "Lasso Regression"]
                    X_tr = X_train_scaled if use_scaled else X_train
                    X_te = X_test_scaled if use_scaled else X_test

                    try:
                        # Fit model
                        model.fit(X_tr, y_train)
                        y_pred_train = model.predict(X_tr)
                        y_pred_test = model.predict(X_te)

                        trained_store[name] = {
                            "model": model,
                            "use_scaled": use_scaled,
                            "y_pred_test": y_pred_test,
                            "y_test": y_test,
                            "X_test": X_te,
                            "feature_names": X.columns.tolist()
                        }

                        if task_type == "Classification":
                            acc_train = accuracy_score(y_train, y_pred_train)
                            acc_test = accuracy_score(y_test, y_pred_test)
                            prec = precision_score(y_test, y_pred_test, average='weighted', zero_division=0)
                            rec = recall_score(y_test, y_pred_test, average='weighted', zero_division=0)
                            f1 = f1_score(y_test, y_pred_test, average='weighted', zero_division=0)
                            
                            kf_score_str = "N/A"
                            if use_kfold:
                                cv = KFold(n_splits=k_folds, shuffle=True, random_state=42)
                                cv_scores = cross_val_score(model, X_train_scaled if use_scaled else X_train, y_train, cv=cv, scoring='accuracy')
                                kf_score_str = f"{cv_scores.mean():.3f} (±{cv_scores.std():.3f})"

                            results.append({
                                "Model": name,
                                "Test Accuracy": acc_test,
                                "Train Accuracy": acc_train,
                                "Precision": prec,
                                "Recall": rec,
                                "F1-Score": f1,
                                f"K-Fold Acc (K={k_folds})": kf_score_str
                            })
                        else:
                            r2_tr = r2_score(y_train, y_pred_train)
                            r2_te = r2_score(y_test, y_pred_test)
                            mae = mean_absolute_error(y_test, y_pred_test)
                            mse = mean_squared_error(y_test, y_pred_test)
                            rmse = np.sqrt(mse)

                            kf_score_str = "N/A"
                            if use_kfold:
                                cv = KFold(n_splits=k_folds, shuffle=True, random_state=42)
                                cv_scores = cross_val_score(model, X_train_scaled if use_scaled else X_train, y_train, cv=cv, scoring='r2')
                                kf_score_str = f"{cv_scores.mean():.3f} (±{cv_scores.std():.3f})"

                            results.append({
                                "Model": name,
                                "Test R²": r2_te,
                                "Train R²": r2_tr,
                                "RMSE": rmse,
                                "MAE": mae,
                                "MSE": mse,
                                f"K-Fold R² (K={k_folds})": kf_score_str
                            })
                    except Exception as err:
                        st.warning(f"Error training {name}: {err}")

                    prog_bar.progress((idx + 1) / len(selected_model_names))
                
                time.sleep(0.3)
                prog_bar.empty()

                if results:
                    st.session_state.model_results = pd.DataFrame(results)
                    st.session_state.trained_models = trained_store
                    st.session_state.last_task_type = task_type
                    st.session_state.target_encoder = target_encoder

    # DISPLAY BENCHMARK RESULTS & LEADERBOARD
    if st.session_state.model_results is not None:
        st.markdown("### 🏆 Model Comparison Leaderboard")
        results_df = st.session_state.model_results.copy()
        current_task = st.session_state.last_task_type

        # Sort by primary metric
        if current_task == "Classification":
            sort_metric = "Test Accuracy"
            results_df = results_df.sort_values(by=sort_metric, ascending=False).reset_index(drop=True)
            best_model_name = results_df.iloc[0]["Model"]
            best_score = results_df.iloc[0][sort_metric]
            st.success(f"🥇 **Champion Model:** `{best_model_name}` with **{sort_metric}: {best_score:.4f}**")
        else:
            sort_metric = "Test R²"
            results_df = results_df.sort_values(by=sort_metric, ascending=False).reset_index(drop=True)
            best_model_name = results_df.iloc[0]["Model"]
            best_score = results_df.iloc[0][sort_metric]
            st.success(f"🥇 **Champion Model:** `{best_model_name}` with **{sort_metric}: {best_score:.4f}**")

        # Format and display table with highlighting
        numeric_format = {col: "{:.4f}" for col in results_df.select_dtypes(include=[np.number]).columns}
        st.dataframe(results_df.style.format(numeric_format), use_container_width=True)

        st.markdown("---")

        # In-depth Diagnostics & Confusion Matrix
        st.markdown("### 🔬 Detailed Model Diagnostics & Deep Dive")
        selected_inspect_model = st.selectbox(
            "Select Model to Inspect in Detail",
            list(st.session_state.trained_models.keys()),
            index=list(st.session_state.trained_models.keys()).index(best_model_name) if best_model_name in st.session_state.trained_models else 0
        )

        model_info = st.session_state.trained_models[selected_inspect_model]
        y_true = model_info["y_test"]
        y_pred = model_info["y_pred_test"]
        model_obj = model_info["model"]
        feature_names = model_info["feature_names"]

        if current_task == "Classification":
            diag_c1, diag_c2 = st.columns(2)
            
            with diag_c1:
                st.markdown("#### 🔲 Confusion Matrix")
                cm = confusion_matrix(y_true, y_pred)
                fig_cm, ax_cm = plt.subplots(figsize=(5, 4))
                cax = ax_cm.matshow(cm, cmap='Blues', alpha=0.8)
                fig_cm.colorbar(cax)
                
                for i in range(cm.shape[0]):
                    for j in range(cm.shape[1]):
                        ax_cm.text(j, i, str(cm[i, j]), ha='center', va='center',
                                   color='white' if cm[i, j] > cm.max() / 2 else 'black',
                                   fontweight='bold', fontsize=12)
                
                labels = [str(x) for x in np.unique(y_true)]
                if st.session_state.get("target_encoder") is not None:
                    try:
                        labels = [str(l) for l in st.session_state.target_encoder.classes_]
                    except Exception:
                        pass
                ax_cm.set_xticks(range(len(labels)))
                ax_cm.set_yticks(range(len(labels)))
                ax_cm.set_xticklabels(labels, rotation=45, ha='left')
                ax_cm.set_yticklabels(labels)
                ax_cm.set_xlabel("Predicted Label", fontweight='bold')
                ax_cm.set_ylabel("True Label", fontweight='bold')
                ax_cm.set_title(f"Confusion Matrix: {selected_inspect_model}", fontsize=11, fontweight='bold', pad=15)
                st.pyplot(fig_cm)
                plt.close(fig_cm)

            with diag_c2:
                st.markdown("#### 📑 Classification Report")
                try:
                    rep_dict = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
                    rep_df = pd.DataFrame(rep_dict).T
                    st.dataframe(rep_df.style.format("{:.3f}"), use_container_width=True)
                except Exception as e:
                    st.write(f"Classification Report: {e}")

            # Feature Importance / Coefficients if available
            st.markdown("#### 🌟 Feature Importance / Coefficients")
            has_feat_imp = False
            feat_imp_df = pd.DataFrame()
            if hasattr(model_obj, "feature_importances_"):
                feat_imp_df = pd.DataFrame({
                    "Feature": feature_names,
                    "Importance": model_obj.feature_importances_
                }).sort_values(by="Importance", ascending=False).head(15)
                has_feat_imp = True
            elif hasattr(model_obj, "coef_"):
                coef_vals = np.mean(np.abs(model_obj.coef_), axis=0) if model_obj.coef_.ndim > 1 else np.abs(model_obj.coef_)
                feat_imp_df = pd.DataFrame({
                    "Feature": feature_names,
                    "Importance": coef_vals
                }).sort_values(by="Importance", ascending=False).head(15)
                has_feat_imp = True

            if has_feat_imp and not feat_imp_df.empty:
                fig_imp, ax_imp = plt.subplots(figsize=(9, 4.5))
                ax_imp.barh(feat_imp_df["Feature"][::-1], feat_imp_df["Importance"][::-1], color='#3B82F6')
                ax_imp.set_xlabel("Relative Importance / Magnitude", fontweight='bold')
                ax_imp.set_title(f"Top Feature Drivers ({selected_inspect_model})", fontsize=12, fontweight='bold')
                ax_imp.grid(True, linestyle='--', alpha=0.3, axis='x')
                st.pyplot(fig_imp)
                plt.close(fig_imp)
            else:
                st.info("Feature importance is not directly exposed by this model architecture.")

        else:
            # Regression Diagnostics
            reg_c1, reg_c2 = st.columns(2)
            with reg_c1:
                st.markdown("#### 📈 Actual vs Predicted Values")
                fig_reg, ax_reg = plt.subplots(figsize=(6, 4.5))
                ax_reg.scatter(y_true, y_pred, color='#2563EB', alpha=0.6, edgecolors='none', s=40)
                # 45-degree reference line
                min_val = min(min(y_true), min(y_pred))
                max_val = max(max(y_true), max(y_pred))
                ax_reg.plot([min_val, max_val], [min_val, max_val], color='#DC2626', linestyle='--', linewidth=2, label='Perfect Fit')
                ax_reg.set_xlabel("Actual Values", fontweight='bold')
                ax_reg.set_ylabel("Predicted Values", fontweight='bold')
                ax_reg.set_title(f"Actual vs Predicted ({selected_inspect_model})", fontsize=11, fontweight='bold')
                ax_reg.legend()
                ax_reg.grid(True, linestyle='--', alpha=0.3)
                st.pyplot(fig_reg)
                plt.close(fig_reg)

            with reg_c2:
                st.markdown("#### 📉 Residuals Distribution")
                residuals = np.array(y_true) - np.array(y_pred)
                fig_res, ax_res = plt.subplots(figsize=(6, 4.5))
                ax_res.hist(residuals, bins=25, color='#8B5CF6', edgecolor='black', alpha=0.7)
                ax_res.axvline(0, color='red', linestyle='--', linewidth=2)
                ax_res.set_xlabel("Residual (Actual - Predicted)", fontweight='bold')
                ax_res.set_ylabel("Count")
                ax_res.set_title(f"Residuals Histogram ({selected_inspect_model})", fontsize=11, fontweight='bold')
                ax_res.grid(True, linestyle='--', alpha=0.3)
                st.pyplot(fig_res)
                plt.close(fig_res)


# ==========================================
# TAB 5: CLUSTERING (UNSUPERVISED)
# ==========================================
with tab_cluster:
    st.subheader("🧬 Unsupervised Clustering Studio")
    st.caption("Discover hidden structures, natural groupings, and customer segments with K-Means and Hierarchical Clustering.")

    num_cols_cluster = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(num_cols_cluster) < 2:
        st.warning("Clustering requires at least two numerical columns. Please check your dataset.")
    else:
        cl_f1, cl_f2 = st.columns([3, 1])
        with cl_f1:
            selected_cluster_features = st.multiselect(
                "Select Features for Clustering",
                num_cols_cluster,
                default=num_cols_cluster[:min(5, len(num_cols_cluster))]
            )
        with cl_f2:
            auto_scale = st.checkbox("Standardize Features (Recommended)", value=True)

        if not selected_cluster_features:
            st.info("Select features to proceed with clustering.")
        else:
            X_cluster_raw = df[selected_cluster_features].dropna()
            if len(X_cluster_raw) < 10:
                st.error("Insufficient samples for clustering after dropping NaNs.")
                st.stop()

            scaler = StandardScaler()
            X_cluster = scaler.fit_transform(X_cluster_raw) if auto_scale else X_cluster_raw.values

            cluster_algo = st.radio("Clustering Algorithm", ["K-Means Clustering", "Hierarchical (Agglomerative) Clustering"], horizontal=True)

            if cluster_algo == "K-Means Clustering":
                k_c1, k_c2 = st.columns([1, 2])
                with k_c1:
                    k_clusters = st.slider("Number of Clusters (K)", min_value=2, max_value=10, value=3)
                    calc_elbow = st.checkbox("Compute Elbow & Silhouette Curve (K=2 to 8)", value=True)

                if calc_elbow:
                    with st.spinner("Calculating Elbow & Silhouette metrics..."):
                        inertias = []
                        silhouettes = []
                        k_range = range(2, min(9, len(X_cluster)))
                        for k in k_range:
                            km_test = KMeans(n_clusters=k, random_state=42, n_init=10)
                            km_test.fit(X_cluster)
                            inertias.append(km_test.inertia_)
                            silhouettes.append(silhouette_score(X_cluster, km_test.labels_))

                        fig_elbow, (ax_e1, ax_e2) = plt.subplots(1, 2, figsize=(10, 3.8))
                        ax_e1.plot(list(k_range), inertias, marker='o', color='#2563EB', linewidth=2)
                        ax_e1.set_title("Elbow Method (Inertia)", fontweight='bold')
                        ax_e1.set_xlabel("Number of Clusters (K)")
                        ax_e1.set_ylabel("Inertia")
                        ax_e1.grid(True, linestyle='--', alpha=0.3)

                        ax_e2.plot(list(k_range), silhouettes, marker='s', color='#10B981', linewidth=2)
                        ax_e2.set_title("Silhouette Score Curve", fontweight='bold')
                        ax_e2.set_xlabel("Number of Clusters (K)")
                        ax_e2.set_ylabel("Silhouette Score")
                        ax_e2.grid(True, linestyle='--', alpha=0.3)
                        st.pyplot(fig_elbow)
                        plt.close(fig_elbow)

                # Fit Final KMeans
                kmeans_final = KMeans(n_clusters=k_clusters, random_state=42, n_init=10)
                cluster_labels = kmeans_final.fit_predict(X_cluster)
                sil_final = silhouette_score(X_cluster, cluster_labels)
                db_final = davies_bouldin_score(X_cluster, cluster_labels)

                st.markdown(f"**Silhouette Score:** `{sil_final:.4f}` | **Davies-Bouldin Index:** `{db_final:.4f}`")

                # PCA 2D Cluster Visualization
                pca = PCA(n_components=2)
                pca_coords = pca.fit_transform(X_cluster)
                
                fig_pca, ax_pca = plt.subplots(figsize=(8, 4.5))
                scatter = ax_pca.scatter(pca_coords[:, 0], pca_coords[:, 1], c=cluster_labels, cmap='tab10', alpha=0.7, s=45)
                # Plot PCA Centroids
                centroids_pca = pca.transform(kmeans_final.cluster_centers_)
                ax_pca.scatter(centroids_pca[:, 0], centroids_pca[:, 1], marker='X', s=200, color='red', edgecolor='black', label='Centroids')
                ax_pca.set_title(f"K-Means 2D PCA Cluster Scatter (K={k_clusters})", fontsize=12, fontweight='bold')
                ax_pca.set_xlabel(f"PCA 1 ({pca.explained_variance_ratio_[0]*100:.1f}% var)")
                ax_pca.set_ylabel(f"PCA 2 ({pca.explained_variance_ratio_[1]*100:.1f}% var)")
                ax_pca.legend()
                ax_pca.grid(True, linestyle='--', alpha=0.3)
                st.pyplot(fig_pca)
                plt.close(fig_pca)

                # Cluster Profile Summary Table
                st.markdown("#### 📋 Cluster Profile Summary (Mean per Feature)")
                clustered_df = X_cluster_raw.copy()
                clustered_df["Cluster"] = cluster_labels
                st.dataframe(clustered_df.groupby("Cluster").mean().style.format("{:.3f}"), use_container_width=True)

            else:
                # Hierarchical Clustering
                h_c1, h_c2 = st.columns([1, 2])
                with h_c1:
                    h_clusters = st.slider("Number of Clusters", min_value=2, max_value=8, value=3)
                    linkage_method = st.selectbox("Linkage Method", ["ward", "complete", "average", "single"])

                if SCIPY_AVAILABLE:
                    st.markdown("#### 🌳 Hierarchical Dendrogram")
                    # Sample down if large for dendrogram clarity
                    max_dendro_samples = min(150, len(X_cluster))
                    sample_indices = np.random.RandomState(42).choice(len(X_cluster), max_dendro_samples, replace=False)
                    X_dendro = X_cluster[sample_indices]

                    linked = linkage(X_dendro, method=linkage_method)
                    fig_dendro, ax_dendro = plt.subplots(figsize=(10, 4.5))
                    dendrogram(linked, orientation='top', distance_sort='descending', show_leaf_counts=True, ax=ax_dendro)
                    ax_dendro.set_title(f"Hierarchical Dendrogram ({linkage_method.capitalize()} Linkage, N={max_dendro_samples})", fontsize=12, fontweight='bold')
                    ax_dendro.set_xlabel("Sample Index")
                    ax_dendro.set_ylabel("Distance")
                    st.pyplot(fig_dendro)
                    plt.close(fig_dendro)

                # Fit Agglomerative Clustering
                agg = AgglomerativeClustering(n_clusters=h_clusters, linkage=linkage_method)
                agg_labels = agg.fit_predict(X_cluster)
                sil_agg = silhouette_score(X_cluster, agg_labels)
                st.markdown(f"**Hierarchical Silhouette Score:** `{sil_agg:.4f}`")

                # 2D PCA plot
                pca = PCA(n_components=2)
                pca_coords = pca.fit_transform(X_cluster)
                fig_pca_h, ax_pca_h = plt.subplots(figsize=(8, 4.5))
                ax_pca_h.scatter(pca_coords[:, 0], pca_coords[:, 1], c=agg_labels, cmap='Set2', alpha=0.7, s=45)
                ax_pca_h.set_title(f"Hierarchical Clusters (PCA Projection, K={h_clusters})", fontsize=12, fontweight='bold')
                ax_pca_h.grid(True, linestyle='--', alpha=0.3)
                st.pyplot(fig_pca_h)
                plt.close(fig_pca_h)


# ==========================================
# TAB 6: TIME SERIES FORECASTING (ARIMA / SARIMA)
# ==========================================
with tab_timeseries:
    st.subheader("📈 Time Series Forecasting Studio")
    st.caption("Perform stationarity checks (ADF Test), chronological train-test splits, and build ARIMA / SARIMA forecasting models.")

    if not STATSMODELS_AVAILABLE:
        st.warning("`statsmodels` is not installed in the current environment. Please install it (`pip install statsmodels`) to unlock ARIMA and SARIMA forecasting models.")
    else:
        ts_c1, ts_c2 = st.columns(2)
        with ts_c1:
            date_col = st.selectbox("Select Date / Time Column", all_cols)
        with ts_c2:
            num_cols_ts = df.select_dtypes(include=[np.number]).columns.tolist()
            if not num_cols_ts:
                st.error("No numeric series available for time series modeling.")
                st.stop()
            target_ts_col = st.selectbox("Select Metric to Forecast", num_cols_ts)

        # Parse time series
        ts_df = df[[date_col, target_ts_col]].dropna().copy()
        try:
            ts_df[date_col] = pd.to_datetime(ts_df[date_col])
            ts_df = ts_df.sort_values(by=date_col).reset_index(drop=True)
            series = ts_df.set_index(date_col)[target_ts_col]
        except Exception:
            st.warning(f"Could not convert '{date_col}' to datetime. Using sequential order index instead.")
            series = ts_df[target_ts_col].reset_index(drop=True)

        st.markdown("---")

        # 1. Stationarity Check (Augmented Dickey-Fuller Test)
        st.markdown("#### 1. Stationarity Diagnostic (Augmented Dickey-Fuller Test)")
        try:
            adf_res = adfuller(series.dropna())
            adf_stat = adf_res[0]
            p_value = adf_res[1]
            critical_vals = adf_res[4]

            adf_c1, adf_c2 = st.columns([1, 2])
            with adf_c1:
                st.write(f"**ADF Statistic:** `{adf_stat:.4f}`")
                st.write(f"**p-value:** `{p_value:.4e}`")
                if p_value < 0.05:
                    st.success("✅ Series is **Stationary** (p < 0.05). Differencing d=0 is likely appropriate.")
                else:
                    st.warning("⚠️ Series is **Non-Stationary** (p >= 0.05). Differencing (d=1) is recommended.")
            with adf_c2:
                # Rolling statistics plot
                roll_mean = series.rolling(window=min(12, max(2, len(series)//10))).mean()
                roll_std = series.rolling(window=min(12, max(2, len(series)//10))).std()
                
                fig_roll, ax_roll = plt.subplots(figsize=(7, 3.2))
                ax_roll.plot(series, label='Original', color='#93C5FD', alpha=0.6)
                ax_roll.plot(roll_mean, label='Rolling Mean', color='#2563EB', linewidth=2)
                ax_roll.plot(roll_std, label='Rolling Std', color='#DC2626', linewidth=1.5)
                ax_roll.set_title("Rolling Mean & Standard Deviation", fontsize=11, fontweight='bold')
                ax_roll.legend(fontsize=8)
                ax_roll.grid(True, linestyle='--', alpha=0.3)
                st.pyplot(fig_roll)
                plt.close(fig_roll)
        except Exception as e:
            st.info(f"Stationarity test could not be evaluated: {e}")

        st.markdown("---")

        # 2. Forecasting Setup & Model Selection
        st.markdown("#### 2. Model Configuration: ARIMA & SARIMA")
        ts_model_type = st.radio("Choose Model Architecture", ["ARIMA (Autoregressive Integrated Moving Average)", "SARIMA (Seasonal ARIMA)"], horizontal=True)

        col_p, col_d, col_q = st.columns(3)
        with col_p:
            p_order = st.number_input("p (Autoregressive Order)", min_value=0, max_value=7, value=1)
        with col_d:
            d_order = st.number_input("d (Differencing Degree)", min_value=0, max_value=2, value=1)
        with col_q:
            q_order = st.number_input("q (Moving Average Order)", min_value=0, max_value=7, value=1)

        # Seasonal inputs
        P_seas, D_seas, Q_seas, s_period = 0, 0, 0, 12
        if "SARIMA" in ts_model_type:
            st.markdown("##### Seasonal Parameters (P, D, Q, s)")
            col_sp, col_sd, col_sq, col_ss = st.columns(4)
            with col_sp:
                P_seas = st.number_input("P (Seasonal AR)", min_value=0, max_value=3, value=1)
            with col_sd:
                D_seas = st.number_input("D (Seasonal Diff)", min_value=0, max_value=2, value=1)
            with col_sq:
                Q_seas = st.number_input("Q (Seasonal MA)", min_value=0, max_value=3, value=1)
            with col_ss:
                s_period = st.number_input("s (Seasonal Period)", min_value=2, max_value=52, value=12)

        ts_test_ratio = st.slider("Time Series Holdout Test Size (%)", min_value=5, max_value=35, value=15)
        forecast_horizon = st.slider("Out-of-sample Future Forecast Periods", min_value=1, max_value=60, value=12)

        if st.button("🚀 Fit Time Series Model & Forecast", type="primary"):
            with st.spinner("Fitting time series model..."):
                try:
                    split_idx = int(len(series) * (1 - ts_test_ratio / 100))
                    train_series = series.iloc[:split_idx]
                    test_series = series.iloc[split_idx:]

                    if "SARIMA" in ts_model_type:
                        model_ts = SARIMAX(
                            train_series,
                            order=(p_order, d_order, q_order),
                            seasonal_order=(P_seas, D_seas, Q_seas, s_period),
                            enforce_stationarity=False,
                            enforce_invertibility=False
                        )
                    else:
                        model_ts = ARIMA(
                            train_series,
                            order=(p_order, d_order, q_order),
                            enforce_stationarity=False,
                            enforce_invertibility=False
                        )

                    fit_res = model_ts.fit()

                    # Test set prediction
                    test_pred = fit_res.predict(start=len(train_series), end=len(series)-1)

                    # Performance Metrics
                    mae_ts = mean_absolute_error(test_series, test_pred)
                    rmse_ts = np.sqrt(mean_squared_error(test_series, test_pred))
                    mape_ts = np.mean(np.abs((test_series - test_pred) / np.where(test_series != 0, test_series, 1e-6))) * 100

                    # Future out of sample forecast
                    full_model = SARIMAX(
                        series,
                        order=(p_order, d_order, q_order),
                        seasonal_order=(P_seas, D_seas, Q_seas, s_period) if "SARIMA" in ts_model_type else (0,0,0,0),
                        enforce_stationarity=False,
                        enforce_invertibility=False
                    ) if "SARIMA" in ts_model_type else ARIMA(
                        series,
                        order=(p_order, d_order, q_order),
                        enforce_stationarity=False,
                        enforce_invertibility=False
                    )
                    full_fit = full_model.fit()
                    future_forecast = full_fit.forecast(steps=forecast_horizon)

                    # Display Metrics
                    st.markdown("### 📊 Forecast Evaluation Metrics (Holdout Test Set)")
                    m_c1, m_c2, m_c3, m_c4 = st.columns(4)
                    with m_c1:
                        st.metric("Test RMSE", f"{rmse_ts:.3f}")
                    with m_c2:
                        st.metric("Test MAE", f"{mae_ts:.3f}")
                    with m_c3:
                        st.metric("Test MAPE", f"{mape_ts:.2f}%")
                    with m_c4:
                        st.metric("AIC Score", f"{fit_res.aic:.1f}")

                    # Plot Results
                    fig_fc, ax_fc = plt.subplots(figsize=(10, 4.8))
                    ax_fc.plot(train_series.index if hasattr(train_series, 'index') else range(len(train_series)),
                               train_series.values, label='Historical Train', color='#1E40AF', linewidth=1.8)
                    
                    test_idx = test_series.index if hasattr(test_series, 'index') else range(len(train_series), len(series))
                    ax_fc.plot(test_idx, test_series.values, label='Actual Test', color='#059669', linewidth=2)
                    ax_fc.plot(test_idx, test_pred.values if hasattr(test_pred, 'values') else test_pred,
                               label='Model Prediction', color='#DC2626', linestyle='--', linewidth=2)

                    # Future forecast plot
                    if isinstance(series.index, pd.DatetimeIndex):
                        freq = pd.infer_freq(series.index) or 'MS'
                        future_idx = pd.date_range(start=series.index[-1], periods=forecast_horizon+1, freq=freq)[1:]
                    else:
                        future_idx = range(len(series), len(series) + forecast_horizon)

                    ax_fc.plot(future_idx, future_forecast, label=f'Future Forecast (+{forecast_horizon})',
                               color='#7C3AED', marker='o', markersize=4, linestyle=':', linewidth=2)

                    ax_fc.set_title(f"{ts_model_type.split(' ')[0]} Forecast vs Actual", fontsize=13, fontweight='bold')
                    ax_fc.set_xlabel("Time / Index")
                    ax_fc.set_ylabel(target_ts_col)
                    ax_fc.legend()
                    ax_fc.grid(True, linestyle='--', alpha=0.3)
                    st.pyplot(fig_fc)
                    plt.close(fig_fc)

                    # Forecast Table
                    st.markdown("#### 🔮 Out-of-Sample Future Projections")
                    future_df = pd.DataFrame({
                        "Horizon Period": [f"t+{i+1}" for i in range(forecast_horizon)],
                        "Predicted Value": np.round(future_forecast.values if hasattr(future_forecast, 'values') else future_forecast, 3)
                    })
                    st.dataframe(future_df.T, use_container_width=True)

                except Exception as ex:
                    st.error(f"Time series model fitting encountered an issue: {ex}")
                    st.info("Tip: Try adjusting the (p, d, q) orders or check for irregular date intervals.")

