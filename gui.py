import os
import tkinter as tk
import threading
import webbrowser
from tkinter import ttk, filedialog, scrolledtext
from scraper import scrape_website
from utils import sanitize_folder_name, get_domain_from_url
from constants import ANTI_DETECTION_CONFIG

class WebScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Web Scraper")
        
        # Set icon if available
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
            
        # Configure style
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#ccc")
        self.style.configure("TLabel", font=("Helvetica", 10))
        self.style.configure("Header.TLabel", font=("Helvetica", 12, "bold"))
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10 10 10 10")
        self.main_frame.pack(fill="both", expand=True)
        
        # Create notebook for tabs
        self.tabs = ttk.Notebook(self.main_frame)
        self.tabs.pack(fill="both", expand=True)

        # Create tabs
        self.create_url_tab()
        self.create_save_tab()
        self.create_options_tab()
        self.create_log_tab()
        
        # Status bar at the bottom
        self.status_frame = ttk.Frame(root, relief="sunken", padding="2 2 2 2")
        self.status_frame.pack(side="bottom", fill="x")
        
        self.status_label = ttk.Label(self.status_frame, text="Ready", anchor="w")
        self.status_label.pack(side="left", fill="x", expand=True)
        
        self.progress_bar = ttk.Progressbar(self.status_frame, mode="indeterminate", length=100)
        self.progress_bar.pack(side="right", padx=5)
        
        # Initialize variables
        self.scraping_thread = None
        self.stop_scraping = False
        self.current_save_folder = None

    def create_url_tab(self):
        url_frame = ttk.Frame(self.tabs, padding="10 10 10 10")
        self.tabs.add(url_frame, text="URL Input")
        
        # URL input section
        url_label = ttk.Label(url_frame, text="Enter Website URL:", style="Header.TLabel")
        url_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        url_description = ttk.Label(url_frame, text="Enter the full URL of the website you want to scrape (including http:// or https://)", wraplength=500)
        url_description.grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 10))

        self.url_entry = ttk.Entry(url_frame, width=70)
        self.url_entry.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)
        self.url_entry.focus()
        
        # URL examples
        examples_label = ttk.Label(url_frame, text="Examples: https://example.com, https://news.ycombinator.com")
        examples_label.grid(row=3, column=0, columnspan=3, sticky="w", pady=(0, 20))
        
        # Action buttons
        button_frame = ttk.Frame(url_frame)
        button_frame.grid(row=4, column=0, columnspan=3, sticky="w")
        
        self.fetch_button = ttk.Button(button_frame, text="Start Scraping", command=self.start_scraping_thread)
        self.fetch_button.pack(side="left", padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_scraping_thread, state="disabled")
        self.stop_button.pack(side="left")
        
        # Status message
        self.url_status_label = ttk.Label(url_frame, text="", foreground="green")
        self.url_status_label.grid(row=5, column=0, columnspan=3, sticky="w", pady=10)
        
        # Configure grid
        url_frame.columnconfigure(0, weight=1)

    def create_save_tab(self):
        save_frame = ttk.Frame(self.tabs, padding="10 10 10 10")
        self.tabs.add(save_frame, text="Save Settings")
        
        # Save path section
        save_label = ttk.Label(save_frame, text="Save Location:", style="Header.TLabel")
        save_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        save_description = ttk.Label(save_frame, text="Choose where to save the scraped data. If not specified, data will be saved in the current directory.", wraplength=500)
        save_description.grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 10))
        
        # Default to the directory where the script is located
        default_path = os.path.dirname(os.path.abspath(__file__))
        self.save_path = tk.StringVar(value=default_path)
        
        path_frame = ttk.Frame(save_frame)
        path_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=5)
        
        self.save_path_entry = ttk.Entry(path_frame, width=60, textvariable=self.save_path)
        self.save_path_entry.pack(side="left", fill="x", expand=True)
        
        self.browse_button = ttk.Button(path_frame, text="Browse...", command=self.browse_save_path)
        self.browse_button.pack(side="right", padx=(5, 0))
        
        # Folder structure preview
        preview_label = ttk.Label(save_frame, text="Folder Structure Preview:", style="Header.TLabel")
        preview_label.grid(row=3, column=0, sticky="w", pady=(20, 5))
        
        preview_frame = ttk.Frame(save_frame, relief="sunken", padding=10)
        preview_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=5)
        
        preview_text = """When you scrape a website (e.g., example.com), the following folder structure will be created:

/example.com/
  ├── index.html           # Main HTML file
  ├── summary.md           # Summary of scraped data
  ├── html/                # HTML files
  ├── css/                 # CSS files
  ├── js/                  # JavaScript files
  ├── images/              # Image files
  ├── videos/              # Video files
  └── data/                # Extracted data
      ├── links.txt        # All links found
      ├── emails.txt       # Extracted email addresses
      ├── phone_numbers.txt # Extracted phone numbers
      ├── social_media.json # Social media links
      └── meta_data.json   # Website metadata
"""
        
        preview = ttk.Label(preview_frame, text=preview_text, justify="left", font=("Courier", 9))
        preview.pack(fill="both")
        
        # Open folder option
        self.open_folder_var = tk.BooleanVar(value=True)
        open_folder_check = ttk.Checkbutton(save_frame, text="Open folder after scraping completes", variable=self.open_folder_var)
        open_folder_check.grid(row=5, column=0, sticky="w", pady=(10, 0))
        
        # Configure grid
        save_frame.columnconfigure(0, weight=1)

    def create_options_tab(self):
        options_frame = ttk.Frame(self.tabs, padding="10 10 10 10")
        self.tabs.add(options_frame, text="Scraping Options")
        
        # Anti-detection options
        anti_label = ttk.Label(options_frame, text="Anti-Detection Settings:", style="Header.TLabel")
        anti_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        anti_description = ttk.Label(options_frame, text="Configure settings to avoid being detected and blocked by websites.", wraplength=500)
        anti_description.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        # User agent rotation
        self.rotate_user_agent_var = tk.BooleanVar(value=ANTI_DETECTION_CONFIG["rotate_user_agent"])
        rotate_user_agent_check = ttk.Checkbutton(options_frame, text="Rotate User-Agent headers", variable=self.rotate_user_agent_var)
        rotate_user_agent_check.grid(row=2, column=0, sticky="w", pady=2)
        
        # Random delays
        self.random_delay_var = tk.BooleanVar(value=True)
        random_delay_check = ttk.Checkbutton(options_frame, text="Use random delays between requests", variable=self.random_delay_var)
        random_delay_check.grid(row=3, column=0, sticky="w", pady=2)
        
        # Proxy usage
        self.use_proxy_var = tk.BooleanVar(value=ANTI_DETECTION_CONFIG["use_proxy"])
        use_proxy_check = ttk.Checkbutton(options_frame, text="Use proxy rotation (requires configuration in constants.py)", variable=self.use_proxy_var)
        use_proxy_check.grid(row=4, column=0, sticky="w", pady=2)
        
        # Retry settings
        retry_frame = ttk.Frame(options_frame)
        retry_frame.grid(row=5, column=0, sticky="w", pady=5)
        
        retry_label = ttk.Label(retry_frame, text="Max retry attempts:")
        retry_label.pack(side="left")
        
        self.max_retries_var = tk.IntVar(value=ANTI_DETECTION_CONFIG["max_retries"])
        retry_spinbox = ttk.Spinbox(retry_frame, from_=1, to=10, width=5, textvariable=self.max_retries_var)
        retry_spinbox.pack(side="left", padx=5)
        
        # Scraping depth
        depth_frame = ttk.Frame(options_frame)
        depth_frame.grid(row=6, column=0, sticky="w", pady=5)
        
        depth_label = ttk.Label(depth_frame, text="Scraping depth (0 = current page only):")
        depth_label.pack(side="left")
        
        self.scrape_depth_var = tk.IntVar(value=0)
        depth_spinbox = ttk.Spinbox(depth_frame, from_=0, to=3, width=5, textvariable=self.scrape_depth_var)
        depth_spinbox.pack(side="left", padx=5)
        
        # Warning about deep scraping
        depth_warning = ttk.Label(options_frame, text="Note: Deeper scraping may take significantly longer and could trigger anti-scraping measures.", foreground="red", wraplength=500)
        depth_warning.grid(row=7, column=0, columnspan=2, sticky="w", pady=5)
        
        # Data extraction options
        extract_label = ttk.Label(options_frame, text="Data Extraction Options:", style="Header.TLabel")
        extract_label.grid(row=8, column=0, sticky="w", pady=(20, 5))
        
        # Checkboxes for different data types
        self.extract_emails_var = tk.BooleanVar(value=True)
        extract_emails_check = ttk.Checkbutton(options_frame, text="Extract email addresses", variable=self.extract_emails_var)
        extract_emails_check.grid(row=9, column=0, sticky="w", pady=2)
        
        self.extract_phones_var = tk.BooleanVar(value=True)
        extract_phones_check = ttk.Checkbutton(options_frame, text="Extract phone numbers", variable=self.extract_phones_var)
        extract_phones_check.grid(row=10, column=0, sticky="w", pady=2)
        
        self.extract_social_var = tk.BooleanVar(value=True)
        extract_social_check = ttk.Checkbutton(options_frame, text="Extract social media links", variable=self.extract_social_var)
        extract_social_check.grid(row=11, column=0, sticky="w", pady=2)
        
        self.download_images_var = tk.BooleanVar(value=True)
        download_images_check = ttk.Checkbutton(options_frame, text="Download images", variable=self.download_images_var)
        download_images_check.grid(row=12, column=0, sticky="w", pady=2)
        
        self.download_css_js_var = tk.BooleanVar(value=True)
        download_css_js_check = ttk.Checkbutton(options_frame, text="Download CSS and JavaScript files", variable=self.download_css_js_var)
        download_css_js_check.grid(row=13, column=0, sticky="w", pady=2)
        
        # Configure grid
        options_frame.columnconfigure(0, weight=1)

    def create_log_tab(self):
        log_frame = ttk.Frame(self.tabs, padding="10 10 10 10")
        self.tabs.add(log_frame, text="Log")
        
        # Log viewer
        log_label = ttk.Label(log_frame, text="Scraping Log:", style="Header.TLabel")
        log_label.pack(anchor="w", pady=(0, 5))
        
        # Create scrolled text widget for logs
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, width=80, wrap=tk.WORD)
        self.log_text.pack(fill="both", expand=True, pady=5)
        self.log_text.config(state="disabled")
        
        # Buttons for log actions
        button_frame = ttk.Frame(log_frame)
        button_frame.pack(fill="x", pady=5)
        
        clear_log_button = ttk.Button(button_frame, text="Clear Log", command=self.clear_log)
        clear_log_button.pack(side="left", padx=(0, 5))
        
        save_log_button = ttk.Button(button_frame, text="Save Log", command=self.save_log)
        save_log_button.pack(side="left")

    def browse_save_path(self):
        path = filedialog.askdirectory(initialdir=self.save_path.get())
        if path:
            self.save_path.set(path)

    def log_message(self, message, level="INFO"):
        """Add a message to the log tab"""
        self.log_text.config(state="normal")
        
        # Add timestamp and level
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Set color based on level
        if level == "ERROR":
            tag = "error"
            self.log_text.tag_config(tag, foreground="red")
        elif level == "WARNING":
            tag = "warning"
            self.log_text.tag_config(tag, foreground="orange")
        elif level == "SUCCESS":
            tag = "success"
            self.log_text.tag_config(tag, foreground="green")
        else:  # INFO
            tag = "info"
            self.log_text.tag_config(tag, foreground="black")
        
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        self.log_text.insert(tk.END, log_entry, tag)
        self.log_text.see(tk.END)  # Scroll to the end
        self.log_text.config(state="disabled")
        
        # Update status bar as well
        self.status_label.config(text=message)

    def clear_log(self):
        """Clear the log text widget"""
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")

    def save_log(self):
        """Save the log to a file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Log As"
        )
        
        if file_path:
            try:
                self.log_text.config(state="normal")
                log_content = self.log_text.get(1.0, tk.END)
                self.log_text.config(state="disabled")
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(log_content)
                    
                self.log_message(f"Log saved to {file_path}", "SUCCESS")
            except Exception as e:
                self.log_message(f"Error saving log: {str(e)}", "ERROR")

    def start_scraping_thread(self):
        """Start scraping in a separate thread to keep UI responsive"""
        url = self.url_entry.get().strip()
        if not url:
            self.url_status_label.config(text="Please enter a URL", foreground="red")
            self.log_message("No URL provided", "ERROR")
            return
            
        # Add http:// if missing
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, url)
        
        # Disable UI elements during scraping
        self.fetch_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.progress_bar.start(10)
        
        # Reset stop flag
        self.stop_scraping = False
        
        # Start scraping in a separate thread
        self.scraping_thread = threading.Thread(target=self.fetch_website)
        self.scraping_thread.daemon = True
        self.scraping_thread.start()

    def stop_scraping_thread(self):
        """Signal the scraping thread to stop"""
        if self.scraping_thread and self.scraping_thread.is_alive():
            self.stop_scraping = True
            self.log_message("Stopping scraping process...", "WARNING")
            self.status_label.config(text="Stopping scraping process...")

    def fetch_website(self):
        """Fetch website data (runs in a separate thread)"""
        url = self.url_entry.get().strip()
        
        try:
            # Update UI
            self.root.after(0, lambda: self.url_status_label.config(text="Scraping in progress...", foreground="blue"))
            self.log_message(f"Starting to scrape: {url}", "INFO")
            
            # Get domain and create save folder
            domain = get_domain_from_url(url)
            save_folder = os.path.join(self.save_path.get(), sanitize_folder_name(domain))
            self.current_save_folder = save_folder
            
            self.log_message(f"Data will be saved to: {save_folder}", "INFO")
            
            # Get options from UI
            options = {
                "use_proxy": self.use_proxy_var.get(),
                "use_random_delay": self.random_delay_var.get(),
                "max_retries": self.max_retries_var.get(),
                "scrape_depth": self.scrape_depth_var.get(),
                "extract_emails": self.extract_emails_var.get(),
                "extract_phones": self.extract_phones_var.get(),
                "extract_social": self.extract_social_var.get(),
                "download_images": self.download_images_var.get(),
                "download_css_js": self.download_css_js_var.get()
            }
            
            # Call the scraper function
            result_folder = scrape_website(
                url, 
                save_folder, 
                use_proxy=options["use_proxy"],
                use_random_delay=options["use_random_delay"],
                max_retries=options["max_retries"]
            )
            
            # Update UI with success message
            if not self.stop_scraping:
                self.root.after(0, lambda: self.url_status_label.config(
                    text="Website scraped and saved successfully!", 
                    foreground="green"
                ))
                self.log_message("Scraping completed successfully", "SUCCESS")
                
                # Open the folder if option is selected
                if self.open_folder_var.get():
                    self.root.after(0, lambda: self.open_result_folder(result_folder))
        except Exception as e:
            # Update UI with error message
            error_msg = str(e)
            self.root.after(0, lambda: self.url_status_label.config(
                text=f"Error: {error_msg}", 
                foreground="red"
            ))
            self.log_message(f"Error: {error_msg}", "ERROR")
        finally:
            # Re-enable UI elements
            self.root.after(0, self.reset_ui)

    def reset_ui(self):
        """Reset UI elements after scraping is done"""
        self.fetch_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.progress_bar.stop()

    def open_result_folder(self, folder_path):
        """Open the result folder in file explorer"""
        try:
            if os.path.exists(folder_path):
                # Use the appropriate command based on the OS
                if os.name == 'nt':  # Windows
                    os.startfile(folder_path)
                elif os.name == 'posix':  # macOS and Linux
                    import subprocess
                    subprocess.Popen(['xdg-open', folder_path])
                self.log_message(f"Opened folder: {folder_path}", "INFO")
            else:
                self.log_message(f"Folder not found: {folder_path}", "WARNING")
        except Exception as e:
            self.log_message(f"Error opening folder: {str(e)}", "ERROR")