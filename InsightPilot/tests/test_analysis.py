"""
InsightPilot - Automated Calculation Unit Tests
Verifies mathematical correctness of all deterministic Pandas operations.
"""

import unittest
import pandas as pd
import numpy as np

from modules.data_analysis import (
    compute_column_metrics,
    compute_grouped_aggregation,
    compute_rankings,
    compute_correlations
)
from modules.data_cleaning import (
    remove_duplicates,
    drop_columns,
    rename_columns,
    handle_missing_values
)
from modules.question_engine import parse_question_intent, execute_question


class TestInsightPilotCalculations(unittest.TestCase):

    def setUp(self):
        # 5-row sample dataset mirroring sample_sales.csv
        self.df = pd.DataFrame({
            "Product": ["Laptop", "Phone", "Laptop", "Tablet", "Phone"],
            "Category": ["Electronics", "Electronics", "Electronics", "Electronics", "Electronics"],
            "Sales": [75000, 25000, 80000, 30000, 28000],
            "Quantity": [3, 5, 4, 2, 6]
        })

    def test_total_sum(self):
        stats = compute_column_metrics(self.df, "Sales")
        expected_total = 75000 + 25000 + 80000 + 30000 + 28000
        self.assertEqual(stats["sum"], expected_total)

    def test_average_mean(self):
        stats = compute_column_metrics(self.df, "Sales")
        expected_mean = (75000 + 25000 + 80000 + 30000 + 28000) / 5
        self.assertEqual(stats["mean"], expected_mean)

    def test_min_and_max(self):
        stats = compute_column_metrics(self.df, "Sales")
        self.assertEqual(stats["min"], 25000)
        self.assertEqual(stats["max"], 80000)

    def test_median(self):
        stats = compute_column_metrics(self.df, "Sales")
        # Sorted sales: [25000, 28000, 30000, 75000, 80000] -> median is 30000
        self.assertEqual(stats["median"], 30000)

    def test_grouped_sum(self):
        grouped = compute_grouped_aggregation(self.df, "Product", "Sales", agg_func="sum")
        # Laptop sum: 75000 + 80000 = 155000
        laptop_row = grouped[grouped["Product"] == "Laptop"]
        self.assertEqual(laptop_row["Sum of Sales"].values[0], 155000)

    def test_top_ranking(self):
        ranking = compute_rankings(self.df, "Product", "Sales", top_n=1)
        self.assertEqual(ranking["best_performer"], "Laptop")
        self.assertEqual(ranking["best_value"], 155000)

    def test_missing_value_imputation(self):
        df_missing = self.df.copy()
        df_missing.loc[0, "Sales"] = np.nan
        # Impute with mean
        cleaned_df, affected = handle_missing_values(df_missing, strategy="fill_mean", column="Sales")
        self.assertEqual(affected, 1)
        self.assertEqual(cleaned_df["Sales"].isnull().sum(), 0)

    def test_duplicate_removal(self):
        df_dups = pd.concat([self.df, self.df.iloc[[0]]], ignore_index=True)
        self.assertEqual(len(df_dups), 6)
        cleaned_df, removed = remove_duplicates(df_dups)
        self.assertEqual(removed, 1)
        self.assertEqual(len(cleaned_df), 5)

    def test_invalid_column_handling(self):
        with self.assertRaises(ValueError):
            compute_column_metrics(self.df, "NonExistentColumn")

    def test_empty_dataframe_handling(self):
        empty_df = pd.DataFrame(columns=["Sales", "Quantity"])
        with self.assertRaises(ValueError):
            compute_column_metrics(empty_df, "Sales")

    def test_question_execution(self):
        res = execute_question(self.df, "What is the total Sales?")
        self.assertTrue(res["has_exact_answer"])
        self.assertIn("Total of Sales", res["answer_text"])
        self.assertIn("238,000.00", res["answer_text"])


if __name__ == "__main__":
    unittest.main()

