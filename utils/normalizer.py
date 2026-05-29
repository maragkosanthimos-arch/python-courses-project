"""
κανονικοποίηση δεδομένων όπως:
-φιλτραρισμα τιτλου και df
-αφαιρεση duplicates
-κανει lowercase
-κανει κανονικοποίηση μονάδων
-invalid urls/courses
-αφαιρεση punctuation
-αφαιρεση αριθμων
-αφαιρεση whitespace
"""

import re
import pandas as pd


#χάρτης κατηγοριών καθώς τα JSON απο τα API και τα Scrapers δεν τα παρέχουν, τα αντλούμε από το πεδιο της κατηγορίας και τον τίτλο
CATEGORY_MAP = {
    "programming":          "Programming",
    "computer science":     "Programming",
    "web development":      "Web Development",
    "data science":         "Data Science",
    "data analytics":       "Data Science",
    "machine learning":     "Data Science",
    "artificial intelligence": "Data Science",
    "ai":                   "Data Science",
    "cybersecurity":        "Cybersecurity",
    "devops":               "DevOps",
    "cloud":                "Cloud Computing",
    "mobile":               "Mobile Development",
    "database":             "Databases",
    "sql":                  "Databases",
    "python":               "Programming",
    "py":                   "Programming",
    "web":                  "Programming",
    "sound engineering":    "Sound Engineering",
    "sound":                "Sound Engineering"
}

#το ίδιο ισχύει για την δυσκολία πολλές φορές, οπότε την αντλούμε επίσης απο τον τίτλο
DIFFICULTY_MAP = {
    "beginner":      "Beginner",
    "introduction":  "Beginner",
    "introductory":  "Beginner",
    "intro":         "Beginner",
    "what is":       "Beginner",
    "basic":         "Beginner",
    "tutorial":      "Beginner",
    "fundamentals":  "Beginner",
    "foundations":   "Beginner",
    "intermediate":  "Intermediate",
    "medium":        "Intermediate",
    "varies":        "Intermediate",
    "mixed":         "Intermediate",
    "complete":      "Intermediate",
    "little experience": "Intermediate",
    "applied":       "Intermediate",
    "practical":     "Intermediate",
    "computational": "Intermediate",
    "specialization": "Intermediate",
    "analyze":        "Intermediate",
    "analysis":       "Intermediate",   
    "advanced":      "Advanced",
    "expert":        "Advanced",
    "deep learning":   "Advanced",
    "professional":  "Advanced",
    "mastering":     "Advanced",
    "full stack":    "Advanced",
    "devops":        "Advanced",
    "all levels":    "All Levels"
}

#λέξεις κλειδιά που θέλουμε και αντίστοιχα δεν θέλουμε να έχει ενα course στον τίτλο του
#έτσι, για να φιλτράρουμε και να συλλέξουμε δεδομένα που μας αφορούνψάχνουμε για κάποιες λέξεις οι οποίες μας δείχνουν ότι το δεομένο που συλλέξαμε είναι εκτός θεματικής της άσκησης
#όλα πάντα βάσει των search terms μας
IRRELEVANT_KEYWORDS = [
    "podcast", "novel", "fiction", "policy",
    "wellness", "seminar", "lecture", "audioexperience"
]

RELEVANT_KEYWORDS = [
    "programming", "python", "java", "javascript", "course",
    "coding", "data", "machine learning", "web", "software","sql"
]

#συνάρτηση που αξιοποιεί τους πίνακες απο πάνω για φροντίσει ότι δεν θα συμπεριληφθούν 
#άσχετες πληροφορίες στο csv
def filter_results(df, *search_term):
    #εφαρμόζουμε lower case στον τίτλο και ψάχνουμε να συμπεριλάβουμε ότι είναι σχετικό 
    #με τους search terms και τα relevant keywords μας
    def is_relevant(title):
        title_lower = title.lower()
        
        if any(word in title_lower for word in IRRELEVANT_KEYWORDS):
            return False
        
        if any(term.lower() in title_lower for term in search_term):
            return True
        
        if any(word in title_lower for word in RELEVANT_KEYWORDS) or any(word in title_lower for word in CATEGORY_MAP):
            return True
        
        return False
    
    return df[df["Course Title"].apply(is_relevant)]

#ακολουθουν συνάρτήσεις κανονικοποίησης κάθε πεδίου

#κανονικοποίηση τίτλου
#δεν καναμε αφαίρεση αριθμών καθώς μπορει να σηματοδοτούν έκδοση ή νουμερο απο σειρά courses
def normalise_course_title(title):
    if not isinstance(title, str) or title.lower() == "nan":
        return "N/A"
    title = title.strip()
    title = re.sub(r"[-_/]", " ", title)    #αντικατάσταση ειδικών χαρακτήρων με κενό
    title = re.sub(r"[^\w\s]", "", title)   #αφαίρεση μη αλφαριθμητικών
    title = re.sub(r"\s+", " ", title)  #συμπίεση κενών
    return title.title()    #κεφαλαία στο πρώτο γράμμα κάθε λέξης
   

#κανονικοποίηση ονόματος παρόχου - πανεπιστημίου
def normalise_provider(provider):
    if not isinstance(provider, str):
        return "N/A"
    provider = provider.strip()
    provider = re.sub(r"\s+", " ", provider)
    provider = re.sub(r"[^\w\s]", "", provider)   
    provider = re.sub(r"\d+", "", provider) #αφαίρεση αριθμών
    return provider.title()
    
#κανονικοποίηση κατηγορίας με ψάξιμο ανάμεσα στον χαρτη κατηγοριών πιο πάνω 
#για σωστό mapping
def normalise_category(category):
    if not isinstance(category,str):
        return "General"
    category=category.strip().lower()
    for key,value in CATEGORY_MAP.items():      
        if key in category:
            return value
    return "General"       #αν δεν βρουμε κατηγορία ούτε από το πεδίο όυτε από τον τίτλο(εξηγω στην normalise_dataframe), έχουμε fallback = General

def normalise_difficulty(difficulty, title="", url=""):
    #αρχικοποιούμε σε all levels
    base = "All Levels"
    if isinstance(difficulty, str) and difficulty.strip():
        lower = difficulty.strip().lower()
        lower1 = title.strip().lower()
        for keyword, normalized in DIFFICULTY_MAP.items():      #mapping δυσκολίας μετά απο ψάξιμο και σε πεδίο δυσκολίας και σε τίτλο για σιγουρία
            if keyword in lower or keyword in lower1:           #αυτό δεν μας τρομάζει για error καθώς αποκλείεται να έχουν conflicting difficulties
                base = normalized
                break

    #advanced δυσκολία πιο ειδικό ψάξιμο για καλύτερο mapping καθώς ειναι πιο σπάνια
    combined = (title + " " + url).lower()
    if any(w in combined for w in ["advanced", "expert", "professional",
                                    "sde", "mastering", "full stack", "devops"]):
        return "Advanced"

    return base     #fallback

def normalise_cost(cost):
    if not isinstance(cost, str):
        return "N/A"
    original = cost.strip()
    lower=original.lower()  #τοπική μεταβλητή για να ψάχνουμε το αυτούσιο κόστος
    #καλύπτουμε όλες τις περιπτώσεις του δωρεάν
    if any(w in lower for w in ["free", "0", "no cost", "gratis", "partially free", "enroll for free"]):
        return "Free"
    
    #εξαγωγή τιμής σε δολάρια
    match = re.search(r"\$(\d+(\.\d+)?)", original)
    if match:
        return match.group()
    
    if any(w in lower for w in ["paid", "subscription", "premium", "fee"]):
        return "Needs Paid Subscription"

    #fallbacks
    if "varies" in lower:
        return "Varies"

    return "N/A"

def normalise_duration(duration):
    if not isinstance(duration, str):
        return "N/A"
    duration = duration.strip().lower()
    
    #αν δεν βρεθει αριθμος στο string, θεωρείται self-paced
    match = re.search(r"(\d+(\.\d+)?)", duration)
    if not match:
        return "Self-paced"

    number = match.group(1)

    # mapping της ώρας 
    if any(w in duration for w in ["hour", "hr"]):
        return f"{number} Hours"
    elif "day" in duration:
        return f"{number} Days"
    elif any(w in duration for w in ["week", "wk"]):
        return f"{number} Weeks"
    elif any(w in duration for w in ["month", "mo"]):
        return f"{number} Months"
    elif any(w in duration for w in ["year", "yr"]):
        return f"{number} Years"
    return "Self-paced"

#κανονικοποίηση γλώσσας
#pretty straigh-forward, αν υπάρχει συντομογραφία κάποιας γλώσσας την καθαρογράφουμε
def normalise_language(language):
    if not isinstance(language, str):
        return "N/A"
    language = language.strip().lower()
    if "english" in language or "en" in language or "eng" in language:
        return "English"
    elif "spanish" in language or "es" in language or "esp" in language:
        return "Spanish"
    elif "french" in language or "fr" in language or "fra" in language:
        return "French"
    return "Unknown"
    

def normalise_dataframe(df):
    if df.empty:
        return df
    #στην συναρτήσεις επεξεργασίας dataframe αποφασίσαμε να μην επεξεργαζόμαστε απευθείας το αρχικό
    #αλλά αντί αυτού να φτιάχνουμε ένα αντίγραφο για ασφάλεια
    #εφαρμόζουμε όλες τις συναρτήσεις αντίστοιχα για να μην τις καλούμε στα άλλα files ξεχωριστά
    df=df.copy()
    df["Course Title"]=df["Course Title"].apply(normalise_course_title)
    df["Provider / University"]=df["Provider / University"].apply(normalise_provider)
    #χρησιμοποιούμε lamda για ευκολα tasks αντί μια ολόκληρη νέα συνάρτηση
    #εφαρμόζουμε normalise_category και ψάχνουμε και στο πεδίο κατηγορία και στον τ´τιλο για καλύτερο mapping
    df["Category"] = df.apply(
        lambda row: normalise_category(
            str(row["Category"] or "") + " " + str(row["Course Title"] or "")
        ), axis=1
    )
    #αντίστοιχα εδώ αντλούμε από τον τίτλο, το πεδίο δυσκολίας και το url
    df["Difficulty Level"] = df.apply(
    lambda row: normalise_difficulty(
        row["Difficulty Level"],
        row["Course Title"],
        row.get("URL", "")
    ),
    axis=1
    )
    df["Cost"]=df["Cost"].apply(normalise_cost)
    df["Duration"]=df["Duration"].apply(normalise_duration)
    df["Teaching Language"]=df["Teaching Language"].apply(normalise_language)
    #ξανα drop duplicates για double-check
    df.drop_duplicates(
        subset=["Course Title", "Provider / University"],
        keep="last",
        inplace=True
    )
    df.reset_index(drop=True, inplace=True)   #επαναρύθμιση index μετά την αφαίρεση
    return df

    