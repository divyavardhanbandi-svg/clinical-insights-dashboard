"""
data_generator.py
------------------
Generates a synthetic clinical dataset for the Clinical Insights Dashboard.
No real patient data is used — everything here is randomly generated
purely for demo / portfolio purposes.

Run: python data_generator.py
Output: sample_data.csv
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

random.seed(42)
np.random.seed(42)

NUM_RECORDS = 1200

DEPARTMENTS = ["Cardiology", "Orthopedics", "Neurology", "Pediatrics",
               "Oncology", "General Medicine", "Emergency"]

DIAGNOSES = {
    "Cardiology": ["Hypertension", "Arrhythmia", "Coronary Artery Disease"],
    "Orthopedics": ["Fracture", "Osteoarthritis", "Sports Injury"],
    "Neurology": ["Migraine", "Epilepsy", "Stroke"],
    "Pediatrics": ["Asthma", "Ear Infection", "Flu"],
    "Oncology": ["Breast Cancer", "Lung Cancer", "Leukemia"],
    "General Medicine": ["Diabetes", "Infection", "Routine Checkup"],
    "Emergency": ["Trauma", "Chest Pain", "Allergic Reaction"],
}

GENDERS = ["Male", "Female", "Other"]
INSURANCE = ["Private", "Government", "Self-Pay", "Uninsured"]


def random_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=random_seconds)


def generate_dataset(n=NUM_RECORDS) -> pd.DataFrame:
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 12, 31)

    rows = []
    for i in range(1, n + 1):
        dept = random.choice(DEPARTMENTS)
        diagnosis = random.choice(DIAGNOSES[dept])
        admit_date = random_date(start_date, end_date)
        length_of_stay = max(1, int(np.random.exponential(scale=3.5)))
        discharge_date = admit_date + timedelta(days=length_of_stay)
        age = int(np.clip(np.random.normal(loc=48, scale=18), 1, 95))
        readmitted = np.random.choice([0, 1], p=[0.85, 0.15])
        satisfaction = int(np.clip(np.random.normal(loc=4.0, scale=0.8), 1, 5))
        cost = round(length_of_stay * np.random.uniform(800, 2500), 2)

        rows.append({
            "patient_id": f"P{i:05d}",
            "age": age,
            "gender": random.choice(GENDERS),
            "department": dept,
            "diagnosis": diagnosis,
            "admit_date": admit_date.date().isoformat(),
            "discharge_date": discharge_date.date().isoformat(),
            "length_of_stay_days": length_of_stay,
            "readmitted_30d": readmitted,
            "insurance_type": random.choice(INSURANCE),
            "satisfaction_score": satisfaction,
            "treatment_cost_usd": cost,
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = generate_dataset()
    df.to_csv("sample_data.csv", index=False)
    print(f"Generated {len(df)} synthetic patient records -> sample_data.csv")
