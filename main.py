import pandas as pd
from collectors.api_collectors import fetch_github, fetch_itunes, fetch_openlib
from collectors.scrapers import scrape_geeksforgeeks, scrape_codecademy, scrape_coursera

SEARCH_TERM_1 = "data science"
SEARCH_TERM_2 = "AI"
SEARCH_TERM_3 = "python"

df_openlib = fetch_openlib(SEARCH_TERM_3)
df_itunes  = fetch_itunes(SEARCH_TERM_3)
df_github  = fetch_github(SEARCH_TERM_3)

# ── Scrapers ──────────────────────────────────────────
df_gfg        = scrape_geeksforgeeks(SEARCH_TERM_1)
df_coursera   = scrape_coursera(SEARCH_TERM_2)
df_codecademy = scrape_codecademy(SEARCH_TERM_3)

# ── Συνδυασμός ────────────────────────────────────────
df_final = pd.concat([
    df_openlib, df_itunes, df_github,
    df_gfg, df_coursera, df_codecademy
], ignore_index=True)

print(f"\nTotal courses collected: {len(df_final)}")
print(df_final.to_string(index=False))

# ── Αποθήκευση ────────────────────────────────────────
df_final.to_csv("courses.csv", index=False, encoding="utf-8-sig")
print(f"\n Saved to courses.csv")