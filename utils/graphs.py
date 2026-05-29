"""
οπτικοποίηση γραφημάτων, βοηθητικά εργαλεία.
charts,trends,visualization,graphs,plotting,matplotlib
"""

import matplotlib.pyplot as plt
import re
from utils.csv_manager import CSV_FILE, load_from_csv

#συναρτηση που μετατρέπει διάρκεια σε ώρες ώστε να γινει σωστά η σύγκριση μεταξύ ωρών, ημερών, βδομάδων κλπ
#παρόλα αυτά στο γράφημα θα παρουσιάζονται με τις μονάδες τους τις κανονικές. αυτό γινεται μόνο για τη σύγκριση
def convertor_to_hours(duration):
    if not isinstance(duration, str):
        return "None"
    duration = duration.strip().lower()
    #χρησιμοποιείται εσωτερικά για να μετατρέψει διάφορες μορφές διάρκειας σε ώρες για τη συγκριση και την ομαδοποίηση.
    match = re.search(r"(\d+(\.\d+)?)", duration)
    if not match:
        return None
    number = float(match.group(1))
    if "hour" in duration:
        return number
    elif "day" in duration:
        return number * 24
    elif "week" in duration:
        return number * 24 * 7
    elif "month" in duration:
        return number * 24 * 30
    elif "year" in duration:
        return number * 24 * 365
    elif "self" in duration:
        return None
    return None

#μαζεύουμε τους 5 παρόχους με μεγαλύτερη διάρκεια
def get_top_providers(df,top=5):
    if df.empty:
        return []
    df=df.copy()
    df["Hours"]=df["Duration"].apply(convertor_to_hours)
    df=df.dropna(subset=["Hours"])
    df=df.sort_values(by="Hours",ascending=False).head(top)
    return df

#5 μαθήματα με μεγαλύτερη διάρκεια
def bar_chart(top=5):
    df=load_from_csv() 
    top_providers = get_top_providers(df,top)
    if top_providers.empty:
        print("No data to display.")
        return
    fig,ax = plt.subplots(figsize=(10,6))

    positions = range(len(top_providers))
    ax.bar(positions, top_providers["Hours"], color="green")

    #εμφανίζει τους παρόχους στον άξονα x με περιστροφή για καλύτερη ανάγνωση
    ax.set_xticks(positions)
    ax.set_xticklabels(top_providers["Course Title"], rotation=20, ha="right")

    #εμφανίζει παργματικη διάρκεια στον άξονα y
    ax.set_yticks(top_providers["Hours"])
    ax.set_yticklabels(top_providers["Duration"])

    #τιτλος και ετικέτες x και y άξονα αντίστοιχα 
    ax.set_title(f"Top {top} Providers by Course Duration")
    ax.set_xlabel("Course Title")
    ax.set_ylabel("Duration")

    plt.tight_layout()
    plt.show()

#κατανομη μαθηματων βάσει δυσκολίας
#όπως παρατηρείτε αφήνω πολλα debuggers για να βλέπετε τον τρόπο σκέψης μας 
def pie_chart():
    df=load_from_csv()
    print(f"[DEBUG] Loading from: {CSV_FILE}")  # να δούμε ποιο αρχείο φορτώνει
    if df.empty:
        print("No data to display.")
        return
    counts = (df["Difficulty Level"].value_counts())
    
    fig,ax= plt.subplots(figsize=(8,8))
    ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%", startangle=140)
    ax.set_title("Distribution of Difficulty Levels")
    plt.tight_layout()
    plt.show()

#ξαναπαιρνουμε τα 5 μαθήματα με την μεγαλύτερη διάρκεια για να τα συσχετίσουμε με το κόστος να δουμε τη σχέση κόστους-διάρκειας 
def line_plot():
    df=load_from_csv()
    if df.empty:
        print("No data to display.")
        return
    top5=get_top_providers(df,top=5)
    top5=top5.copy()
    #μεσω lamda function μετατρέπουμε το κόστος απο string σε αριθμό για σύγκριση
    #πάντα σε αντίγραφο για να μην πειράξουμε το αρχικό df
    top5["Cost_Num"]=top5["Cost"].apply(lambda cost: 0.0 if cost.lower() == "free" else
                                        float(re.search(r"(\d+(\.\d+)?)", cost).group(1))
                                        if re.search(r"(\d+(\.\d+)?)", cost) else None) 
    fig,ax=plt.subplots(figsize=(10,6))
    ax.plot(top5["Hours"], top5["Cost_Num"], marker="o", linestyle="-", color="blue")
    ax.set_xticks(top5["Hours"])
    ax.set_xticklabels(top5["Duration"], rotation=20, ha="right")
    ax.set_title("Cost Respectively to Duration")
    ax.set_xlabel("Duration")
    ax.set_ylabel("Cost (USD)")
    plt.tight_layout()
    plt.show()