"""
frontend application, user interface, GUI, tkinter
Αρχείο που περιέχει την κλάση CourseGUI — το γραφικό περιβάλλον της εφαρμογής.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os

from collectors.api_collectors import (fetch_github, fetch_itunes, fetch_devto)
from collectors.scrapers import (scrape_geeksforgeeks, scrape_codecademy, scrape_coursera)
from utils.normalizer import normalise_dataframe, filter_results
from utils.csv_manager import save_to_csv
from utils.graphs import (bar_chart, line_plot, pie_chart)
from utils.recommender import recommend_courses, convert_cost_to_number


class CourseGUI:

    #constructor - οι βασικές λειτουργίες που θέλουμε να γίνουν με το που πατήσουμε το κουμπί του compile
    def __init__(self, root):
        # Αποθήκευση αναφοράς στο κύριο παράθυρο της εφαρμογής
        self.root = root

        # ορισμός τίτλου παραθύρου με τα ονόματα και ΑΜ της ομάδας
        self.root.title("ΑΝΘΙΜΟΣ ΜΑΡΑΓΚΟΣ 1115493 - ΑΓΓΕΛΟΣ ΒΟΥΤΥΡΑΣ 1115516 - ΒΛΑΣΙΟΣ ΚΟΥΚΟΥΒΕΣ 1115474")
        # Ορισμός διαστάσεων παραθύρου σε pixels (πλάτος x ύψος)
        self.root.geometry("1300x800")

        # κατασκευή τουμονοπατιού για το αρχείο CSV
        # χρησιμοποιούμε abspath+dirname δύο φορές για να παμε στον φάκελο του project και να τι βαλουμε στον επιμέρους φάκελο "data" 
        self.csv_filename = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "courses_1115493.csv"
        )

        # Αρχικοποίηση κενού DataFrame
        #θα γεμίσει είτε απο ήδη υπάρχον csv είτε από συλλογη δεδομένων
        self.df = pd.DataFrame()

        # Λίστα με τους όρους αναζήτησης που χρησιμοποιούνται σε APIs και Scrapers
        self.search_terms = [
            "programming",       
            "sound engineering",
            "data science",       
            "sql"                
        ]

        # κλήση των μεθόδων που χτίζουν τα τρία βασικά τμήματα του GUI
        self.create_buttons()  # δημιουργία κουμπιών
        self.create_filters()  # δημιουργία φίλτρων
        self.create_table()    # δημιουργία πίνακα αποτελεσμάτων

        # Προσπάθεια αυτόματης φόρτωσης υπάρχοντος CSV κατά την εκκίνηση
        #αν υπάρχει ήδη csv στα data,το φορτώνει στον πίνακα
        try:
            # Ανάγνωση του αρχείου CSV σε DataFrame
            self.df = pd.read_csv(self.csv_filename)
            # Έλεγχος αν το αρχείο είναι κενό
            #αν δεν είναι κενό, φορτώνουμε τα δεδομένα που ήδη έχει αφου κάνουμε update table
            #αλλιώς, exception δεν βρέθηκε αρχείο και ξεκινάει το collect
            if self.df.empty:
                print(f"[{self.csv_filename}] Status: File is empty.")
            else:
                self.update_table(self.df)
                print(f"[{self.csv_filename}] Status: Existing data loaded on startup.")
        except FileNotFoundError:
            print(f"[{self.csv_filename}] Status: No initial history found.")


    # ========================================================
    #                        BUTTONS
    # ========================================================
    def create_buttons(self):
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        collect_apis_button = tk.Button(
            button_frame,
            text="Collect APIs",
            width=15,
            command=self.collect_api_data  # συνδέεται με τη μέθοδο collect_api_data
        )

        collect_scrapers_button = tk.Button(
            button_frame,
            text="Collect Scrapers",
            width=15,
            command=self.collect_scrapers_data  # συνδέεται με τη μέθοδο collect_scrapers_data
        )

        collect_apis_button.pack(side="left", padx=5)
        collect_scrapers_button.pack(side="left", padx=5)

        reset_button = tk.Button(
            button_frame,
            text="Reset & Restart",
            width=15,
            fg="red",
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


    # ========================================================
    #                        FILTERS
    # ========================================================
    def create_filters(self):
        filter_frame = tk.Frame(self.root)
        filter_frame.pack(pady=5)

        # Ετικέτα περιγραφής του φίλτρου
        tk.Label(filter_frame, text="Difficulty").pack(side="left", padx=5)
        # Μεταβλητή που κρατά την επιλογή του χρήστη
        self.difficulty_var = tk.StringVar()
        self.difficulty_box = ttk.Combobox(
            filter_frame,
            textvariable=self.difficulty_var,
            values=["All Levels", "Beginner", "Intermediate", "Advanced"],
            width=18
        )
        self.difficulty_box.pack(side="left", padx=5)
        # Προεπιλεγμένη τιμή: All levels
        self.difficulty_box.set("All Levels")

        tk.Label(filter_frame, text="Category").pack(side="left", padx=5)
        self.category_var = tk.StringVar()
        # Αναπτυσσόμενη λίστα με τις διαθέσιμες κατηγορίες μαθημάτων
        self.category_box = ttk.Combobox(
            filter_frame,
            textvariable=self.category_var,
            values=["All", "Programming", "Data Science", "SQL", "Sound Engineering"],
            width=18
        )
        self.category_box.pack(side="left", padx=5)
        self.category_box.set("All")

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

        #0 όπως προαναφέραμε σημαίνει δωρεάν
        tk.Label(filter_frame, text="Max Cost (0=Free)").pack(side="left", padx=2)
        self.cost_entry = tk.Entry(filter_frame, width=10)
        self.cost_entry.pack(side="left", padx=5)

        recommend_btn = tk.Button(
            filter_frame,
            text="Recommend Courses",
            fg="blue",
            command=self.run_recommendation
        )
        recommend_btn.pack(side="left", padx=10)

        #για επιστροφη στο αρχικό μενου των δεδομένων
        self.show_all_btn = tk.Button(
            filter_frame,
            text="Show All",
            fg="green",
            command=self.show_all_courses
        )
        
        self.show_all_btn.pack(side="left", padx=10)
        #εμφανίζεται μόνο μετα απο recommendation
        self.show_all_btn.pack_forget()

    #========================================================
    #              REFRESH AFTER RECOMMENDATION
    #========================================================
    def show_all_courses(self):
        self.update_table(self.df)
        self.show_all_btn.pack_forget()


    #========================================================
    #                        TABLE
    #========================================================
    def create_table(self):
        #δημιουργουμε container που θα καταλαμβάνει όλο το υπολοιπο παράθυρο
        table_frame = tk.Frame(self.root)
        # fill="both" και expand=True για να μεγαλώνει με το παράθυρο
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

        #δημιουργία treeview widget 
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        # Ορισμός επικεφαλίδας και πλάτους για κάθε στήλη
        #όνομα στηλης ακριβώς στη μέση
        for col in columns:
            self.tree.heading(col, text=col)              
            self.tree.column(col, width=180, anchor="center") 

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview  # συνδέεται με την κατακόρυφη κύλιση του Treeview
        )

        self.tree.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

    #όρισμα το df που θελουμε να εμφανίσουμε στον πίνακα
    #αυτοματο refresh του treeview με κάθε κλείσιμο και άνοιγμα της εφαρμογής. σβήνει ότι υπήρχε και ξανατυπώνει εκ νέου
    #για αυτο το καλούμε στον constructor
    def update_table(self, dataframe):
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Αν το DataFrame δεν είναι κενό, εισαγωγή κάθε γραμμής στον πίνακα
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


    # ========================================================
    #                     COLLECT DATA
    # ========================================================
    #αρκετα self-explanatory, μαζευει δεδομένα μέσω API
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

        #αν δεν είναι κενός ο πίνακας με τα API data, κάλεσε save and refresh(normalization ξανα γιατι μόνο καλό κάνει)
        if api_dfs:
            merged = pd.concat(api_dfs, ignore_index=True)
            self.save_and_refresh_data(merged)


    def collect_scrapers_data(self):
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
            merged = pd.concat(scraper_dfs, ignore_index=True)
            self.save_and_refresh_data(merged)


    def save_and_refresh_data(self, new_data_df):
        try:
            # αρχικοποιούμε κενό DataFrame για το υπάρχον ιστορικό
            existing_df = pd.DataFrame()
            try:
                existing_df = pd.read_csv(self.csv_filename)
            except FileNotFoundError:
                # Αν δεν υπάρχει αρχείο, συνεχίζουμε με κενό DataFrame
                pass

            # Εφαρμογή κανονικοποίησης στα νέα δεδομένα (τίτλοι, κόστος, γλώσσα κ.λπ.)
            normalized_new = normalise_dataframe(new_data_df)
            # Φιλτράρισμα ώστε να κρατηθούν μόνο σχετικά μαθήματα με τους όρους αναζήτησης
            normalized_new = filter_results(normalized_new, *self.search_terms)
            print("[Data Normalization] Status: Success")

            #αν υπάρχουν παλια δεδομένα ενώνουμε με καινούρια, αλλιώς αυτά είναι τα πρώτα
            if not existing_df.empty:
                combined = pd.concat([existing_df, normalized_new], ignore_index=True)
            else:
                combined = normalized_new

            # αφαίρεση διπλότυπων βάσει τίτλου και παρόχου.ΠΑΛΙ.
            #σας εγγυώμαστε, διπλότυπο μέσα στο αρχείο δεν θα βρείτε μετά απο 3 filtrations, στανταρ.
            self.df = combined.drop_duplicates(
                subset=["Course Title", "Provider / University"],
                keep="first"
            )
            # επαναρίθμηση index μετά την αφαίρεση διπλότυπων αλλιώς θα είχαμε 60 στοιχεία αλλα 80 αριθμημένες θέσεις
            self.df.reset_index(drop=True, inplace=True)

            # Αποθήκευση του τελικού DataFrame στο CSV με υποστήριξη ελληνικών (utf-8-sig)
            self.df.to_csv(self.csv_filename, index=False, encoding='utf-8-sig')
            print(f"[CSV Manager] Status: Successfully updated {self.csv_filename}")

            #ανανεώνουμε treeview με νέα δεδομένα
            self.update_table(self.df)
            messagebox.showinfo("Success", "Data collected and synchronized successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Error saving data: {str(e)}")


    def run_recommendation(self):
        try:
            try:
                #ο καθιερωμένος μέχρι τώρα έλεγχος για κενό ή ανύπαρκτο csv 
                current_df = pd.read_csv(self.csv_filename)
                if current_df.empty:
                    messagebox.showwarning("Warning", "The CSV history file is empty. Please collect data first.")
                    return
            except FileNotFoundError:
                messagebox.showwarning("Warning", "No CSV history file found. Please collect data first.")
                return

            # διαβασμα τιμών που έβαλε ο χρήστης στα φίλτρα
            difficulty = self.difficulty_var.get()    
            category = self.category_var.get()        
            language = self.language_var.get()        
            cost_text = self.cost_entry.get().strip() 
            max_cost = float(cost_text) if cost_text else None

            filtered_df = current_df.copy()

            #ένα ακόμα στρώμα normalization
            #επειδή δεν θέλαμε ο recommender να μην δίνει αποτελέσματα σε ορισμένες περιπτώσεις
            #αν κάποιος ψαχνει κάποιο level και δεν υπάρχει, επιστρέφει All Levels, όπως μάλλον έχουμε προαναφέρει, μιας και το All Levels τα συμπεριλαμβάνει όλα
            if category != "All":
                    filtered_df = filtered_df[filtered_df["Category"].str.lower() == category.lower()]

            if language != "All":
                    filtered_df = filtered_df[filtered_df["Teaching Language"].str.lower() == language.lower()]
                
            
            if difficulty != "All Levels":
                temp = filtered_df[filtered_df["Difficulty Level"].str.lower() == difficulty.lower()]
                if temp.empty:
                    print(f"No '{difficulty}' found. Showing All Levels.")
                else:
                    filtered_df = temp

            if max_cost is not None and max_cost == 0:
                filtered_df = filtered_df[filtered_df["Cost"] == "Free"]
            elif max_cost is not None and max_cost > 0:
                filtered_df = filtered_df[filtered_df["Cost"].apply(convert_cost_to_number) <= max_cost]

            if filtered_df.empty:
                messagebox.showinfo("No Results", "No matching courses found for the given criteria.")
                self.update_table(pd.DataFrame())
                return

            #υπολογισμός του score για να προτείνουμε κατάλληλα
            recommendations = recommend_courses(df=filtered_df)

            #εξονυχιστικό debugging
            if recommendations is None or recommendations.empty:
                messagebox.showinfo("No Results", "No matching recommendations found.")
            else:
                self.update_table(recommendations.head(3))
                self.show_all_btn.pack(side="left", padx=10)

        except Exception as e:
            messagebox.showerror("Error", f"Recommendation error: {str(e)}")


    def export_csv(self):
        """Εξάγει τα τρέχοντα δεδομένα σε νέο αρχείο CSV μέσω της save_to_csv"""
        try:
            # Έλεγχος αν υπάρχουν δεδομένα για εξαγωγή
            if self.df.empty:
                messagebox.showwarning("Warning", "No data available to export.")
                return
            # Κλήση της βοηθητικής συνάρτησης αποθήκευσης
            save_to_csv(self.df)
            messagebox.showinfo("Export Complete", "Current data successfully exported to a new CSV file!")
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def show_bar_chart(self):
        """Εμφανίζει bar chart με τα top-5 μαθήματα βάσει score"""
        try:
            bar_chart(top=5)  # top=5 για τα 5 καλύτερα μαθήματα
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_pie_chart(self):
        """Εμφανίζει pie chart με ποσοστιαία κατανομή κατηγοριών"""
        try:
            pie_chart()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_line_plot(self):
        """Εμφανίζει line plot με εξέλιξη δεδομένων ανά κατηγορία/δυσκολία"""
        try:
            line_plot()
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def reset_and_restart(self):
        """Διαγράφει το CSV, καθαρίζει την οθόνη και ξεκινά εκ νέου συλλογή"""

        # Παράθυρο επιβεβαίωσης — ο χρήστης πρέπει να πατήσει "Yes" για να συνεχίσει
        confirm = messagebox.askyesno(
            "Confirmation",
            "Are you sure you want to delete the previous CSV file and restart data collection from scratch?"
        )

        if confirm:
            try:
                # Έλεγχος αν υπάρχει το αρχείο πριν την απόπειρα διαγραφής
                if os.path.exists(self.csv_filename):
                    os.remove(self.csv_filename)  # οριστική διαγραφή του αρχείου
                    print(f"[CSV Manager] Status: Deleted existing file {self.csv_filename}")
                else:
                    # Αν δεν υπάρχει αρχείο, συνεχίζουμε κανονικά
                    print(f"[CSV Manager] Status: No file found to delete. Starting fresh.")

                # Επαναφορά του εσωτερικού DataFrame σε κενή κατάσταση
                self.df = pd.DataFrame()

                # Καθαρισμός του πίνακα στην οθόνη
                self.update_table(self.df)

                messagebox.showinfo("Reset Successful", "Previous data cleared. Starting new data collection...")
                print("[Reset & Restart] Executing fresh data collection...")

                # Λίστα για συγκέντρωση όλων των φρέσκων δεδομένων
                fresh_dfs = []

                # ── Συλλογή από APIs ──
                try:
                    df_devto = pd.concat([fetch_devto(term) for term in self.search_terms], ignore_index=True)
                    fresh_dfs.append(df_devto)
                except Exception: pass  # αγνοούμε αποτυχία μεμονωμένης πηγής

                try:
                    df_itunes = pd.concat([fetch_itunes(term) for term in self.search_terms], ignore_index=True)
                    fresh_dfs.append(df_itunes)
                except Exception: pass

                try:
                    df_github = pd.concat([fetch_github(term) for term in self.search_terms], ignore_index=True)
                    fresh_dfs.append(df_github)
                except Exception: pass

                # ── Συλλογή από Scrapers ──
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

                # Αν μαζεύτηκαν δεδομένα από τουλάχιστον μία πηγή, αποθήκευσέ τα
                if fresh_dfs:
                    # Ένωση όλων σε ένα DataFrame και παράδοση στη save_and_refresh_data
                    # που θα αναλάβει κανονικοποίηση, dedup και δημιουργία νέου CSV
                    merged_fresh = pd.concat(fresh_dfs, ignore_index=True)
                    self.save_and_refresh_data(merged_fresh)
                else:
                    # Αν όλες οι πηγές απέτυχαν, ενημερώνουμε τον χρήστη
                    messagebox.showwarning("Warning", "Could not fetch any new data after reset.")

            except Exception as e:
                messagebox.showerror("Error", f"An error occurred during reset: {str(e)}")