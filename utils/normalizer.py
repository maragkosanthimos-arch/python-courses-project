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
    "advanced":      "Advanced",
    "expert":        "Advanced",
    "professional":  "Advanced",
    "all levels":    "All Levels",
    "varies":        "All Levels",
    "mixed":         "All Levels",
}

def normalise_course_title(title):
    if not isinstance(title, str):
        return "N/A"
    title = title.strip()
    title = re.sub(r"\s+", " ", title)
    title = re.sub(r"[^\w\s]", "", title)   
    title = re.sub(r"\d+", "", title)
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

def normalise_difficulty(difficulty,title=" ",url=" "):
    
    if isinstance(difficulty, str) and difficulty != "N/A":
        lower = difficulty.strip().lower()
        for keyword, normalized in DIFFICULTY_MAP.items():
            if keyword in lower:
                return normalized

    
    combined = (title + " " + url).lower()
    if any(w in combined for w in ["beginner", "intro", "basic", "foundations", "learn-"]):
        return "Beginner"
    elif any(w in combined for w in ["intermediate", "medium"]):
        return "Intermediate"
    elif any(w in combined for w in ["advanced", "expert", "professional", "sde"]):
        return "Advanced"

    return "All Levels"

def normalise_cost(cost):
    if not isinstance(cost, str):
        return "N/A"
    original = cost.strip()
    lower=cost.lower()
    if any(w in lower for w in ["free", "0", "no cost", "gratis", "partially free"]):
        return "Free"
    
    match = re.search(r"(\d+(\.\d+)?)", original)
    if match:
        return match.group()
    
    if any(w in lower for w in ["paid", "subscription", "premium", "fee"]):
        return "Paid"

    if "varies" in lower:
        return "Varies"

    return "N/A"

def normalise_duration(duration):
    if not isinstance(duration, str):
        return "N/A"
    duration = duration.strip().lower()
    if any(w in duration for w in ["hour", "hr", "h"]):
        match = re.search(r"(\d+(\.\d+)?)", duration)
        if match:
            return f"{match.group()} Hours"
    elif any(w in duration for w in ["week", "wk", "w"]):
        match = re.search(r"(\d+(\.\d+)?)", duration)
        if match:
            return f"{match.group()} Weeks"
    elif any(w in duration for w in ["month", "mo", "m"]):
        match = re.search(r"(\d+(\.\d+)?)", duration)
        if match:
            return f"{match.group()} Months"
    elif any(w in duration for w in ["year", "yr", "y"]):
        match = re.search(r"(\d+(\.\d+)?)", duration)
        if match:
            return f"{match.group()} Years"
    return "N/A"

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
    df["Difficulty Level"]=df.apply(lambda row: normalise_difficulty(row["Difficulty Level"], row["Course Title"], row.get("URL", "")), axis=1)
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
    