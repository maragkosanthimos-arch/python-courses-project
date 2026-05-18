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
def fetch_itunes():
    url = "https://itunes.apple.com/search"
    params = {
        "term":   "programming course",
        "media":  "podcast",
        "limit":  10
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        courses = []
        for item in data["results"]:
            course = {
                "title":      item.get("collectionName"),
                "provider":   item.get("artistName"),
                "category":   item.get("primaryGenreName"),
                "difficulty": "All Levels",
                "cost":       0.0,
                "duration":   None,
                "language":   "English",
                "source":     "iTunes_API"
            }
            courses.append(course)

        print(f"[iTunes_API] Status: Success | Courses fetched: {len(courses)}")
        return courses

    except Exception as e:
        print(f"[iTunes_API] Status: Failed | Error: {e}")
        return []


# ══════════════════════════════════════════════
# 3. OPEN LIBRARY
# ══════════════════════════════════════════════
def fetch_open_library():
    url = "https://openlibrary.org/search.json"
    params = {
        "q":      "programming course",
        "limit":  10,
        "fields": "title,author_name,subject,language"
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        courses = []
        for item in data["docs"]:
            course = {
                "title":      item.get("title"),
                "provider":   "Open Library",
                "category":   "Programming",
                "difficulty": "All Levels",
                "cost":       0.0,
                "duration":   None,
                "language":   "English",
                "source":     "OpenLibrary_API"
            }
            courses.append(course)

        print(f"[OpenLibrary_API] Status: Success | Courses fetched: {len(courses)}")
        return courses

    except Exception as e:
        print(f"[OpenLibrary_API] Status: Failed | Error: {e}")
        return []


# ══════════════════════════════════════════════
# ΣΥΝΑΡΤΗΣΗ ΠΟΥ ΚΑΛΕΙΤΑΙ ΑΠΟ ΤΟ main.py
# ══════════════════════════════════════════════
def collect_all_api_courses():
    print("\n=== API Collection Started ===")

    all_courses = []
    all_courses += fetch_stepik()
    time.sleep(1)
    all_courses += fetch_itunes()
    time.sleep(1)
    all_courses += fetch_open_library()

    print(f"=== API Collection Done | Total: {len(all_courses)} courses ===\n")
    return all_courses


# ══════════════════════════════════════════════
# TEST - τρέξε το αρχείο για να δεις αν δουλεύει
# ══════════════════════════════════════════════
if __name__ == "__main__":
    courses = collect_all_api_courses()
    for c in courses:
        print(c)
