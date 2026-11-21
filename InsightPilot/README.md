# 📊 InsightPilot — Local AI Data Analyst

> An intelligent, interactive, privacy-first AI Data Analyst built for Gen AI Hackathons. Powered by **Python, Streamlit, Pandas, and local Ollama (`qwen2.5:3b`)**. Runs 100% locally on your computer with zero external API fees.

---

## 🌟 Key Features

1. **Multi-Format Ingestion & Health Inspection**
   - Seamlessly uploads **CSV** (with UTF-8, Latin-1, CP1252 fallbacks) and **Excel (`.xlsx`, `.xls`)**.
   - Computes instant data health diagnostics: total records, columns, duplicate rows count, missing value breakdown, and memory footprint.
   - Exploratory inspection: Head (first 10 rows), Tail (last 10 rows), Random Sample, and Schema Data Types.

2. **Non-Destructive Interactive Data Cleaning**
   - **Missing Value Imputation**: Drop rows, or fill with Mean, Median, Mode, or Custom Value.
   - **Duplicate Removal**: Identifies and removes duplicate records with a single click.
   - **Column Management**: Selectively drop or rename columns.
   - **Type Casting**: Cast columns to numeric, string, datetime, or boolean.
   - **Reset Safeguard**: A single-click *"🔄 Reset to Original"* button restores raw data at any time.

3. **Two-Tier Question Engine (Zero Math Hallucinations)**
   - **Deterministic Python Execution**: High-precision calculations for totals, averages, medians, standard deviations, variances, top/bottom rankings, and correlations.
   - **Grounded Local LLM Summaries**: Passes the verified numbers to local Ollama (`qwen2.5:3b`) to explain findings in natural language without computing math in the model.
   - **Dynamic Suggestions**: Suggests natural language questions tailored to the columns in the uploaded dataset.

4. **8-Chart Dynamic Visualization Studio**
   - Automatically recommends the best chart type based on data attributes.
   - Supported chart types: **Bar Chart, Horizontal Bar Chart (Ranking), Line Chart (Trend), Scatter Plot (Relationship), Histogram (Distribution), Box Plot, Pie/Donut Chart, and Correlation Heatmap**.
   - Custom axis mapping and aggregation controls.

5. **Multilingual Support (English & Malayalam / മലയാളം)**
   - Supports responses in **English**, **Malayalam (മലയാളം)**, and **Auto-detect**.
   - Includes speech/voice interface integration hooks for macOS Apple Silicon.

6. **Automatic Business Insights & Executive Reports**
   - Generates verified findings across 5 business dimensions: Performance Leaders, Growth Opportunities, Distribution Profiles, Correlation Signals, and Statistical Outlier Alerts (1.5x IQR method).
   - Generates downloadable, printable **HTML Executive Reports**, **Insights CSV**, and **Cleaned Dataset CSV**.

---

## 🏗️ Project Architecture

```
InsightPilot/
│
├── app.py                     # Main Streamlit Dashboard Application
├── requirements.txt           # Python Package Dependencies
├── README.md                  # Project Documentation & Hackathon Pitch
├── sample_sales.csv           # Sample Test Dataset
│
├── modules/
│   ├── __init__.py
│   ├── data_loader.py         # CSV/Excel loading & health diagnostics
│   ├── data_cleaning.py       # Non-destructive data cleaning utilities
│   ├── data_analysis.py       # Verified generic Pandas statistical calculations
│   ├── question_engine.py     # Intent parsing & two-tier question execution
│   ├── llm_engine.py          # Local Ollama connection & multilingual prompt generation
│   ├── chart_engine.py        # 8-chart visual studio with auto-recommendations
│   └── report_engine.py       # Automated insights generator & HTML/CSV report exporter
│
└── tests/
    └── test_analysis.py       # Automated unit tests for calculations
```

---

## 🚀 Getting Started

### 1. Prerequisites
- macOS (Optimized for Apple Silicon M1/M2/M3)
- Python 3.10+
- [Ollama](https://ollama.com/) installed and running locally

### 2. Start Ollama and Pull the Model
In your terminal:
```bash
ollama serve
ollama pull qwen2.5:3b
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the InsightPilot App
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Running Unit Tests
To verify all deterministic mathematical calculations:
```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## 🎤 3-Minute Hackathon Demo Script

1. **The Problem (30 sec)**:
   > *"Modern business teams have spreadsheets everywhere, but extracting insights requires either tedious manual formulas or sending private company data to expensive, cloud-hosted LLMs that frequently hallucinate math."*

2. **The Solution (45 sec)**:
   > *"InsightPilot is an intelligent local AI Data Analyst. It combines the rigorous precision of Python and Pandas for calculations with a local Ollama LLM (`qwen2.5:3b`) for natural language understanding and explanation. Your data never leaves your computer."*

3. **Live Demonstration (75 sec)**:
   - **Upload**: Drop in `sample_sales.csv`. Highlight instant KPI cards and health metrics.
   - **Automated Insights**: Show how InsightPilot automatically identifies that Laptop generated 65% of sales.
   - **Interactive Cleaning**: Demonstrate non-destructive column renaming and duplicate checks.
   - **Ask InsightPilot**: Click a suggested question chip (*"Which Product has the highest Sales?"*). Show the exact calculation, data table, generated chart, and grounded AI explanation.
   - **Multilingual Support**: Switch Response Language to *Malayalam (മലയാളം)* and ask *"Explain this dataset"* to show native Malayalam output.
   - **Executive Export**: Download the one-click HTML Executive Report.

4. **Conclusion (30 sec)**:
   > *"InsightPilot delivers zero-cost, private, verifiable data intelligence for every business user."*

