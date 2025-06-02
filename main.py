import tkinter as tk
from tkinter import ttk
from gui import WebScraperGUI

def main():
    root = tk.Tk()
    root.title("Web Scraper GUI")
    root.geometry("800x600")
    app = WebScraperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()