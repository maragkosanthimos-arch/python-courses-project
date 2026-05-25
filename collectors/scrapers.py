
"""
web scraping, data extraction, regex, HTML parsing
"""

import requests     #για να κάνουμε αιτήματα HTTP και να πάρουμε το HTML των σελίδων που θέλουμε να κάνουμε scraping
import pandas as pd     #για να δημιουργήσουμε και να διαχειριστούμε τα dataframes που θα περιέχουν τα δεδομένα των μαθημάτων
import json     #για να κάνουμε parsing των JSON δεδομένων που βρίσκονται μέσα σε script tags
import re       #για να κανουμε καθαρισμό των δεδομένων που θα εξάγουμε από το HTML
from bs4 import BeautifulSoup   #για να κάνουμε parsing του HTML

#οσα site έχουν επιλεχτει ήταν γιατί ήταν απο τα λίγα που δεν φορτώνουν τα δεδομένα τους με JavaScript, οπότε μπορούμε να τα πάρουμε απευθείας από το HTML χωρίς να χρειάζεται να χρησιμοποιήσουμε εργαλεία όπως το Selenium που προσομοιώνουν browser και μπορούν να χειριστούν JavaScript.

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


#συναρτηση για http requests με error handling 
#παρομοια λογικη με την make_request που χρησιμοποιουμε και στα API Collectors
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

#επιστροφη αδειου dataframe σε περιπτωση αποτυχίας
def empty_dataframe():
    return pd.DataFrame(columns=COLUMNS)

# =========================================================
#SCRAPER 1 - GeeksForGeeks Courses Page
# =========================================================


def scrape_geeksforgeeks(search_term):

    print(f"[GeeksForGeeks] Scraping for '{search_term}'...")

    url = "https://www.geeksforgeeks.org/courses"
    html = make_request(url)

    #αν δεν βρει το html της σελίδας επιστρέφει κενό dataframe
    if not html:
        print("[GeeksForGeeks] Failed to retrieve data.")
        return empty_dataframe()

    #ψαχνουμε το script που περιεχει τα δεδομενα σε μορφη json και τα αποθηκευουμε σε μεταβλητη
    soup = BeautifulSoup(html, "html.parser")

    #ψαχνουμε το script tag που περιεχει τα δεδομενα σε μορφη json και τα αποθηκευουμε σε μεταβλητη
    script_tag = soup.find("script", type="application/ld+json")

    if not script_tag:
        print("[GeeksForGeeks] No JSON data found.")
        return empty_dataframe()

    #parsing δεδομενων που βρηαμε και τα πάμε σε μεταβλητη
    data = json.loads(script_tag.string)
    #τα αποτελέσματα αυτά που περιέχουν τα μαθήματα είναι μέσα στο πεδίο "itemListElement" του json, οπότε τα αποθηκεύουμε σε μια μεταβλητη
    courses_raw = data.get("itemListElement", [])


    ready_courses = []

    #τρεχουμε λουπα στα json δεδομενα που βρηκαμε για να τα καθαρισουμε και να τα μετατρεψουμε στη μορφη που θελουμε για το dataframe
    #σε ένα αρχικό στάδιο μόνο καθός εχουμε ξεχωριστο αρχέιο για κανονικοποίηση
    for item in courses_raw[:20]:
        course = item.get("item", {})

        title    = course.get("name", "N/A")
        #ο provider δεν είναι πάντα διαθέσιμος, οπότε χρησιμοποιούμε το όνομα του ιστότοπου ως προεπιλογή
        provider = course.get("provider", {}).get("name", "GeeksForGeeks")
        difficulty = next(
            (course.get(key) for key in ["difficultyLevel", "educationalLevel", "skillLevel", "Experience"]
            if course.get(key)),
            "N/A"
        )


        # για το κόστος ψάχνουμε πεδιο με τίτλο "offers" που μπορεί να περιέχει πληροφορίες για το κόστος, αλλά αν δεν υπάρχει βάζουμε "N/A"
        offers   = course.get("offers", [{}])
        price    = offers[0].get("price", "N/A") if offers else "N/A"
        cost     = f"${price}" if price != "N/A" else "N/A"

        
        instance = course.get("hasCourseInstance", [{}])
        # για τη διάρκεια ψάχνουμε πεδίο με τίτλο "duration" που μπορεί να περιέχει πληροφορίες για τη διάρκεια, αλλά αν δεν υπάρχει βάζουμε "N/A"
        duration_raw = instance[0].get("courseSchedule", {}).get("duration", "N/A") if instance else "N/A"

        # μετατροπή  P84D -> "84 days"
        if duration_raw != "N/A" and duration_raw.startswith("P"):
            duration = duration_raw[1:].replace("D", " days").replace("W", " weeks")
        else:
            duration = duration_raw

        if title != "N/A":
            ready_courses.append({
                "Course Title"         : title,
                "Provider / University": provider,
                "Category"             : "Programming",
                "Difficulty Level"     : difficulty,
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

    #χτιζουμε το url της σελίδας αναζήτησης του Coursera με το search term θελουμε
    url = f"https://www.coursera.org/search?query={search_term}"

    html = make_request(url)

    if not html:
        print("[Coursera] Failed request")
        return empty_dataframe()

    soup = BeautifulSoup(html, "html.parser")

    #βρισκουμε όλα τα script tags της σελίδας 
    scripts = soup.find_all("script")

    data = []

    #flag να ξερουμε αν βρήκαμε script με json δεδομένα
    found_json = False

    for script in scripts:
        text = script.get_text()
        #ψάχνουμε το script που περιέχει τα δεδομένα των μαθημάτων σε μορφή json
        if "courseName" in text or "courses" in text.lower():
            found_json = True

            # εξαγουμε τον τιτλο με regex
            titles = re.findall(r'"name":"(.*?)"', text)

            # εξάγουμε το πρώτο όνομα από το array "partnerNames"
            providers = re.findall(
                r'"partnerNames":\["(.*?)"\]',
                text
            )

            #δοκιμη 3 λέξεων για να βρούμε το πεδίο που περιέχει το επίπεδο δυσκολίας
            difficulties = (
                re.findall(r'"difficultyLevel":"([^"]*)"', text) or
                re.findall(r'"educationalLevel":"([^"]*)"', text) or
                re.findall(r'"skillLevel":"([^"]*)"', text)
            )
            #εξαγωγη τιμων της μορφης $...
            prices = re.findall(r'\$\d+', text)

            for i, title in enumerate(titles[:20]):

                #αν δεν υπαρχει provider, βάζουμε το site
                provider = (
                    providers[i]
                    if i < len(providers)
                    else "Coursera"
                )
                
                #αν δεν βρουμε δυσκολια, βάζουμε "N/A"
                difficulty = (
                    difficulties[i]
                    if i < len(difficulties)
                    else "N/A"
                )

                #αν δεν βρουμε τιμη, βάζουμε "N/A"
                cost = prices[i] if i < len(prices) else "Varies"

                #αντικατάσταση unicode για το & που εμφανιζεται σε πολλους τιτλους μέσω παρατηρήσεων
                clean_title = re.sub(r'\\u0026', '&', title)


                #============================
                #δυστυχως επειδη το coursera φορτωνει δεδομενα με JavaScript dynamically, η requests δεν μπορει να εξαγει σωστά τον πάροχο
                #αυτο θα γινόταν με selenium όμως πιστευω οτι το προγραμμα θα μπλεξει και θα γίνει πολυ πιο αργό
                #η διαδικασία ίδια είναι
                #============================
                data.append({
                    "Course Title": clean_title,
                    "Provider / University": provider,
                    "Category": "Online Course",
                    "Difficulty Level": difficulty,
                    "Cost": cost,
                    "Duration": "N/A",
                    "Teaching Language": "English"
                })

            #βρηκαμε το script με τα δεδομενα, δεν χρειάζεται να συνεχίσουμε να ψάχνουμε
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

    #============================
    #ίδια λογικη με GeeksForGeeks, δηλαδη χρησιμοποιούν JSON-LD
    #============================

    ready_courses = []

    for course in courses_raw[:20]:

        title    = course.get("name", "N/A")
        provider = course.get("provider", {}).get("name", "Codecademy")

        #προσπαθούμε να βρουμε το επιπεδο δυσκολιας από το url
        #αν υποδηλώνει κάτι ο τίτλος
        difficulty = course.get("url", "")
        if "beginner" in difficulty or "introduction" in difficulty or "learn-" in difficulty:
            difficulty = "Beginner"
        elif "intermediate" in difficulty:
            difficulty = "Intermediate"
        else:
            difficulty = "N/A"  
      
        offers = course.get("offers", {})       #για το κόστος ψάχνουμε πεδιο με τίτλο "offers" που μπορεί να περιέχει πληροφορίες για το κόστος
        price    = offers.get("price", None)        #αν υπαρχει συγκεκριμένη τιμή
        currency = offers.get("priceCurrency", "")      #αν υπαρχει νόμισμα, το προσθέτουμε μπροστά από την τιμή, αλλιώς αφήνουμε κενό
        category = offers.get("category", "N/A")

        if price == 0 or price == "0":
            cost = "Free"       #αν η τιμη είναι 0, τυπωνουμε δωρεάν
        elif price:
            cost = f"{currency}{price}"  
        else:
            cost = category

        #κανονικοποίηση διάρκειας απο PT80H -> 80 hours αλλιως return
        instance = course.get("hasCourseInstance", [{}])
        workload = instance[0].get("courseWorkload", "N/A") if instance else "N/A"
        if workload.startswith("PT") and workload.endswith("H"):
            duration = workload[2:-1] + " hours"
        else:
            duration = workload

        # φιλτραρισμα βάσει search_term
        description = course.get("description", "").lower()
        if search_term.lower() not in title.lower() and search_term.lower() not in description:
            continue

        ready_courses.append({
            "Course Title"         : title,
            "Provider / University": provider,
            "Category"             : "Programming",
            "Difficulty Level"     : difficulty,
            "Cost"                 : cost,
            "Duration"             : duration,
            "Teaching Language"    : "English"
        })

    df = pd.DataFrame(ready_courses) if ready_courses else empty_dataframe()
    print(f"[Codecademy] Status: {'Success' if not df.empty else 'No results'} — {len(df)} courses found")
    return df