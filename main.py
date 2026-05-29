import tkinter as tk
from gui.app import CourseGUI  # import

if __name__ == "__main__":
    root = tk.Tk()
    app = CourseGUI(root)   #αρχικοποίηση κλάσης
    root.mainloop()         
