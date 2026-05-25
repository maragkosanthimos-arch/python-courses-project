import requests
import pandas as pd

#============================
#Σημείωση: Τα 2 πρώτα API ήταν οι μόνες λύσεις που δεν χρειαζόντουσαν authentication, οπότε τα έβαλα πρώτα για να έχω δεδομένα για να δουλέψω με το normalization και το csv manager
#============================

#μιμιση πραγματικου χρηστη Agent για να μην μπλοκαριστει το αιτημα
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

#ορισμα στηλων του dataframe 
COLUMNS = [
    "Course Title", "Provider / University", "Category",
    "Difficulty Level", "Cost", "Duration", "Teaching Language"
]

#κενο dataframe με τις στηλες που θελουμε για λογους ασφαλους επιστροφης σε περιπτωση λάθους
def empty_dataframe():
    return pd.DataFrame(columns=COLUMNS)


# =========================================================
# 🔵 API 1 — Open Library API
# =========================================================

def fetch_openlib(search_term):

    print(f"\n[Open Library] Sending request...")

    #χτιζουμε το url με τις παραμετρους τις αναζητησης οπως search term, πεδια που θελουμε να επιστρεφουν, και οριο αποτελεσματων
    url = (
        f"https://openlibrary.org/search.json"
        f"?q={search_term}+programming"
        f"&fields=title,author_name,subject,language"
        f"&limit=20"
    )

    #επιστροφη άδειου dataFrame σε περιπτωση που το αιτημα αποτυχει για οποιοδηποτε λογο
    try:
        response = requests.get(url, timeout=10)
    except requests.RequestException as e:
        print(f"[Open Library] Connection error: {e}")
        return empty_dataframe()

    #o κωδικος 200 σημαινει επιτυχια ευρεσης πληροφοριων, οποτε αν δεν ειναι 200 υπηρξε error και επιστρεφουμε κενο dataframe
    if response.status_code != 200:
        print(f"[Open Library] API Error: {response.status_code}")
        return empty_dataframe()
    
    #περιμενουμε data σε μορφη json και τα αποθηκευουμε σε μεταβλητη
    data = response.json()
    #τα αποτελεσματα της αναζητησης ειναι μεσα στο πεδιο "docs" του json, οποτε τα αποθηκευουμε σε μεταβλητη
    books_raw = data.get("docs", [])

    print(f"[Open Library] Status: Success — {len(books_raw)} results found")

    #κενος πινακας να βάλουμε τα αποτελεσματα για να φτιαξουμε το dataframe
    cleaned = []

    for book in books_raw[:20]:
        cleaned.append({
            "Course Title"         : book.get("title", "N/A"),
            "Provider / University": ", ".join(book.get("author_name", ["Unknown Author"])),
            "Category"             : ", ".join(book.get("subject", ["Programming"])[:2]),
            "Difficulty Level"     : "All Levels",   #δεν παρεχονται πληροφοριες μεσω του API για το επιπεδο δυσκολιας, τη διαρκεια και το κοστος
            "Cost"                 : "Free",    #site με βιβλία άρα δωρεάν
            "Duration"             : "Self-paced",     #το ίδιο και για τη διάρκεια
            "Teaching Language"    : ", ".join(book.get("language", ["English"])[:1])
        })

    return pd.DataFrame(cleaned) if cleaned else empty_dataframe()


# =========================================================
# 🟠 API 2 — iTunes Search API
# =========================================================

def fetch_itunes(search_term):

    print(f"\n[iTunes] Sending request...")

    url = (
        f"https://itunes.apple.com/search"
        f"?term={search_term}+course"
        f"&media=podcast"
        f"&entity=podcast"
        f"&limit=20"
        f"&lang=en_us"
    )

    try:
        response = requests.get(url, timeout=10)
    except requests.RequestException as e:
        print(f"[iTunes] Connection error: {e}")
        return empty_dataframe()

    if response.status_code != 200:
        print(f"[iTunes] API Error: {response.status_code}")
        return empty_dataframe()
    
    #====================================
    #μεχρι και εδω το σκεπτικο ειναι ίδιο
    #====================================
    #αναθετουμε τα δεδομενα που επιστρεφονται σε μορφη json σε μεταβλητη και απο εκει τα αποτελεσματα της αναζητησης που ειναι μεσα στο πεδιο "results" του json σε μια αλλη μεταβλητη
    results = response.json().get("results", [])

    print(f"[iTunes] Status: Success — {len(results)} results found")

    cleaned = []

    for item in results:
        cleaned.append({
            "Course Title"         : item.get("collectionName", "N/A"),
            "Provider / University": item.get("artistName", "N/A"),
            "Category"             : ", ".join(item.get("genres", ["N/A"])),
            "Difficulty Level"     : "All Levels",
            "Cost"                 : "Free",        #τα podcasts είναι δωρεάν
            "Duration"             : "Self-paced",      #και τα podcasts είναι self-paced
            "Teaching Language"    : "English"
        })

    return pd.DataFrame(cleaned) if cleaned else empty_dataframe()


# =========================================================
# 🟢 API 3 — GitHub Search API
# =========================================================

def fetch_github(search_term):

    print(f"\n[GitHub] Sending request...")

    url = (
        f"https://api.github.com/search/repositories"
        f"?q={search_term}+course&topic=education&sort=stars"
        f"&sort=stars"
        f"&order=desc"
        f"&per_page=20"
    )

    try:
        response = requests.get(
            url,
            headers={"Accept": "application/vnd.github+json"},
            timeout=10
        )
    except requests.RequestException as e:
        print(f"[GitHub] Connection error: {e}")
        return empty_dataframe()

    if response.status_code != 200:
        print(f"[GitHub] API Error: {response.status_code}")
        return empty_dataframe()

    results = response.json().get("items", [])

    #====================================
    #μεχρι και εδω το σκεπτικο ειναι ίδιο
    #====================================

    print(f"[GitHub] Status: Success — {len(results)} results found")

    cleaned = []

    #εκτελουμε εναν βρόχο για να περασουμε τα αποτελεσματα της αναζητησης που ειναι μεσα στο πεδιο "items" του json 
    # και να τα καθαρισουμε και να τα μετατρεψουμε στη μορφη που θελουμε για το dataframe
    for repo in results:
        name = repo.get("name", "N/A")

        # Χρησιμοποιούμε το όνομα του repository ως τίτλο του μαθήματος, κάνοντας κάποιες βασικές καθαρίσεις
        title = name.replace("-", " ").replace("_", " ").title()

        # καθαριζουμε τον τιτλο απο κολλημενες λέξεις και πολύ μεγάλες λέξεις που δεν μοιάζουν με τίτλο μαθήματος
        if len(title) > 80 or (" " not in title and len(title) > 15):
            continue

        cleaned.append({
            "Course Title"         : title,
            "Provider / University": repo.get("owner", {}).get("login", "N/A"),
            "Category"             : repo.get("language", "Programming"),
            "Difficulty Level"     : "All Levels",   #δεν παρεχονται πληροφοριες μεσω του API για το επιπεδο δυσκολιας, τη διαρκεια και το κοστος
            "Cost"                 : "Free",
            "Duration"             : "Self-paced",
            "Teaching Language"    : "English"
        })

    return pd.DataFrame(cleaned) if cleaned else empty_dataframe()
