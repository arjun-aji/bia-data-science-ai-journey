
import pandas as pd
from pathlib import Path


# ==========================================
# INSIGHTPILOT - CSV DATA ANALYST
# Stage 2: CSV Data Upload
# ==========================================


# 1. LOAD CSV DATASET
def load_dataset():

    file_path = input(
        "\nEnter CSV file path (default: sample_sales.csv): "
    ).strip()

    if not file_path:
        file_path = "sample_sales.csv"

    try:

        df = pd.read_csv(Path(file_path).expanduser())

        print("\nDataset loaded successfully!")

        return df

    except FileNotFoundError:

        print("\nError: CSV file not found.")

        return None

    except Exception as error:

        print("\nError loading dataset:", error)

        return None


# 2. ANALYSIS ENGINE
def analyze_data(df, question):

    question = question.lower().strip()

    # TOTAL SALES
    if "total sales" in question:

        if "Sales" not in df.columns:
            return "Dataset does not contain a Sales column."

        return f"Total sales: {df['Sales'].sum():,.2f}"

    # AVERAGE SALES
    elif "average sales" in question:

        if "Sales" not in df.columns:
            return "Dataset does not contain a Sales column."

        return f"Average sales: {df['Sales'].mean():,.2f}"

    # HIGHEST REVENUE PRODUCT
    elif (
        "highest revenue" in question
        or "best selling product" in question
    ):

        if not {"Product", "Sales"}.issubset(df.columns):
            return "Dataset needs Product and Sales columns."

        product_sales = df.groupby("Product")["Sales"].sum()

        product = product_sales.idxmax()

        revenue = product_sales.max()

        return f"{product} generated highest revenue: {revenue:,.2f}"

    # HIGHEST QUANTITY
    elif (
        "most units" in question
        or "highest quantity" in question
    ):

        if not {"Product", "Quantity"}.issubset(df.columns):
            return "Dataset needs Product and Quantity columns."

        product_quantity = df.groupby("Product")["Quantity"].sum()

        product = product_quantity.idxmax()

        quantity = product_quantity.max()

        return f"{product} sold the highest quantity: {quantity}"

    # UNKNOWN QUESTION
    else:

        return (
            "Question not supported yet.\n"
            "Try total sales, average sales, highest revenue, "
            "or highest quantity."
        )


# 3. MAIN PROGRAM
def main():

    print("\n" + "=" * 45)

    print("       INSIGHTPILOT DATA ANALYST")

    print("=" * 45)

    # Load dataset
    df = load_dataset()

    if df is None:
        return

    # Display dataset
    print("\nDATASET PREVIEW")

    print(df.head())

    # Dataset information
    print("\nDATASET INFORMATION")

    print("Rows:", len(df))

    print("Columns:", list(df.columns))

    print("\nColumn Data Types")

    print(df.dtypes)

    # Interactive questions
    while True:

        question = input(
            "\nAsk a question (type exit to stop): "
        )

        if question.lower().strip() == "exit":

            print("\nThank you for using InsightPilot!")

            break

        answer = analyze_data(df, question)

        print("\nINSIGHTPILOT:")

        print(answer)


# 4. RUN PROGRAM
if __name__ == "__main__":

    main()
