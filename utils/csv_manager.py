"""
CSV management, data handling, file operations, pandas, csv module
"""

import os
import pandas as pd
from utils.normalizer import normalise_dataframe

# Βρίσκει το path του φακέλου του project και μεσω της os.path.join μπαινει στον φάκελο data να βαλει το csv
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE = os.path.join(BASE_DIR, "data", "courses_1115493.csv")

#οι στήλες του DataFrame
COLUMNS = [
    "Course Title", "Provider / University", "Category",
    "Difficulty Level", "Cost", "Duration", "Teaching Language"
]

def save_to_csv(df: pd.DataFrame, filepath: str = CSV_FILE):
   
   #σε καθε συνάρτηση με df πρέπει να ελέγχουμε αν είναι άδειο 
    if df.empty:
        print("[CSV] No data to save.")
        return

    # Normalization πριν την αποθήκευση, την οποία θα ξανακάνουμε για "διπλό-φιλτράρισμα"
    #περισσοτερες πληροφορίες για την διαδικασία στο αρχείο normalizer.py
    df = normalise_dataframe(df)

    #ελέγχουμε για την ύπαρξη του φακέλου data ώστε να το διαβάσει και να προσθέσει τα νεα δεδομένα
    #αν δεν υπάρχει, τα δεδομένα είναι τα πρώτα και μεταφέρονται όλα στο combined
    if os.path.exists(filepath):
        existing = pd.read_csv(filepath)
        combined = pd.concat([existing, df], ignore_index=True)
    else:
        combined = df

    #αφαίρεση διπλοτύπων βάσει τίτλου μαθήματος και παρόχου
    #σε περίπτωση διπλοτύπου κρατάμε το τελευταίο, το νεότερο δηλαδή
    combined.drop_duplicates(
        subset=["Course Title", "Provider / University"],
        keep="last",
        inplace=True
    )

    #αποθήκευση στο csv με encoding="utf-8-sig" για ελληνικα. ίσως ειναι λίγο αχρείαστο
    #καθώς ψαχνουμε σε site με αγγλικα courses αλλά για παν ενδεχόμενο
    combined.to_csv(filepath, index=False, encoding="utf-8-sig")
    print(f"[CSV] Saved {len(df)} new rows → total {len(combined)} in '{filepath}'")


#πολύ χρήσιμη συνάρτηση για τα γραφήματα και τον recommender
#το σκεπτικό είναι η εύκολη πρόσβαση στα δεδομένα του αρχείου με αφαιρετικότητα
def load_from_csv(filepath: str = CSV_FILE) -> pd.DataFrame:
   #όπως προαναφέραμε, χρειάζεται ο έλεγχος άδειου df για την σωστή εκτέλεση και debugging του προγράμματος
    if not os.path.exists(filepath):
        #αφήνουμε τέτοια μηνύματα σε όλη την έκταση της εφαρμογής για debugging ώστε να κάνουμε track κάθε βημα οτι εκτελείται σωστά
        print(f"[CSV] File '{filepath}' not found.")
        return pd.DataFrame(columns=COLUMNS)

    df = pd.read_csv(filepath, encoding="utf-8-sig")
    print(f"[CSV] Loaded {len(df)} courses from '{filepath}'")
    return df
