"""
Recommender system utilities.
Αλγόριθμος: Duration * Difficulty / max(Cost,1)
Όσο μεγαλύτερη διάρκεια έχει, τόσο περισσότερο χρόνο δίνει στον χρήστη να μάθει.
Όσο πιο δύσκολο είναι, τόσο περισσότερο ανταμείβει τον χρήστη και τόσο πιο εξειδικευμένη γνώση του παρέχει.
Όσο μικρότερο το κόστος, τόσο πιο προσιτό είναι για τον χρήστη.
Το max(Cost,1) χρησιμοποιείται για να αποφευχθεί η διαίρεση με το 0 στην περίπτωση του free.
"""

from utils.graphs import convertor_to_hours
from utils.csv_manager import load_from_csv
import re
import pandas as pd

#αντιστοίχιση δυσκολίας σε αριθμητική τιμη για υπολογισμό score
DIFFICULTY_SCORES = {
    "All Levels": 1,
    "Beginner": 1,
    "Intermediate": 2,
    "Advanced": 3
}

#μεταροπή του cost σε αριθμό. αν δωρεάν τότε επιστρέφουμε 0. αυτό θα χρησιμοποιηθεί στο διάβασμα του cost filter που μας επιτρέπει το 0
def convert_cost_to_number(cost):
    if not isinstance(cost, str):
        return 0.0
    if "free" in cost.lower():
        return 0.0
    match = re.search(r"(\d+(\.\d+)?)", cost)
    return float(match.group(1)) if match else 0.0

#εδώ πράτουμε ακριβώς το ίδιο απλώς το δωρεάν μεταφράζεται σε 1 για την διαίρεση στον υπολογισμό του score
def to_cost_score(cost):
    """Για calculate_score — Free = 1.0 για αποφυγή διαίρεσης με 0"""
    if not isinstance(cost, str):
        return 1.0
    if "free" in cost.lower():
        return 1.0
    match = re.search(r"(\d+(\.\d+)?)", cost)
    return float(match.group(1)) if match else 1.0

#υπολογισμός score
def calculate_score(row):
    hours = convertor_to_hours(row["Duration"]) or 0.0
    difficulty = DIFFICULTY_SCORES.get(row["Difficulty Level"],1)
    max_cost = to_cost_score(row["Cost"])
    return (hours * difficulty) / max(max_cost, 1)

#συνάρτηση συστάσεων
def recommend_courses(df=None,Difficulty=None, Category=None, Language=None, max_cost=None, case_sensitive=False):
    #αν δεν δοθεί DataFrame, φορτώνουμε το ήδη υπάρχον
    #αν δεν υπάρχει ούτε αυτό, πετάει κατάλληλο exception
    if df is None:
        df = load_from_csv()
    print(f"[DEBUG] Total: {len(df)}")
    if df.empty:
        print("No courses available for recommendation.")
        return pd.DataFrame()
    
    #φιλτράρισμα βάσει επιπέδου δυσκολίας
    if Difficulty and Difficulty.lower() != "all levels" and Difficulty.lower() != "all":
        filtered = pd.DataFrame
        if case_sensitive:
            filtered = df[df["Difficulty Level"] == Difficulty]
        else:
            filtered = df[df["Difficulty Level"].str.lower() == Difficulty.lower()]
        
        #αν ο χρήστης βάλει κάποικο level που δεν υπάρχει σε κάποια κατηγορία(π.χ. beginner data science)
        #τότε πρετείνει από All Levels που τα περιλαμβάνει όλα
        if filtered.empty:
            print(f"[Recommender] No '{Difficulty}' courses found. Recommending courses for All Levls")
            df = df[df["Difficulty Level"] == "All Levels"]
        else:
            df =  filtered
    #φιλτράρισμα βάσει δυσκολίας και γλώσσας
    if Category and Category.lower() != "all":
        if case_sensitive:
            df = df[df["Category"] == Category]
        else:
            df = df[df["Category"].str.lower() == Category.lower()]

    if Language and Language.lower() != "all":
        if case_sensitive:
            df = df[df["Teaching Language"] == Language]
        else:
            df = df[df["Teaching Language"].str.lower() == Language.lower()]

    #στο κόστος βάζουμε όριο που είμαστε να διαθέσουμε και υπολογίζει με ανώτατο όριο το ποσό που τοποθετήθηκε απο τον χρήστη
    #αν το αφήσει κενό θεωρούμε ότι δεν βάζει άρα το κόστος δεν αποτελεί περιορισμό 
    if max_cost is not None and max_cost>0:
        df = df[df["Cost"].apply(convert_cost_to_number) <= max_cost]
        print(f"[DEBUG] After cost '{max_cost}': {len(df)}")
    elif max_cost is not None and max_cost==0:
        df = df[df["Cost"]=="Free"]

    if df.empty and case_sensitive:
        print("[Recommender] No results found. If you want to search in lower case please enable the 'case-insensitive' option.")
        return pd.DataFrame()
    elif df.empty:
        return pd.DataFrame()
    
    df = df.copy()

    #υπολογισμός score για κάθε μάθημα
    df["Score"] = df.apply(calculate_score,axis=1)

    #ταξινόμηση και επιλογή των 3 καλύτερων
    top3 = df.sort_values("Score", ascending=False).head(3)
    top3=top3[["Course Title", "Provider / University",
                 "Category", "Difficulty Level",
                 "Cost", "Duration", "Teaching Language", "Score"]]
    
    print("[Recommender] Top 3 courses found.")
    return top3