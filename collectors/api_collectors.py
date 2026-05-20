import requests
import pandas as pd

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

COLUMNS = [
    "Course Title", "Provider / University", "Category",
    "Difficulty Level", "Cost", "Duration", "Teaching Language"
]


def empty_dataframe():
    return pd.DataFrame(columns=COLUMNS)


# =========================================================
# 🔵 API 1 — Open Library API
# =========================================================

def fetch_openlib(search_term):

    print(f"\n[Open Library] Sending request...")

    url = (
        f"https://openlibrary.org/search.json"
        f"?q={search_term}+programming"
        f"&fields=title,author_name,subject,language"
        f"&limit=20"
    )

    try:
        response = requests.get(url, timeout=10)
    except requests.RequestException as e:
        print(f"[Open Library] Connection error: {e}")
        return empty_dataframe()

    if response.status_code != 200:
        print(f"[Open Library] API Error: {response.status_code}")
        return empty_dataframe()

    data = response.json()
    books_raw = data.get("docs", [])

    print(f"[Open Library] Status: Success — {len(books_raw)} results found")

    cleaned = []

    for book in books_raw[:20]:
        cleaned.append({
            "Course Title"         : book.get("title", "N/A"),
            "Provider / University": ", ".join(book.get("author_name", ["Unknown Author"])),
            "Category"             : ", ".join(book.get("subject", ["Programming"])[:2]),
            "Difficulty Level"     : "N/A",
            "Cost"                 : "Free",
            "Duration"             : "N/A",
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

    results = response.json().get("results", [])

    print(f"[iTunes] Status: Success — {len(results)} results found")

    cleaned = []

    for item in results:
        cleaned.append({
            "Course Title"         : item.get("collectionName", "N/A"),
            "Provider / University": item.get("artistName", "N/A"),
            "Category"             : ", ".join(item.get("genres", ["N/A"])),
            "Difficulty Level"     : "N/A",
            "Cost"                 : "Free",
            "Duration"             : "Self-paced",
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
        f"?q={search_term}+course+tutorial"
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

    print(f"[GitHub] Status: Success — {len(results)} results found")

    cleaned = []

    for repo in results:
        cleaned.append({
            "Course Title"         : repo.get("name", "N/A"),
            "Provider / University": repo.get("owner", {}).get("login", "N/A"),
            "Category"             : repo.get("language", "Programming"),
            "Difficulty Level"     : "N/A",
            "Cost"                 : "Free",
            "Duration"             : "Self-paced",
            "Teaching Language"    : "English"
        })

    return pd.DataFrame(cleaned) if cleaned else empty_dataframe()