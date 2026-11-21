"""
InsightPilot - Intelligent Question Engine
Translates natural language questions into structured analytical intents,
executes verified Pandas calculations (without eval or exec),
and prepares verified numeric contexts for LLM explanation in English or Malayalam.
"""

from typing import Dict, Any, Optional, List, Tuple
import re
import pandas as pd
from modules.data_analysis import (
    get_numeric_columns,
    get_categorical_columns,
    compute_column_metrics,
    compute_category_metrics,
    compute_grouped_aggregation,
    compute_rankings,
    compute_correlations
)


def _find_matching_column(text: str, columns: List[str]) -> Optional[str]:
    """Finds the best matching column name mentioned in the text."""
    text_lower = text.lower()
    for col in columns:
        if str(col).lower() in text_lower:
            return col
    for col in columns:
        col_lower = str(col).lower()
        if col_lower.rstrip("s") in text_lower or (col_lower + "s") in text_lower:
            return col
    return None


def parse_question_intent(question: str, df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyzes user question and extracts analytical intent, columns, and operations.
    Supports English, Malayalam, and Manglish terms.
    """
    q = question.lower().strip()
    num_cols = get_numeric_columns(df)
    cat_cols = get_categorical_columns(df)

    # 1. DATASET-LEVEL INTENTS (English + Malayalam terms)
    if any(p in q for p in ["how many rows", "row count", "total rows", "number of rows", "വരികൾ", "എത്ര വരി"]):
        return {"intent": "dataset_info", "info_type": "rows", "chart_suggested": False}

    if any(p in q for p in ["how many columns", "column count", "total columns", "number of columns", "നിരകൾ", "എത്ര കോളം"]):
        return {"intent": "dataset_info", "info_type": "columns", "chart_suggested": False}

    if any(p in q for p in ["missing value", "missing values", "null count", "null values", "വിട്ടുപോയ", "നഷ്ടപ്പെട്ട"]):
        return {"intent": "dataset_info", "info_type": "missing", "chart_suggested": False}

    if any(p in q for p in ["duplicate row", "duplicate rows", "duplicates", "ഡ്യൂപ്ലിക്കേറ്റ്"]):
        return {"intent": "dataset_info", "info_type": "duplicates", "chart_suggested": False}

    if any(p in q for p in ["what are the columns", "list columns", "show columns", "column names", "കോളങ്ങൾ"]):
        return {"intent": "dataset_info", "info_type": "column_list", "chart_suggested": False}

    # 2. CORRELATION / RELATIONSHIP
    if any(p in q for p in ["correlation", "relationship between", "correlate", "ബന്ധം"]) and len(num_cols) >= 2:
        return {
            "intent": "correlation",
            "chart_suggested": True,
            "chart_type": "scatter"
        }

    # 3. RANKING (Top N / Bottom N / Highest / Lowest category)
    is_ranking = any(w in q for w in ["top", "bottom", "highest", "best", "lowest", "worst", "rank", "കൂടുതൽ", "കുറവ്", "ഏറ്റവും"])
    if is_ranking and cat_cols and num_cols:
        matched_cat = _find_matching_column(q, cat_cols) or cat_cols[0]
        matched_num = _find_matching_column(q, num_cols) or num_cols[0]

        num_match = re.search(r'\b(?:top|bottom)\s+(\d+)\b', q)
        top_n = int(num_match.group(1)) if num_match else 5

        is_bottom = any(w in q for w in ["bottom", "lowest", "worst", "least", "കുറവ്", "കുറഞ്ഞ"])
        return {
            "intent": "ranking",
            "group_column": matched_cat,
            "target_column": matched_num,
            "top_n": top_n,
            "ascending": is_bottom,
            "chart_suggested": True,
            "chart_type": "bar"
        }

    # 4. GROUP-BY / BREAKDOWN
    if any(w in q for w in ["by", "per", "grouped by", "breakdown by", "തിരിച്ച്"]) and cat_cols and num_cols:
        matched_cat = _find_matching_column(q, cat_cols) or cat_cols[0]
        matched_num = _find_matching_column(q, num_cols) or num_cols[0]

        op = "sum"
        if any(w in q for w in ["average", "mean", "avg", "ശരാശരി"]):
            op = "mean"
        elif any(w in q for w in ["count", "number of", "എണ്ണം"]):
            op = "count"
        elif any(w in q for w in ["max", "maximum", "highest", "കൂടുതൽ"]):
            op = "max"
        elif any(w in q for w in ["min", "minimum", "lowest", "കുറവ്"]):
            op = "min"

        return {
            "intent": "grouping",
            "group_column": matched_cat,
            "target_column": matched_num,
            "operation": op,
            "chart_suggested": True,
            "chart_type": "bar"
        }

    # 5. COLUMN STATISTICAL METRIC
    matched_num = _find_matching_column(q, num_cols)
    if matched_num:
        op = None
        if any(w in q for w in ["median", "മധ്യവില"]):
            op = "median"
        elif any(w in q for w in ["standard deviation", "std", "spread"]):
            op = "std"
        elif any(w in q for w in ["variance"]):
            op = "variance"
        elif any(w in q for w in ["average", "mean", "avg", "ശരാശരി"]):
            op = "mean"
        elif any(w in q for w in ["maximum", "highest", "max", "largest", "കൂടുതൽ", "വലിയ"]):
            op = "max"
        elif any(w in q for w in ["minimum", "lowest", "min", "smallest", "കുറഞ്ഞ", "ചെറിയ"]):
            op = "min"
        elif any(w in q for w in ["total", "sum", "ആകെ"]):
            op = "sum"

        if op:
            return {
                "intent": "column_metric",
                "target_column": matched_num,
                "operation": op,
                "chart_suggested": False
            }

    # 6. GENERAL EXPLANATION -> HANDOFF TO OLLAMA
    return {
        "intent": "general_ai",
        "chart_suggested": False
    }


def execute_question(df: pd.DataFrame, question: str, language: str = "English") -> Dict[str, Any]:
    """
    Executes the parsed question deterministically and formats answers
    in either clear English or Simple Malayalam based on the language setting.
    """
    intent_data = parse_question_intent(question, df)
    intent = intent_data.get("intent")
    is_ml = "malayalam" in language.lower()

    # 1. DATASET INFO
    if intent == "dataset_info":
        info_type = intent_data["info_type"]
        if info_type == "rows":
            ans = f"ഡാറ്റാസെറ്റിലെ ആകെ വരികൾ: {len(df):,}" if is_ml else f"Total rows in dataset: {len(df):,}"
            return {"has_exact_answer": True, "answer_text": ans}
        elif info_type == "columns":
            ans = f"ഡാറ്റാസെറ്റിലെ ആകെ നിരകൾ: {len(df.columns):,}" if is_ml else f"Total columns in dataset: {len(df.columns):,}"
            return {"has_exact_answer": True, "answer_text": ans}
        elif info_type == "missing":
            missing = int(df.isnull().sum().sum())
            ans = f"ആകെ വിട്ടുപോയ മൂല്യങ്ങൾ (Missing Values): {missing:,}" if is_ml else f"Total missing values: {missing:,}"
            return {"has_exact_answer": True, "answer_text": ans}
        elif info_type == "duplicates":
            dup = int(df.duplicated().sum())
            ans = f"ആകെ ഡ്യൂപ്ലിക്കേറ്റ് വരികൾ: {dup:,}" if is_ml else f"Total duplicate rows: {dup:,}"
            return {"has_exact_answer": True, "answer_text": ans}
        elif info_type == "column_list":
            ans = f"കോളങ്ങൾ ({len(df.columns)}): {', '.join(df.columns)}" if is_ml else f"Columns ({len(df.columns)}): {', '.join(df.columns)}"
            return {"has_exact_answer": True, "answer_text": ans}

    # 2. COLUMN METRIC
    elif intent == "column_metric":
        col = intent_data["target_column"]
        op = intent_data["operation"]
        stats = compute_column_metrics(df, col)

        op_labels_en = {
            "sum": ("Total", stats["sum"]),
            "mean": ("Average", stats["mean"]),
            "median": ("Median", stats["median"]),
            "min": ("Minimum", stats["min"]),
            "max": ("Maximum", stats["max"]),
            "std": ("Standard Deviation", stats["std"]),
            "variance": ("Variance", stats["variance"]),
        }
        op_labels_ml = {
            "sum": ("ആകെ തുക (Total)", stats["sum"]),
            "mean": ("ശരാശരി (Average)", stats["mean"]),
            "median": ("മധ്യവില (Median)", stats["median"]),
            "min": ("ഏറ്റവും കുറഞ്ഞത് (Minimum)", stats["min"]),
            "max": ("ഏറ്റവും ഉയർന്നത് (Maximum)", stats["max"]),
            "std": ("സ്റ്റാൻഡേർഡ് ഡീവിയേഷൻ (Std)", stats["std"]),
            "variance": ("വേരിയൻസ് (Variance)", stats["variance"]),
        }

        if is_ml:
            label, val = op_labels_ml.get(op, ("കണക്ക്", stats["mean"]))
            ans = f"{col} - {label}: {val:,.2f}"
        else:
            label, val = op_labels_en.get(op, ("Metric", stats["mean"]))
            ans = f"{label} of {col}: {val:,.2f}"

        return {
            "has_exact_answer": True,
            "answer_text": ans,
            "requires_ai_explanation": True,
            "context_for_ai": {"column": col, "metric": op, "value": val, "all_stats": stats}
        }

    # 3. RANKING
    elif intent == "ranking":
        cat_col = intent_data["group_column"]
        num_col = intent_data["target_column"]
        top_n = intent_data["top_n"]
        is_bottom = intent_data["ascending"]

        ranking_res = compute_rankings(df, cat_col, num_col, top_n=top_n, ascending=is_bottom)
        rank_df = ranking_res["ranking_df"]
        best = ranking_res["best_performer"]
        best_val = ranking_res["best_value"]
        share = ranking_res["share_percentage"]

        if is_ml:
            prefix = "ഏറ്റവും കുറഞ്ഞ" if is_bottom else "ഏറ്റവും മികച്ച"
            ans = (
                f"{num_col} അനുസരിച്ച് {prefix} {top_n} {cat_col}:\n"
                f"• ഒന്നാം സ്ഥാനം: '{best}' — {best_val:,.2f} ({share}% വിഹിതം)"
            )
        else:
            prefix = "Bottom" if is_bottom else "Top"
            ans = (
                f"{prefix} {top_n} {cat_col} by {num_col}:\n"
                f"• Number 1: '{best}' with {best_val:,.2f} ({share}% of subset total)."
            )

        return {
            "has_exact_answer": True,
            "answer_text": ans,
            "computed_data": rank_df,
            "chart_config": {
                "type": "bar",
                "x": cat_col,
                "y": num_col,
                "title": f"{prefix} {top_n} {cat_col} by {num_col}"
            },
            "requires_ai_explanation": True,
            "context_for_ai": {
                "ranking_type": prefix,
                "top_n": top_n,
                "best_performer": best,
                "best_value": best_val,
                "ranking_table": rank_df.to_dict(orient="records")
            }
        }

    # 4. GROUPING
    elif intent == "grouping":
        cat_col = intent_data["group_column"]
        num_col = intent_data["target_column"]
        op = intent_data["operation"]

        grouped_df = compute_grouped_aggregation(df, cat_col, num_col, agg_func=op)
        metric_col = grouped_df.columns[1]
        top_cat = grouped_df.iloc[0][cat_col]
        top_val = grouped_df.iloc[0][metric_col]

        if is_ml:
            ans = (
                f"{cat_col} തിരിച്ചുള്ള {num_col} ({op}):\n"
                f"• ഏറ്റവും കൂടുതൽ: '{top_cat}' — {top_val:,.2f}"
            )
        else:
            ans = (
                f"{op.capitalize()} of {num_col} grouped by {cat_col}:\n"
                f"• Highest: '{top_cat}' with {top_val:,.2f}"
            )

        return {
            "has_exact_answer": True,
            "answer_text": ans,
            "computed_data": grouped_df,
            "chart_config": {
                "type": "bar",
                "x": cat_col,
                "y": metric_col,
                "title": f"{op.capitalize()} of {num_col} by {cat_col}"
            },
            "requires_ai_explanation": True,
            "context_for_ai": {
                "group_column": cat_col,
                "target_column": num_col,
                "operation": op,
                "highest_category": top_cat,
                "highest_value": top_val
            }
        }

    # 5. CORRELATION
    elif intent == "correlation":
        corr_matrix = compute_correlations(df)
        if corr_matrix is not None:
            cols = corr_matrix.columns
            pairs = []
            for i in range(len(cols)):
                for j in range(i + 1, len(cols)):
                    pairs.append((cols[i], cols[j], corr_matrix.loc[cols[i], cols[j]]))
            pairs.sort(key=lambda x: abs(x[2]), reverse=True)
            top_p = pairs[0] if pairs else (cols[0], cols[1], 0.0)

            if is_ml:
                ans = f"'{top_p[0]}', '{top_p[1]}' എന്നിവ തമ്മിലാണ് ഏറ്റവും ശക്തമായ ബന്ധം (Pearson r = {top_p[2]:.3f})."
            else:
                ans = f"Strongest Pearson correlation is between '{top_p[0]}' and '{top_p[1]}' (r = {top_p[2]:.3f})."

            return {
                "has_exact_answer": True,
                "answer_text": ans,
                "computed_data": corr_matrix,
                "requires_ai_explanation": True,
                "context_for_ai": {"strongest_pair": f"{top_p[0]} & {top_p[1]}", "correlation_r": top_p[2]}
            }

    # 6. GENERAL AI INTENT (Ollama takes full question)
    return {
        "has_exact_answer": False,
        "requires_ai_explanation": True,
        "context_for_ai": None
    }


def get_suggested_questions(df: pd.DataFrame, language: str = "English") -> List[str]:
    """Generates dynamic, intelligent questions based on actual dataset columns and language."""
    num_cols = get_numeric_columns(df)
    cat_cols = get_categorical_columns(df)
    is_ml = "malayalam" in language.lower()
    suggestions = []

    if is_ml:
        if num_cols:
            suggestions.append(f"ആകെ {num_cols[0]} എത്രയാണ്?")
            suggestions.append(f"ശരാശരി {num_cols[0]} എത്രയാണ്?")
        if cat_cols and num_cols:
            suggestions.append(f"ഏറ്റവും കൂടുതൽ {num_cols[0]} ഉള്ള {cat_cols[0]} ഏതാണ്?")
            suggestions.append(f"ടോപ്പ് 3 {cat_cols[0]} കാണിക്കുക")
        suggestions.append("ഈ ഡാറ്റാസെറ്റ് വിശദീകരിക്കുക")
    else:
        if num_cols:
            suggestions.append(f"What is the total {num_cols[0]}?")
            suggestions.append(f"What is the average {num_cols[0]}?")
        if cat_cols and num_cols:
            suggestions.append(f"Which {cat_cols[0]} has the highest {num_cols[0]}?")
            suggestions.append(f"What are the top 3 {cat_cols[0]}s by {num_cols[0]}?")
        suggestions.append("Explain this dataset and key insights")

    return suggestions
