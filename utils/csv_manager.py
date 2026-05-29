"""
CSV management, data handling, file operations, pandas, csv module
"""

import os
import pandas as pd
from utils.normalizer import normalise_dataframe

# Βρίσκει το path του φακέλου του project και μεσω της os.path.join μπαινει στον φάκελο data να βαλει το csv
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE = os.path.join(BASE_DIR, "data", "courses_1115493.csv")

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
