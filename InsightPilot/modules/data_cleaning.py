"""
InsightPilot - Data Cleaning Module
Provides non-destructive data cleaning utilities: duplicate removal,
missing value handling (drop, mean, median, mode, custom fill), column dropping,
renaming, and data type conversions.
"""

from typing import Dict, Any, Tuple, Optional, List
import pandas as pd
import numpy as np


def remove_duplicates(df: pd.DataFrame, subset: Optional[List[str]] = None) -> Tuple[pd.DataFrame, int]:
    """
    Removes duplicate rows without mutating the original dataframe.
    Returns (cleaned_df, count_of_removed_rows).
    """
    initial_count = len(df)
    cleaned_df = df.drop_duplicates(subset=subset, keep="first").reset_index(drop=True)
    removed_count = initial_count - len(cleaned_df)
    return cleaned_df, removed_count


def drop_columns(df: pd.DataFrame, columns_to_drop: List[str]) -> pd.DataFrame:
    """
    Drops the specified columns from the dataframe.
    """
    valid_cols = [c for c in columns_to_drop if c in df.columns]
    return df.drop(columns=valid_cols).copy()


def rename_columns(df: pd.DataFrame, rename_map: Dict[str, str]) -> pd.DataFrame:
    """
    Renames columns according to the provided mapping dictionary.
    """
    clean_map = {k: v.strip() for k, v in rename_map.items() if k in df.columns and v.strip()}
    return df.rename(columns=clean_map).copy()


def handle_missing_values(
    df: pd.DataFrame,
    strategy: str,
    column: Optional[str] = None,
    custom_value: Optional[Any] = None
) -> Tuple[pd.DataFrame, int]:
    """
    Handles missing values according to the selected strategy:
    - 'drop_rows': Drop rows with any missing values (in specific column or across dataset)
    - 'fill_mean': Fill numeric nulls with column mean
    - 'fill_median': Fill numeric nulls with column median
    - 'fill_mode': Fill nulls with column most frequent value (mode)
    - 'fill_custom': Fill nulls with a user-specified custom value

    Returns: (cleaned_df, count_of_affected_cells_or_rows)
    """
    cleaned_df = df.copy()

    if strategy == "drop_rows":
        initial_rows = len(cleaned_df)
        if column and column in cleaned_df.columns:
            cleaned_df = cleaned_df.dropna(subset=[column]).reset_index(drop=True)
        else:
            cleaned_df = cleaned_df.dropna().reset_index(drop=True)
        affected = initial_rows - len(cleaned_df)
        return cleaned_df, affected

    elif strategy == "fill_mean":
        target_cols = [column] if column else cleaned_df.select_dtypes(include="number").columns.tolist()
        affected = 0
        for col in target_cols:
            if col in cleaned_df.columns and pd.api.types.is_numeric_dtype(cleaned_df[col]):
                null_count = int(cleaned_df[col].isnull().sum())
                if null_count > 0:
                    mean_val = cleaned_df[col].mean()
                    cleaned_df[col] = cleaned_df[col].fillna(mean_val)
                    affected += null_count
        return cleaned_df, affected

    elif strategy == "fill_median":
        target_cols = [column] if column else cleaned_df.select_dtypes(include="number").columns.tolist()
        affected = 0
        for col in target_cols:
            if col in cleaned_df.columns and pd.api.types.is_numeric_dtype(cleaned_df[col]):
                null_count = int(cleaned_df[col].isnull().sum())
                if null_count > 0:
                    median_val = cleaned_df[col].median()
                    cleaned_df[col] = cleaned_df[col].fillna(median_val)
                    affected += null_count
        return cleaned_df, affected

    elif strategy == "fill_mode":
        target_cols = [column] if column else cleaned_df.columns.tolist()
        affected = 0
        for col in target_cols:
            if col in cleaned_df.columns:
                null_count = int(cleaned_df[col].isnull().sum())
                if null_count > 0:
                    modes = cleaned_df[col].mode()
                    if not modes.empty:
                        cleaned_df[col] = cleaned_df[col].fillna(modes[0])
                        affected += null_count
        return cleaned_df, affected

    elif strategy == "fill_custom":
        if not column or column not in cleaned_df.columns:
            return cleaned_df, 0

        null_count = int(cleaned_df[column].isnull().sum())
        if null_count > 0:
            # If target column is numeric, attempt numeric type conversion
            val_to_fill = custom_value
            if pd.api.types.is_numeric_dtype(cleaned_df[column]):
                try:
                    val_to_fill = float(custom_value)
                except (ValueError, TypeError):
                    pass
            cleaned_df[column] = cleaned_df[column].fillna(val_to_fill)
            return cleaned_df, null_count
        return cleaned_df, 0

    return cleaned_df, 0


def convert_column_dtype(
    df: pd.DataFrame,
    column: str,
    target_dtype: str
) -> Tuple[pd.DataFrame, Optional[str]]:
    """
    Converts a column's data type safely without altering the original dataframe.
    Supported target_dtypes: 'numeric', 'string', 'datetime', 'boolean'.
    Returns (cleaned_df, error_message).
    """
    if column not in df.columns:
        return df, f"Column '{column}' does not exist."

    cleaned_df = df.copy()
    try:
        if target_dtype == "numeric":
            cleaned_df[column] = pd.to_numeric(cleaned_df[column], errors="coerce")
        elif target_dtype == "string":
            cleaned_df[column] = cleaned_df[column].astype(str)
        elif target_dtype == "datetime":
            cleaned_df[column] = pd.to_datetime(cleaned_df[column], errors="coerce")
        elif target_dtype == "boolean":
            cleaned_df[column] = cleaned_df[column].astype(bool)
        else:
            return df, f"Unsupported data type '{target_dtype}'."
        return cleaned_df, None
    except Exception as err:
        return df, f"Failed to convert '{column}' to {target_dtype}: {err}"

