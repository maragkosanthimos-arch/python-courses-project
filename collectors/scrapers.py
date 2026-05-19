"""
web scraping, data extraction, regex, HTML parsing
"""

import requests
import pandas as pd
import json
import re
from bs4 import BeautifulSoup


SEARCH_TERM_1 = "data science"
SEARCH_TERM_2 = "AI"
SEARCH_TERM_3 = "python"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

COLUMNS = [ "Course Title", "Provider / University", "Category",
            "Difficulty Level", "Cost", "Duration", "Teaching Language" ]

def make_request(url):

    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Request failed with status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return None

def empty_dataframe():
    return pd.DataFrame(columns=COLUMNS)

# =========================================================
#SCRAPER 1 - GeeksForGeeks Courses Page
# =========================================================


def scrape_geeksforgeeks(search_term):

    print(f"[GeeksForGeeks] Scraping for '{search_term}'...")

    url = "https://www.geeksforgeeks.org/courses"
    html = make_request(url)

    if not html:
        print("[GeeksForGeeks] Failed to retrieve data.")
        return empty_dataframe()

    soup = BeautifulSoup(html, "html.parser")

    # Τα δεδομένα είναι μέσα σε JSON-LD script tag
    script_tag = soup.find("script", type="application/ld+json")

    if not script_tag:
        print("[GeeksForGeeks] No JSON data found.")
        return empty_dataframe()

    data = json.loads(script_tag.string)
    courses_raw = data.get("itemListElement", [])

    ready_courses = []

    for item in courses_raw[:20]:
        course = item.get("item", {})

        title    = course.get("name", "N/A")
        provider = course.get("provider", {}).get("name", "GeeksForGeeks")

        # Κόστος
        offers   = course.get("offers", [{}])
        price    = offers[0].get("price", "N/A") if offers else "N/A"
        cost     = f"${price}" if price != "N/A" else "N/A"

        # Διάρκεια — είναι σε ISO format π.χ. "P84D" = 84 days
        instance = course.get("hasCourseInstance", [{}])
        duration_raw = instance[0].get("courseSchedule", {}).get("duration", "N/A") if instance else "N/A"

        # Μετατροπή P84D → "84 days"
        if duration_raw != "N/A" and duration_raw.startswith("P"):
            duration = duration_raw[1:].replace("D", " days").replace("W", " weeks")
        else:
            duration = duration_raw

        if title != "N/A":
            ready_courses.append({
                "Course Title"         : title,
                "Provider / University": provider,
                "Category"             : "Programming",
                "Difficulty Level"     : "N/A",
                "Cost"                 : cost,
                "Duration"             : duration,
                "Teaching Language"    : "English"
            })

    df = pd.DataFrame(ready_courses) if ready_courses else empty_dataframe()
    print(f"[GeeksForGeeks] Status: {'Success' if not df.empty else 'No results'} — {len(df)} courses found")
    return df

#=========================================================
#SCRAPER 2 - COURSERA COURSES PAGE
#=========================================================


def scrape_coursera(search_term="python"):

    print(f"[Coursera] Searching for '{search_term}'...")

    url = f"https://www.coursera.org/search?query={search_term}"

    html = make_request(url)

    if not html:
        print("[Coursera] Failed request")
        return empty_dataframe()

    soup = BeautifulSoup(html, "html.parser")

    scripts = soup.find_all("script")

    data = []

    found_json = False

    for script in scripts:

        text = script.get_text()

        # Ψάχνουμε embedded JSON data
        if "courseName" in text or "courses" in text.lower():

            found_json = True

            # regex extraction titles
            titles = re.findall(r'"name":"(.*?)"', text)

            providers = re.findall(
                r'"partnerNames":\["(.*?)"\]',
                text
            )

            difficulties = re.findall(
                r'"difficultyLevel":"(.*?)"',
                text
            )

            prices = re.findall(r'\$\d+', text)

            for i, title in enumerate(titles[:20]):

                provider = (
                    providers[i]
                    if i < len(providers)
                    else "Coursera"
                )

                difficulty = (
                    difficulties[i]
                    if i < len(difficulties)
                    else "N/A"
                )

                cost = prices[i] if i < len(prices) else "Varies"

                clean_title = re.sub(r'\\u0026', '&', title)

                data.append({
                    "Course Title": clean_title,
                    "Provider / University": provider,
                    "Category": "Online Course",
                    "Difficulty Level": difficulty,
                    "Cost": cost,
                    "Duration": "N/A",
                    "Teaching Language": "English"
                })

            break

    if not found_json:
        print("[Coursera] No embedded JSON found.")

    df = (
        pd.DataFrame(data)
        if data
        else empty_dataframe()
    )

    print(
        f"[Coursera] Status: "
        f"{'Success' if not df.empty else 'No results'}"
    )

    return df


#=========================================================
#SCRAPER 3 = CODECADEMY
#=========================================================

def scrape_codecademy(search_term):

    print(f"[Codecademy] Scraping for '{search_term}'...")

    url = "https://www.codecademy.com/catalog"
    html = make_request(url)

    if not html:
        print("[Codecademy] Failed to retrieve data.")
        return empty_dataframe()

    soup = BeautifulSoup(html, "html.parser")
    script_tag = soup.find("script", type="application/ld+json")

    if not script_tag:
        print("[Codecademy] No JSON data found.")
        return empty_dataframe()

    data = json.loads(script_tag.string)
    courses_raw = data.get("itemListElement", [])

    ready_courses = []

    for course in courses_raw[:20]:

        title    = course.get("name", "N/A")
        provider = course.get("provider", {}).get("name", "Codecademy")

        # Κόστος — "Partially Free", "Subscription", κλπ
        cost = course.get("offers", {}).get("category", "N/A")

        # Διάρκεια — "PT150H" → "150 hours"
        instance = course.get("hasCourseInstance", [{}])
        workload = instance[0].get("courseWorkload", "N/A") if instance else "N/A"
        if workload.startswith("PT") and workload.endswith("H"):
            duration = workload[2:-1] + " hours"
        else:
            duration = workload

        # Φιλτράρισμα βάσει search_term
        description = course.get("description", "").lower()
        if search_term.lower() not in title.lower() and search_term.lower() not in description:
            continue

        ready_courses.append({
            "Course Title"         : title,
            "Provider / University": provider,
            "Category"             : "Programming",
            "Difficulty Level"     : "N/A",
            "Cost"                 : cost,
            "Duration"             : duration,
            "Teaching Language"    : "English"
        })

    df = pd.DataFrame(ready_courses) if ready_courses else empty_dataframe()
    print(f"[Codecademy] Status: {'Success' if not df.empty else 'No results'} — {len(df)} courses found")
    return df

df = scrape_geeksforgeeks(SEARCH_TERM_1)
print(df.head(10).to_string(index=False))

df = scrape_coursera(SEARCH_TERM_2)
print(df.head(10).to_string(index=False))

df = scrape_codecademy(SEARCH_TERM_3)
print(df.head(10).to_string(index=False))

