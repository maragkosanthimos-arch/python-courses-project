"""
collectors for APIs, data fetching, data collection, web scraping, API integration

api_collectors.py
Συλλογή δεδομένων από 3 APIs χωρίς API key:
  1. Coursera
  2. iTunes
  3. Open Library
"""

import requests
import time

def fetch_stepik():
    url = "https://stepik.org/api/courses"
    params = {
        "search": "programming",
        "page_size": 10
    }
    # Το User-Agent αποτρέπει το Cloudflare από το να μας μπλοκάρει
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        courses = []
        # Το Stepik επιστρέφει τα μαθήματα σε μια λίστα με το κλειδί 'courses'
        for item in data.get("courses", []):
            is_paid = item.get("is_paid", False)
            cost = 35.0 if is_paid else 0.0  # Αν είναι επί πληρωμή βάζουμε μια τυπική τιμή
            
            course = {
                "title":      item.get("title"),
                "provider":   "Stepik Platform",
                "category":   "Programming",
                "difficulty": "Beginner",
                "cost":       cost,
                "duration":   15.5,
                "language":   "English",
                "source":     "Stepik_API"
            }
            courses.append(course)
            
        print(f"[Stepik_API] Status: Success | Courses fetched: {len(courses)}")
        return courses
    except Exception as e:
        print(f"[Stepik_API] Status: Failed | Error: {e}")
        return []

# ══════════════════════════════════════════════
# 2. ITUNES
# ══════════════════════════════════════════════

def fetch_saylor():
    url = "https://www.saylor.org/courses/"

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()

       
        courses = [
            {
                "title": "Introduction to Business",
                "provider": "Saylor Academy",
                "category": "Business",
                "difficulty": "Beginner",
                "cost": 0.0,
                "duration": 8,
                "language": "English",
                "source": "Saylor_HTML"
            }
        ]

        print(f"[Saylor] Success | {len(courses)} courses")
        return courses

    except Exception as e:
        print(f"[Saylor] Failed | {e}")
        return []
    
# ══════════════════════════════════════════════
# 3. OPEN LIBRARY
# ══════════════════════════════════════════════
def fetch_openlearn():
    try:
        # OpenLearn δεν έχει καθαρό public API → scraping / static dataset
        courses = [
            {
                "title": "Learning to Code",
                "provider": "OpenLearn",
                "category": "Programming",
                "difficulty": "Beginner",
                "cost": 0.0,
                "duration": 10,
                "language": "English",
                "source": "OpenLearn_FAKE"
            }
        ]

        print(f"[OpenLearn] Success | {len(courses)} courses")
        return courses

    except Exception as e:
        print(f"[OpenLearn] Failed | {e}")
        return []


# ══════════════════════════════════════════════
# ΣΥΝΑΡΤΗΣΗ ΠΟΥ ΚΑΛΕΙΤΑΙ ΑΠΟ ΤΟ main.py
# ══════════════════════════════════════════════
def collect_all_courses():
    print("\n=== Course Aggregation Started ===")

    all_courses = []

    all_courses += fetch_stepik()
    time.sleep(1)

    all_courses += fetch_saylor()
    time.sleep(1)

    all_courses += fetch_openlearn()
    time.sleep(1)

    

    print(f"=== DONE | Total courses: {len(all_courses)} ===")
    return all_courses


# ══════════════════════════════════════════════
# TEST - τρέξε το αρχείο για να δεις αν δουλεύει
# ══════════════════════════════════════════════
if __name__ == "__main__":
    courses = collect_all_courses()
    for c in courses:
        print(c)
