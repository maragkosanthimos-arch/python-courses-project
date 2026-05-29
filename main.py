import tkinter as tk
from gui.app import CourseGUI  # Κάνουμε import τη σωστή κλάση από το app.py

if __name__ == "__main__":
    root = tk.Tk()
    app = CourseGUI(root)   # Αρχικοποίηση της κλάσης
    root.mainloop()
