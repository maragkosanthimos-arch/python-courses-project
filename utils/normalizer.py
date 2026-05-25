"""
κανονικοποίηση δεδομένων όπως:
- Κανονικοποίηση Min-Max
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

CATEGORY_MAP = {
    "programming":          "Programming",
    "online course":        "Programming",
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
    "database":             "Database",
    "education":           "General",
    "podcast":             "General",
}

DIFFICULTY_MAP = {
    "beginner":      "Beginner",
    "introduction":  "Beginner",
    "introductory":  "Beginner",
    "basic":         "Beginner",
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
    "advanced":      "Advanced",
    "expert":        "Advanced",
    "deep learning":   "Advanced",
    "professional":  "Advanced",
    "mastering":     "Advanced",
    "full stack":    "Advanced",
    "devops":        "Advanced",
    "all levels":    "All Levels",
    "varies":        "All Levels",
    "mixed":         "All Levels",
}


IRRELEVANT_KEYWORDS = [
    "podcast", "novel", "fiction", "policy", "marketing",
    "wellness", "seminar", "lecture", "audioexperience"
]

RELEVANT_KEYWORDS = [
    "programming", "python", "java", "javascript", "course",
    "coding", "data", "machine learning", "web", "software"
]

def filter_results(df, *search_term):
    
    def is_relevant(title):
        title_lower = title.lower()
        
        if any(word in title_lower for word in IRRELEVANT_KEYWORDS):
            return False
        
        if any(term.lower() in title_lower for term in search_term):
            return True
        
        if any(word in title_lower for word in RELEVANT_KEYWORDS):
            return True
        
        return False
    
    return df[df["Course Title"].apply(is_relevant)]

def normalise_course_title(title):
    if not isinstance(title, str):
        return "N/A"
    title = title.strip()
    title = re.sub(r"[-_/]", " ", title)
    title = re.sub(r"[^\w\s]", "", title)
    title = re.sub(r"\s+", " ", title)
    return title.title()
   

def normalise_provider(provider):
    if not isinstance(provider, str):
        return "N/A"
    provider = provider.strip()
    provider = re.sub(r"\s+", " ", provider)
    provider = re.sub(r"[^\w\s]", "", provider)   
    provider = re.sub(r"\d+", "", provider)
    return provider.title()
    

def normalise_category(category):
    if not isinstance(category,str):
        return "General"
    category=category.strip().lower()
    for key,value in CATEGORY_MAP.items():
        if key in category:
             return value
    return "General"

def normalise_difficulty(difficulty, title="", url=""):
    # Start from the difficulty field
    base = "All Levels"
    if isinstance(difficulty, str) and difficulty.strip():
        lower = difficulty.strip().lower()
        lower1 = title.strip().lower()
        for keyword, normalized in DIFFICULTY_MAP.items():
            if keyword in lower or keyword in lower1:
                base = normalized
                break

    # Only upgrade to Advanced if title signals it
    combined = (title + " " + url).lower()
    if any(w in combined for w in ["advanced", "expert", "professional",
                                    "sde", "mastering", "full stack", "devops"]):
        return "Advanced"

    return base

def normalise_cost(cost):
    if not isinstance(cost, str):
        return "N/A"
    original = cost.strip()
    lower=original.lower()
    if any(w in lower for w in ["free", "0", "no cost", "gratis", "partially free", "enroll for free"]):
        return "Free"
    
    match = re.search(r"\$(\d+(\.\d+)?)", original)
    if match:
        return match.group()
    
    if any(w in lower for w in ["paid", "subscription", "premium", "fee"]):
        return "Needs Paid Subscription"

    if "varies" in lower:
        return "Varies"

    return "N/A"

def normalise_duration(duration):
    if not isinstance(duration, str):
        return "N/A"
    duration = duration.strip().lower()
    
    match = re.search(r"(\d+(\.\d+)?)", duration)
    if not match:
        return "Self-paced"

    number = match.group(1)

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
    df=df.copy()
    df["Course Title"]=df["Course Title"].apply(normalise_course_title)
    df["Provider / University"]=df["Provider / University"].apply(normalise_provider)
    df["Category"]=df["Category"].apply(normalise_category)
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
    df.drop_duplicates(
        subset=["Course Title", "Provider / University"],
        keep="last",
        inplace=True
    )
    df.reset_index(drop=True, inplace=True)
    return df

    