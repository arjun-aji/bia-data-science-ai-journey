"""
InsightPilot - Data Loader Module
Handles multi-format dataset loading (CSV, Excel), validation,
encoding detection, and dataset health diagnostics.
"""

from typing import Dict, Any, Tuple, Optional
import io
import pandas as pd


def load_dataset_file(uploaded_file) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Loads an uploaded file (CSV or XLSX) into a pandas DataFrame.
    Gracefully handles empty files, encoding issues, and format mismatches.

    Returns:
        (df, error_message): df is None if loading failed, otherwise error_message is None.
    """
    if uploaded_file is None:
        return None, "No file provided."

    file_name = uploaded_file.name
    lower_name = file_name.lower()

    try:
        # ---------------------------------------------------------
        # CSV Handling with encoding fallbacks
        # ---------------------------------------------------------
        if lower_name.endswith(".csv"):
            try:
                # First attempt: UTF-8
                df = pd.read_csv(uploaded_file)
            except (UnicodeDecodeError, pd.errors.ParserError):
                # Second attempt: Latin-1 fallback for legacy encoded files
                uploaded_file.seek(0)
                try:
                    df = pd.read_csv(uploaded_file, encoding="latin1")
                except Exception as latin_err:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding="cp1252")

        # ---------------------------------------------------------
        # Excel Handling (.xlsx, .xls)
        # ---------------------------------------------------------
        elif lower_name.endswith((".xlsx", ".xls")):
            try:
                df = pd.read_excel(uploaded_file, engine="openpyxl")
            except Exception as excel_err:
                return None, f"Could not read Excel file: {excel_err}. Please ensure the sheet is not corrupted."

        else:
            return None, "Unsupported file format. Please upload a .csv or .xlsx file."

        # ---------------------------------------------------------
        # Validation: Empty dataset check
        # ---------------------------------------------------------
        if df.empty:
            return None, "The uploaded file is empty (contains no data rows)."

        # Ensure all column headers are strings and trimmed of whitespace
        df.columns = [str(col).strip() for col in df.columns]

        # Handle unnamed or duplicate column names
        if df.columns.duplicated().any():
            duplicate_cols = df.columns[df.columns.duplicated()].tolist()
            # Rename duplicates deterministically
            new_cols = []
            seen = {}
            for col in df.columns:
                if col in seen:
                    seen[col] += 1
                    new_cols.append(f"{col}_{seen[col]}")
                else:
                    seen[col] = 0
                    new_cols.append(col)
            df.columns = new_cols

        return df, None

    except pd.errors.EmptyDataError:
        return None, "The uploaded file is completely empty."
    except Exception as general_err:
        return None, f"Error processing file '{file_name}': {general_err}"


def get_dataset_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes comprehensive dataset health diagnostics:
    - Dimensions (rows, columns)
    - Column data types
    - Numeric, Categorical, Datetime columns
    - Missing value counts & percentages
    - Duplicate rows count
    - Memory footprint
    - Head, Tail, and Random Sample views
    """
    if df is None or df.empty:
        return {}

    row_count, col_count = df.shape

    # 1. Column classifications
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category", "string"]).columns.tolist()
    datetime_cols = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()

    # 2. Missing value analytics
    missing_series = df.isnull().sum()
    total_missing = int(missing_series.sum())
    missing_per_col = {
        col: {
            "count": int(missing_series[col]),
            "percentage": round(float((missing_series[col] / row_count) * 100), 2)
        }
        for col in df.columns
        if missing_series[col] > 0
    }

    # 3. Duplicate rows count
    duplicate_rows_count = int(df.duplicated().sum())

    # 4. Memory footprint calculation
    memory_bytes = df.memory_usage(deep=True).sum()
    if memory_bytes < 1024:
        memory_str = f"{memory_bytes} bytes"
    elif memory_bytes < 1024 * 1024:
        memory_str = f"{memory_bytes / 1024:.2f} KB"
    else:
        memory_str = f"{memory_bytes / (1024 * 1024):.2f} MB"

    # 5. Column data types mapping
    dtypes_map = {col: str(dtype) for col, dtype in df.dtypes.items()}

    # 6. Sample views
    sample_size = min(10, row_count)
    head_view = df.head(sample_size)
    tail_view = df.tail(sample_size)
    sample_view = df.sample(sample_size, random_state=42) if row_count > 0 else df

    return {
        "rows": row_count,
        "columns": col_count,
        "column_names": list(df.columns),
        "dtypes": dtypes_map,
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
        "datetime_columns": datetime_cols,
        "total_missing": total_missing,
        "missing_per_column": missing_per_col,
        "duplicate_rows": duplicate_rows_count,
        "memory_usage": memory_str,
        "head": head_view,
        "tail": tail_view,
        "sample": sample_view,
        "numeric_stats": df[numeric_cols].describe() if numeric_cols else None
    }

