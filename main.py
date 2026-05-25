import pandas as pd
from collectors.api_collectors import fetch_github, fetch_itunes, fetch_openlib
from collectors.scrapers import scrape_geeksforgeeks, scrape_codecademy, scrape_coursera
from utils.csv_manager import save_to_csv
from utils.normalizer import filter_results
from utils.graphs import bar_chart, bar_chart,line_plot,pie_chart

df_openlib    = fetch_openlib("programming")
df_itunes     = fetch_itunes("programming")
df_github     = fetch_github("programming")

df_gfg        = scrape_geeksforgeeks("data science")
df_coursera   = scrape_coursera("AI")
df_codecademy = scrape_codecademy("programming")

df_final = pd.concat([
    df_openlib, df_itunes, df_github,
    df_gfg, df_coursera, df_codecademy
], ignore_index=True)

df_final=filter_results(df_final,"programming")

save_to_csv(df_final)

bar_chart(top=5)
pie_chart()
line_plot()

