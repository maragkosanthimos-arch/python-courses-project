import requests
import pandas as pd

# για χρήση APIs χρειαζόμαστε requests και pandas
print("Libraries loaded successfully!")

# ── Search Parameter ─────────────────────────────────────
SEARCH_TERM = "python"


# =========================================================
# 🔵 API 1 — Open Library API
# Educational books and learning material
# =========================================================

openlib_url = (
    f"https://openlibrary.org/search.json"
    f"?q={SEARCH_TERM}+programming"
    f"&fields=title,author_name,subject,language"
    f"&limit=20"
)

print(f"\nSending request to Open Library API...")

response_openlib = requests.get(
    openlib_url,
    timeout=10
)

if response_openlib.status_code == 200:

    data_openlib = response_openlib.json()

    print("Data received successfully!")
    print(f"Total results found: {data_openlib['numFound']}")

else:

    print(f"API Error: {response_openlib.status_code}")
    data_openlib = {"docs": []}

books_raw = data_openlib["docs"]

cleaned_openlib = []

for book in books_raw[:20]:

    cleaned_openlib.append({

        "Course Title": book.get(
            "title",
            "N/A"
        ),

        "Provider / University": ", ".join(
            book.get("author_name", ["Unknown Author"])
        ),

        "Category": ", ".join(
            book.get("subject", ["Programming"])[:2]
        ),

        "Difficulty Level": "N/A",

        "Cost": "Free",

        "Duration": "N/A",

        "Teaching Language": ", ".join(
            book.get("language", ["English"])[:1]
        )

    })

df_openlib = pd.DataFrame(cleaned_openlib)

print("\nOpen Library Results:")
print(df_openlib.head(10).to_string(index=False))


# =========================================================
# 🟠 API 2 — iTunes Search API (Apple)
# Educational podcasts and courses — no API key needed
# =========================================================

itunes_url = (
    f"https://itunes.apple.com/search"
    f"?term={SEARCH_TERM}+course"
    f"&media=podcast"
    f"&entity=podcast"
    f"&limit=20"
    f"&lang=en_us"
)

print(f"\nSending request to iTunes API...")

response_itunes = requests.get(
    itunes_url,
    timeout=10
)

if response_itunes.status_code == 200:

    data_itunes = response_itunes.json()

    results_itunes = data_itunes.get("results", [])

    print("Data received successfully!")
    print(f"Total results found: {data_itunes.get('resultCount', 0)}")

    # Sample of first result
    if results_itunes:
        sample = results_itunes[0]
        print(f"\n Title     : {sample.get('collectionName')}")
        print(f" Creator   : {sample.get('artistName', 'N/A')}")
        print(f" Genre     : {', '.join(sample.get('genres', ['N/A']))}")
        print(f" Link      : {sample.get('collectionViewUrl', 'N/A')}")

else:

    print(f"API Error: {response_itunes.status_code}")
    results_itunes = []

cleaned_itunes = []

for item in results_itunes:

    cleaned_itunes.append({

        "Course Title": item.get(
            "collectionName",
            "N/A"
        ),

        "Provider / University": item.get(
            "artistName",
            "N/A"
        ),

        "Category": ", ".join(
            item.get("genres", ["N/A"])
        ),

        "Difficulty Level": "N/A",

        "Cost": "Free",

        "Duration": "Self-paced",

        "Teaching Language": "English"

    })

df_itunes = pd.DataFrame(cleaned_itunes) if cleaned_itunes else pd.DataFrame(
    columns=["Course Title", "Provider / University", "Category",
             "Difficulty Level", "Cost", "Duration", "Teaching Language"]
)

print("\niTunes Results:")
print(df_itunes.head(10).to_string(index=False))


# =========================================================
# 🟢 API 3 — GitHub Search API
# Educational repositories and tutorials
# =========================================================

github_url = (
    f"https://api.github.com/search/repositories"
    f"?q={SEARCH_TERM}+course+tutorial"
    f"&sort=stars"
    f"&order=desc"
    f"&per_page=20"
)

headers_github = {
    "Accept": "application/vnd.github+json"
}

print(f"\nSending request to GitHub API...")

response_github = requests.get(
    github_url,
    headers=headers_github,
    timeout=10
)

if response_github.status_code == 200:

    data_github = response_github.json()

    results_github = data_github.get("items", [])

    print("Data received successfully!")
    print(f"Total results found: {data_github.get('total_count', 0)}")

else:

    print(f"API Error: {response_github.status_code}")
    results_github = []

cleaned_github = []

for repo in results_github:

    cleaned_github.append({

        "Course Title": repo.get(
            "name",
            "N/A"
        ),

        "Provider / University": repo.get(
            "owner",
            {}
        ).get(
            "login",
            "N/A"
        ),

        "Category": repo.get(
            "language",
            "Programming"
        ),

        "Difficulty Level": "N/A",

        "Cost": "Free",

        "Duration": "Self-paced",

        "Teaching Language": "English"

    })

df_github = pd.DataFrame(cleaned_github)

print("\nGitHub Results:")
print(df_github.head(10).to_string(index=False))


# =========================================================
# 🔗 Merge All APIs
# =========================================================

frames = [

    df_openlib,
    df_itunes,   # ← διορθώθηκε από df_youtube
    df_github

]

df_all = pd.concat(
    frames,
    ignore_index=True
)

print(f"\nTotal courses collected: {len(df_all)}")

print("\nFinal Unified Dataset:")
print(df_all.head(20).to_string(index=False))


# =========================================================
# Export to CSV
# =========================================================

output_filename = f"courses_{SEARCH_TERM}.csv"

df_all.to_csv(

    output_filename,
    index=False,
    encoding="utf-8-sig"

)

print(f"\nFile '{output_filename}' created successfully!")