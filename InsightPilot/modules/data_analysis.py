"""
InsightPilot - Data Analysis Engine
Performs generic, verified, deterministic Pandas calculations across any dataset
without hardcoding column names.
"""

from typing import Dict, Any, Optional, List, Tuple
import pandas as pd
import numpy as np


def get_numeric_columns(df: pd.DataFrame) -> List[str]:
    """Returns list of numeric columns in the DataFrame."""
    return df.select_dtypes(include="number").columns.tolist()


def get_categorical_columns(df: pd.DataFrame) -> List[str]:
    """Returns list of categorical/text columns in the DataFrame."""
    return df.select_dtypes(include=["object", "category", "string"]).columns.tolist()


def compute_column_metrics(df: pd.DataFrame, column: str) -> Dict[str, Any]:
    """
    Computes full numeric statistical profile for a given numeric column:
    Sum, Mean, Median, Min, Max, Standard Deviation, Variance, Count, Quantiles.
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist in the dataset.")

    series = pd.to_numeric(df[column], errors="coerce").dropna()
    if series.empty:
        raise ValueError(f"Column '{column}' contains no numeric data.")

    return {
        "column": column,
        "count": int(series.count()),
        "sum": float(series.sum()),
        "mean": float(series.mean()),
        "median": float(series.median()),
        "min": float(series.min()),
        "max": float(series.max()),
        "std": float(series.std()) if len(series) > 1 else 0.0,
        "variance": float(series.var()) if len(series) > 1 else 0.0,
        "q25": float(series.quantile(0.25)),
        "q75": float(series.quantile(0.75)),
    }


def compute_category_metrics(df: pd.DataFrame, column: str, top_n: int = 10) -> Dict[str, Any]:
    """
    Computes categorical distribution:
    Unique count, value counts, most common, least common, percentage distribution.
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist in the dataset.")

    series = df[column].dropna().astype(str)
    if series.empty:
        raise ValueError(f"Column '{column}' contains no valid data.")

    counts = series.value_counts()
    percentages = (counts / len(series) * 100).round(2)

    top_df = pd.DataFrame({
        column: counts.head(top_n).index,
        "Count": counts.head(top_n).values,
        "Percentage (%)": percentages.head(top_n).values
    })

    return {
        "column": column,
        "total_valid": len(series),
        "unique_count": int(series.nunique()),
        "most_common": str(counts.index[0]),
        "most_common_count": int(counts.iloc[0]),
        "least_common": str(counts.index[-1]),
        "least_common_count": int(counts.iloc[-1]),
        "distribution_table": top_df
    }


def compute_grouped_aggregation(
    df: pd.DataFrame,
    group_column: str,
    target_column: str,
    agg_func: str = "sum"
) -> pd.DataFrame:
    """
    Groups by `group_column` and aggregates `target_column` using `agg_func` (sum, mean, count, min, max).
    Returns clean DataFrame sorted descending by the calculated metric.
    """
    if group_column not in df.columns:
        raise ValueError(f"Group column '{group_column}' does not exist in the dataset.")
    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' does not exist in the dataset.")

    # Validate aggregate function
    agg_map = {
        "sum": "sum",
        "total": "sum",
        "mean": "mean",
        "average": "mean",
        "avg": "mean",
        "count": "count",
        "min": "min",
        "max": "max"
    }
    pandas_func = agg_map.get(agg_func.lower(), "sum")

    # Group and aggregate
    grouped = (
        df.groupby(group_column, as_index=False)[target_column]
        .agg(pandas_func)
    )

    metric_name = f"{pandas_func.capitalize()} of {target_column}"
    grouped.rename(columns={target_column: metric_name}, inplace=True)
    grouped.sort_values(by=metric_name, ascending=False, inplace=True)
    grouped.reset_index(drop=True, inplace=True)

    return grouped


def compute_rankings(
    df: pd.DataFrame,
    category_column: str,
    numeric_column: str,
    top_n: int = 5,
    ascending: bool = False
) -> Dict[str, Any]:
    """
    Computes Top N or Bottom N ranking of categories based on numeric total.
    """
    grouped = (
        df.groupby(category_column, as_index=False)[numeric_column]
        .sum()
        .sort_values(by=numeric_column, ascending=ascending)
        .reset_index(drop=True)
    )

    ranked_subset = grouped.head(top_n)
    total_val = float(df[numeric_column].sum())
    subset_val = float(ranked_subset[numeric_column].sum())
    share_pct = round((subset_val / total_val * 100), 2) if total_val > 0 else 0.0

    return {
        "ranking_df": ranked_subset,
        "category_column": category_column,
        "numeric_column": numeric_column,
        "top_n": top_n,
        "is_bottom": ascending,
        "subset_total": subset_val,
        "dataset_total": total_val,
        "share_percentage": share_pct,
        "best_performer": ranked_subset.iloc[0][category_column] if not ranked_subset.empty else None,
        "best_value": ranked_subset.iloc[0][numeric_column] if not ranked_subset.empty else None
    }


def compute_correlations(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    Calculates pairwise Pearson correlation for all numeric columns.
    Returns correlation matrix DataFrame or None if fewer than 2 numeric columns exist.
    """
    numeric_cols = get_numeric_columns(df)
    if len(numeric_cols) < 2:
        return None

    return df[numeric_cols].corr().round(3)

