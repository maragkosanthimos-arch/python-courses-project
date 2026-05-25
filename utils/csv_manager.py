"""
CSV management, data handling, file operations, pandas, csv module
"""

import os
import pandas as pd
from utils.normalizer import normalise_dataframe

# Βρίσκει το path του csv σε σχέση με το csv_manager.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE = os.path.join(BASE_DIR, "data", "courses.csv")

COLUMNS = [
    "Course Title", "Provider / University", "Category",
    "Difficulty Level", "Cost", "Duration", "Teaching Language"
]

def save_to_csv(df: pd.DataFrame, filepath: str = CSV_FILE):
   
    if df.empty:
        print("[CSV] No data to save.")
        return

    # Normalization πριν την αποθήκευση
    df = normalise_dataframe(df)

    if os.path.exists(filepath):
        existing = pd.read_csv(filepath)
        combined = pd.concat([existing, df], ignore_index=True)
    else:
        combined = df

    combined.drop_duplicates(
        subset=["Course Title", "Provider / University"],
        keep="last",
        inplace=True
    )

    combined.to_csv(filepath, index=False, encoding="utf-8-sig")
    print(f"[CSV] Saved {len(df)} new rows → total {len(combined)} in '{filepath}'")


def load_from_csv(filepath: str = CSV_FILE) -> pd.DataFrame:
   
    if not os.path.exists(filepath):
        print(f"[CSV] File '{filepath}' not found.")
        return pd.DataFrame(columns=COLUMNS)

    df = pd.read_csv(filepath, encoding="utf-8-sig")
    print(f"[CSV] Loaded {len(df)} courses from '{filepath}'")
    return df

"""
def filter_courses(df: pd.DataFrame, category: str = None,
                   difficulty: str = None, search: str = None) -> pd.DataFrame:
    if df.empty:
        return df

    if category and category != "All":
        df = df[df["Category"] == category]

    if difficulty and difficulty != "All":
        df = df[df["Difficulty Level"] == difficulty]

    if search:
        mask = df["Course Title"].str.contains(search, case=False, na=False)
        df = df[mask]

    return df
"""