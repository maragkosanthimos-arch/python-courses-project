import pandas as pd
from collectors.api_collectors import fetch_github, fetch_itunes, fetch_openlib
from collectors.scrapers import scrape_geeksforgeeks, scrape_codecademy, scrape_coursera
from utils.csv_manager import save_to_csv
from utils.normalizer import filter_results
from utils.graphs import bar_chart, bar_chart,line_plot,pie_chart

search_terms = ["programming", "sound engineering", "biology", "sql"]

df_openlib = pd.concat([fetch_openlib(term) for term in search_terms], ignore_index=True)
df_itunes  = pd.concat([fetch_itunes(term)  for term in search_terms], ignore_index=True)
df_github  = pd.concat([fetch_github(term)  for term in search_terms], ignore_index=True)


df_gfg        =  pd.concat([scrape_geeksforgeeks(term) for term in search_terms], ignore_index=True)
df_coursera   = pd.concat([scrape_coursera(term) for term in search_terms], ignore_index=True)
df_codecademy = pd.concat([scrape_codecademy(term) for term in search_terms], ignore_index=True)

df_final = pd.concat([
    df_openlib, df_itunes, df_github,
    df_gfg, df_coursera, df_codecademy
], ignore_index=True)

df_final=filter_results(df_final,*search_terms)


save_to_csv(df_final)

bar_chart(top=5)
pie_chart()
line_plot()

