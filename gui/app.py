"""
frontend application, user interface, GUI, tkinter
"""
import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/120.0.0.0 Safari/537.36"}

sites = [
    "https://www.simplilearn.com/all-courses",
    "https://www.udacity.com/courses/all",
    "https://www.edx.org/search?q=python",
]

for url in sites:
    r = requests.get(url, headers=HEADERS, timeout=10)
    print(f"{url} → {r.status_code}")