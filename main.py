from utils.csv_manager import df_final

if __name__ == "__main__":
    print("=== Course Collection Completed ===")
    print(f"Total courses collected: {len(df_final)}")
    print(df_final.head(10).to_string(index=False))