# Clinical Insights Dashboard

A simple, self-contained analytics dashboard for hospital / clinical
operations data — patient volumes, length of stay, readmission rates,
treatment cost, and satisfaction — built with **Python, Pandas, Plotly,
and Streamlit**.

> All data is **synthetically generated**. No real patient records or
> PHI are used anywhere in this project.

## Features

- KPI summary cards (patient count, avg length of stay, readmission
  rate, avg satisfaction, total cost)
- Patient volume by department
- Top diagnoses
- Admissions trend over time
- Readmission rate by department
- Length-of-stay distribution
- Cost vs. length-of-stay correlation
- Sidebar filters: date range, department, age group, insurance type
- Upload your own CSV, or use the bundled synthetic sample dataset

## Project structure

```
clinical_insights_dashboard/
├── app.py              # Streamlit dashboard (main entry point)
├── data_generator.py   # Generates synthetic sample_data.csv
├── sample_data.csv     # Pre-generated synthetic dataset (1200 records)
├── requirements.txt
└── README.md
```

## Getting started

1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Regenerate the sample dataset:
   ```bash
   python data_generator.py
   ```

4. Run the dashboard:
   ```bash
   streamlit run app.py
   ```

5. Open the local URL Streamlit prints (usually `http://localhost:8501`).

## Using your own data

Upload a CSV via the sidebar. It must include these columns:

| Column | Type | Description |
|---|---|---|
| patient_id | string | Unique patient identifier |
| age | int | Patient age |
| gender | string | Patient gender |
| department | string | Hospital department |
| diagnosis | string | Diagnosis / condition |
| admit_date | date | Admission date (YYYY-MM-DD) |
| discharge_date | date | Discharge date (YYYY-MM-DD) |
| length_of_stay_days | int | Days admitted |
| readmitted_30d | 0/1 | Readmitted within 30 days |
| insurance_type | string | Payer type |
| satisfaction_score | int (1-5) | Patient satisfaction |
| treatment_cost_usd | float | Total treatment cost |

## Extending this project

- Swap the CSV source for a real data warehouse (BigQuery, Snowflake,
  Postgres) behind the same `load_data()` function.
- Add predictive models (e.g., readmission risk scoring) with
  scikit-learn and surface predictions as a new tab.
- Add authentication (`streamlit-authenticator`) before deploying
  externally, since clinical data is sensitive even when de-identified.
- Deploy to Streamlit Community Cloud, or containerize with Docker for
  internal hosting.

## Notes on privacy

This project is a **template/demo**. If you connect it to real patient
data, ensure compliance with applicable regulations (e.g., HIPAA, GDPR)
— including de-identification, access controls, and audit logging —
before using it beyond a local sandbox.
