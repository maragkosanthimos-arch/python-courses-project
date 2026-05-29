"""
frontend application, user interface, GUI, tkinter
"""
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os

# ---------------- IMPORT YOUR FUNCTIONS ---------------- #
from collectors.api_collectors import (fetch_github, fetch_itunes, fetch_devto)
from collectors.scrapers import (scrape_geeksforgeeks, scrape_codecademy, scrape_coursera)
from utils.normalizer import normalise_dataframe,filter_results
from utils.csv_manager import save_to_csv
from utils.graphs import (bar_chart, line_plot, pie_chart)
from utils.recommender import recommend_courses,convert_cost_to_number

class CourseGUI:

    def __init__(self, root):  # 1. Διορθώθηκε σε __init__
        self.root = root
        
        self.root.title("ΑΝΘΙΜΟΣ ΜΑΡΑΓΚΟΣ 1115493 - ΑΓΓΕΛΟΣ ΒΟΥΤΥΡΑΣ 1115516 - ΒΛΑΣΙΟΣ ΚΟΥΚΟΥΒΕΣ 1115474")
        self.root.geometry("1300x800")

        # 2. Ορισμός του ονόματος του CSV με βάση ένα ΑΜ της ομάδας 
        self.csv_filename = self.csv_filename = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "courses_1115493.csv") 

        # 3. Διορθώθηκε σε DataFrame με κεφαλαίο 'F'
        self.df = pd.DataFrame()

        self.search_terms = [
            "programming",
            "sound engineering",
            "data science",
            "sql"
        ]
        
        # 4. Διορθώθηκαν τα ονόματα των μεθόδων και προστέθηκαν οι παρενθέσεις ()
        self.create_buttons()
        self.create_filters()
        self.create_table()
        
        # Αυτόματο φόρτωμα αν υπάρχει ήδη το αρχείο CSV με ιστορικό [cite: 70]
        try:
            self.df = pd.read_csv(self.csv_filename)
            if self.df.empty:
                print(f"[{self.csv_filename}] Status: File is empty.")
            else:
                self.update_table(self.df)
                print(f"[{self.csv_filename}] Status: Existing data loaded on startup.")
        except pd.errors.EmptyDataError:
            print(f"[{self.csv_filename}] Status: File is empty.")
        except FileNotFoundError:
            print(f"[{self.csv_filename}] Status: No initial history found.")
#==========BUTTONS==========#
    def create_buttons(self):
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        collect_apis_button = tk.Button(
            button_frame,
            text="Collect APIs",
            width=15,
            command=self.collect_api_data
        )

        collect_scrapers_button = tk.Button(
            button_frame,
            text="Collect Scrapers",
            width=15,
            command=self.collect_scrapers_data
        )

        collect_apis_button.pack(side="left", padx=5)
        collect_scrapers_button.pack(side="left", padx=5)

        # 🆕 ΝΕΟ ΚΟΥΜΠΙ: RESET & RESTART
        reset_button = tk.Button(
            button_frame,
            text="Reset & Restart",
            width=15,
            fg="red", # Κόκκινο χρώμα για προειδοποίηση
            command=self.reset_and_restart
        )
        reset_button.pack(side="left", padx=5)

        export_button = tk.Button(
            button_frame,
            text="Export CSV",
            width=15,
            command=self.export_csv
        )
        export_button.pack(side="left", padx=5)

        bar_chart_button = tk.Button(
            button_frame,
            text="Bar Chart",
            width=15,
            command=self.show_bar_chart
        )
        bar_chart_button.pack(side="left", padx=5)

        pie_chart_button = tk.Button(
            button_frame,
            text="Pie Chart",
            width=15,
            command=self.show_pie_chart
        )
        pie_chart_button.pack(side="left", padx=5)

        line_plot_button = tk.Button(
            button_frame,
            text="Line Plot",
            width=15,
            command=self.show_line_plot
        )
        line_plot_button.pack(side="left", padx=5)


#==========FILTERS==========#
    def create_filters(self): # 5. Επαναφορά της μεθόδου εντός της κλάσης (Indentation)
        filter_frame = tk.Frame(self.root)
        filter_frame.pack(pady=5)

        tk.Label(filter_frame, text="Difficulty").pack(side="left", padx=5)

        self.difficulty_var = tk.StringVar()
        self.difficulty_box = ttk.Combobox(
            filter_frame,
            textvariable=self.difficulty_var,
            values=["All Levels", "Beginner", "Intermediate", "Advanced"],
            width=18
        )
        self.difficulty_box.pack(side="left", padx=5)
        self.difficulty_box.set("All Levels")

        # ---------------- CATEGORY ---------------- #
        tk.Label(filter_frame, text="Category").pack(side="left", padx=5)

        self.category_var = tk.StringVar()
        self.category_box = ttk.Combobox(
            filter_frame,
            textvariable=self.category_var,
            values=["All", "Programming", "Data Science", "SQL", "Sound Engineering"],
            width=18
        )
        self.category_box.pack(side="left", padx=5)
        self.category_box.set("All")

        # ---------------- LANGUAGE ---------------- #
        tk.Label(filter_frame, text="Language").pack(side="left", padx=5)

        self.language_var = tk.StringVar()
        self.language_box = ttk.Combobox(
            filter_frame,
            textvariable=self.language_var,
            values=["All", "English", "Spanish", "French"],
            width=18
        )
        self.language_box.pack(side="left", padx=5)
        self.language_box.set("All")

        # ---------------- MAX COST ---------------- #
        tk.Label(filter_frame, text="Max Cost (0=Free)").pack(side="left", padx=2)

        self.cost_entry = tk.Entry(filter_frame, width=10)
        self.cost_entry.pack(side="left", padx=5)

        # ---------------- CASE SENSITIVE ---------------- #
        self.case_var = tk.BooleanVar()
        case_check = tk.Checkbutton(
            filter_frame,
            text="Case Sensitive",
            variable=self.case_var
        )
        case_check.pack(side="left", padx=10)

        # ---------------- RECOMMEND BUTTON ---------------- #
        recommend_btn = tk.Button(
            filter_frame,
            text="Recommend Courses",
            command=self.run_recommendation
        )
        recommend_btn.pack(side="left", padx=10)
    

#==========TABLE==========#
    def create_table(self):
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True)

        columns = (
            "Course Title",
            "Provider / University",
            "Category",
            "Difficulty Level",
            "Cost",
            "Duration",
            "Teaching Language"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180, anchor="center")

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)


    def update_table(self, dataframe):
        """Βοηθητική μέθοδος για να καθαρίζει και να ανανεώνει τον πίνακα του GUI"""
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        if dataframe is not None and not dataframe.empty:
            for _, row in dataframe.iterrows():
                self.tree.insert(
                    "", "end",
                    values=(
                        row.get("Course Title", ""),
                        row.get("Provider / University", ""),
                        row.get("Category", ""),
                        row.get("Difficulty Level", ""),
                        row.get("Cost", ""),
                        row.get("Duration", ""),
                        row.get("Teaching Language", "")
                    )
                )


#==========COLLECT DATA==========#
    def collect_api_data(self):
        api_dfs = []
        try:
            df_devto = pd.concat([fetch_devto(term) for term in self.search_terms], ignore_index=True)
            api_dfs.append(df_devto)
            print("[Dev.to API] Status: Success") 
        except Exception as e:
            print(f"[Dev.to API] Status: Failed | Error: {e}")

        try:
            df_itunes = pd.concat([fetch_itunes(term) for term in self.search_terms], ignore_index=True)
            api_dfs.append(df_itunes)
            print("[iTunes API] Status: Success") 
        except Exception as e:
            print(f"[iTunes API] Status: Failed | Error: {e}")

        try:
            df_github = pd.concat([fetch_github(term) for term in self.search_terms], ignore_index=True)
            api_dfs.append(df_github)
            print("[GitHub API] Status: Success") 
        except Exception as e:
            print(f"[GitHub API] Status: Failed | Error: {e}")

        if api_dfs:
            # Αν κλήθηκε μεμονωμένα το κουμπί, κανονικοποιούμε και σώζουμε
            merged = pd.concat(api_dfs, ignore_index=True)
            self.save_and_refresh_data(merged)
            
    def collect_scrapers_data(self):
        """Αναλαμβάνει αποκλειστικά τη συλλογή από τα 3 Web Scrapers"""
        scraper_dfs = []

        try:
            df_gfg = pd.concat([scrape_geeksforgeeks(term) for term in self.search_terms], ignore_index=True)
            scraper_dfs.append(df_gfg)
            print("[GeeksForGeeks Scraper] Status: Success") 
        except Exception as e:
            print(f"[GeeksForGeeks Scraper] Status: Failed | Error: {e}")

        try:
            df_coursera = pd.concat([scrape_coursera(term) for term in self.search_terms], ignore_index=True)
            scraper_dfs.append(df_coursera)
            print("[Coursera Scraper] Status: Success") 
        except Exception as e:
            print(f"[Coursera Scraper] Status: Failed | Error: {e}")

        try:
            df_codecademy = pd.concat([scrape_codecademy(term) for term in self.search_terms], ignore_index=True)
            scraper_dfs.append(df_codecademy)
            print("[Codecademy Scraper] Status: Success") 
        except Exception as e:
            print(f"[Codecademy Scraper] Status: Failed | Error: {e}")

        if scraper_dfs:
            # Αν κλήθηκε μεμονωμένα το κουμπί, κανονικοποιούμε και σώζουμε
            merged = pd.concat(scraper_dfs, ignore_index=True)
            self.save_and_refresh_data(merged)

    def save_and_refresh_data(self, new_data_df):
        """Βοηθητική μέθοδος για την ένωση, αφαίρεση διπλοτύπων και αποθήκευση"""
        try:
            existing_df = pd.DataFrame()
            try:
                existing_df = pd.read_csv(self.csv_filename)
            except FileNotFoundError:
                pass

            normalized_new = normalise_dataframe(new_data_df)
            normalized_new = filter_results(normalized_new, *self.search_terms)
            print("[Data Normalization] Status: Success") 

            # 2. Ένωση με το ιστορικό [cite: 32]
            if not existing_df.empty:
                combined = pd.concat([existing_df, normalized_new], ignore_index=True)
            else:
                combined = normalized_new

            # 3. Αφαίρεση διπλοτύπων για να μην γεμίζει το CSV ίδια μαθήματα
            self.df = combined.drop_duplicates(subset=["Course Title", "Provider / University"], keep="first")
            self.df.reset_index(drop=True, inplace=True)

            # 4. Αποθήκευση στο κεντρικό αρχείο [cite: 27, 83]
            self.df.to_csv(self.csv_filename, index=False, encoding='utf-8-sig')
            print(f"[CSV Manager] Status: Successfully updated {self.csv_filename}") 

            # Ενημέρωση του πίνακα στην οθόνη 
            self.update_table(self.df)
            messagebox.showinfo("Success", "Data collected and synchronized successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving data: {str(e)}")


    def run_recommendation(self):
        """Εκτελεί τον αλγόριθμο συστάσεων (Composite Score) [cite: 56, 75]"""
        try:
            # Διαβάζουμε το τρέχον ιστορικό από το CSV 
            try:
                current_df = pd.read_csv(self.csv_filename)
                if current_df.empty:
                    messagebox.showwarning("Warning", "The CSV history file is empty. Please collect data first.") 
                    return
            except FileNotFoundError:
                messagebox.showwarning("Warning", "No CSV history file found. Please collect data first.") 
                return

            # Παίρνουμε τις τιμές από το GUI [cite: 60]
            difficulty = self.difficulty_var.get()
            category = self.category_var.get()
            language = self.language_var.get()
            cost_text = self.cost_entry.get().strip()
            max_cost = float(cost_text) if cost_text else None
            case_sensitive = self.case_var.get()

            # --- ΔΙΟΡΘΩΣΗ ΦΙΛΤΡΩΝ ΓΙΑ ΤΟ "ALL" ---
            # Αν ο χρήστης επέλεξε "All Levels" ή "All", φιλτράρουμε μόνο αν η επιλογή ΔΕΝ είναι "All"
            temp = pd.DataFrame()
            filtered_df = current_df.copy()
        
                    
            if category != "All":
                if not case_sensitive:
                    filtered_df = filtered_df[filtered_df["Category"].str.lower() == category.lower()]
                else:
                    filtered_df = filtered_df[filtered_df["Category"] == category]
                    
            if language != "All":
                if not case_sensitive:
                    filtered_df = filtered_df[filtered_df["Teaching Language"].str.lower() == language.lower()]
                else:
                    filtered_df = filtered_df[filtered_df["Teaching Language"] == language]
            
            if difficulty != "All Levels":
                if not case_sensitive:
                    temp = filtered_df[filtered_df["Difficulty Level"].str.lower() == difficulty.lower()]
                else:
                    temp = filtered_df[filtered_df["Difficulty Level"] == difficulty]
                
                if temp.empty:
                    # Δεν βρήκε Beginner Data Science → κρατάει Data Science χωρίς difficulty filter
                    print(f"No '{difficulty}' found. Showing All Levels.")
                else:
                    filtered_df = temp  # βρήκε → χρησιμοποίησε το

            if max_cost is not None and max_cost == 0:
                filtered_df = filtered_df[filtered_df["Cost"] == "Free"]
            elif max_cost is not None and max_cost > 0:
                filtered_df = filtered_df[filtered_df["Cost"].apply(convert_cost_to_number) <= max_cost]
            # Αν μετά τα φίλτρα δεν έμεινε τίποτα, σταματάμε [cite: 71]
            if filtered_df.empty:
                messagebox.showinfo("No Results", "No matching courses found for the given criteria.") 
                self.update_table(pd.DataFrame()) # Καθαρισμός πίνακα
                return

            # Κλήση της recommend_courses περνώντας της το ήδη ΦΙΛΤΡΑΡΙΣΜΕΝΟ DataFrame 
            # ώστε αυτή να αναλάβει ΜΟΝΟ τον υπολογισμό του Composite Score [cite: 65, 75]
            # (Σημείωση: Πρέπει να προσαρμόσεις τη συνάρτηση recommend_courses στο αρχείο σου να δέχεται το dataframe)
            recommendations = recommend_courses(df=filtered_df) 

            if recommendations is None or recommendations.empty:
                messagebox.showinfo("No Results", "No matching recommendations found.") 
            else:
                # Εμφάνιση των 3 βέλτιστων προτάσεων στον πίνακα [cite: 65, 71]
                self.update_table(recommendations.head(3))

        except Exception as e:
            messagebox.showerror("Error", f"Recommendation error: {str(e)}")

    def export_csv(self):
        """Εξαγωγή των τρεχόντων δεδομένων του πίνακα σε νέο αρχείο [cite: 41]"""
        try:
            if self.df.empty:
                messagebox.showwarning("Warning", "No data available to export.")
                return
            save_to_csv(self.df)
            messagebox.showinfo("Export Complete", "Current data successfully exported to a new CSV file!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_bar_chart(self):
        try:
            bar_chart(top=5) # 1ο Γράφημα [cite: 44]
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_pie_chart(self):
        try:
            pie_chart() # 2ο Γράφημα [cite: 47]
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_line_plot(self):
        try:
            line_plot() # 3ο Γράφημα [cite: 50]
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def reset_and_restart(self):
        """Διαγράφει το υπάρχον αρχείο CSV, καθαρίζει τα δεδομένα και ξεκινά νέα συλλογή"""
        # Ερώτηση επιβεβαίωσης στον χρήστη για ασφάλεια
        confirm = messagebox.askyesno(
            "Confirmation", 
            "Are you sure you want to delete the previous CSV file and restart data collection from scratch?"
        )
        
        if confirm:
            try:
                # 1. Έλεγχος αν υπάρχει το αρχείο και διαγραφή του
                if os.path.exists(self.csv_filename):
                    os.remove(self.csv_filename)
                    print(f"[CSV Manager] Status: Deleted existing file {self.csv_filename}")
                else:
                    print(f"[CSV Manager] Status: No file found to delete. Starting fresh.")

                # 2. Καθαρισμός του εσωτερικού DataFrame της εφαρμογής
                self.df = pd.DataFrame()

                # 3. Καθαρισμός του πίνακα (Treeview) στην οθόνη
                self.update_table(self.df)

                messagebox.showinfo("Reset Successful", "Previous data cleared. Starting new data collection...")

                # 4. Αυτόματη έναρξη της συλλογής δεδομένων
                # Καλούμε ξεχωριστά τα API και τα Scrapers για να μαζέψουν τα νέα δεδομένα
                print("[Reset & Restart] Executing fresh data collection...")
                
                # Φτιάχνουμε μια προσωρινή λίστα για να μαζέψουμε τα ολόφρεσκα δεδομένα
                fresh_dfs = []
                
                # Συλλογή API
                try:
                    df_devto = pd.concat([fetch_devto(term) for term in self.search_terms], ignore_index=True)
                    fresh_dfs.append(df_devto)
                except Exception: pass
                
                try:
                    df_itunes = pd.concat([fetch_itunes(term) for term in self.search_terms], ignore_index=True)
                    fresh_dfs.append(df_itunes)
                except Exception: pass
                
                try:
                    df_github = pd.concat([fetch_github(term) for term in self.search_terms], ignore_index=True)
                    fresh_dfs.append(df_github)
                except Exception: pass

                # Συλλογή Scrapers
                try:
                    df_gfg = pd.concat([scrape_geeksforgeeks(term) for term in self.search_terms], ignore_index=True)
                    fresh_dfs.append(df_gfg)
                except Exception: pass
                
                try:
                    df_coursera = pd.concat([scrape_coursera(term) for term in self.search_terms], ignore_index=True)
                    fresh_dfs.append(df_coursera)
                except Exception: pass
                
                try:
                    df_codecademy = pd.concat([scrape_codecademy(term) for term in self.search_terms], ignore_index=True)
                    fresh_dfs.append(df_codecademy)
                except Exception: pass

                if fresh_dfs:
                    merged_fresh = pd.concat(fresh_dfs, ignore_index=True)
                    # Η save_and_refresh_data θα αναλάβει να τα φιλτράρει, να αφαιρέσει διπλότυπα 
                    # και να δημιουργήσει το καινούριο πλέον αρχείο CSV
                    self.save_and_refresh_data(merged_fresh)
                else:
                    messagebox.showwarning("Warning", "Could not fetch any new data after reset.")

            except Exception as e:
                messagebox.showerror("Error", f"An error occurred during reset: {str(e)}")