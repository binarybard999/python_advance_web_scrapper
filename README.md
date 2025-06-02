# Advanced Web Scraper

This is an advanced web scraping tool designed to extract various types of data from websites, including HTML content, links, images, videos, CSS files, JavaScript files, emails, phone numbers, social media links, and metadata. It features anti-detection measures to improve scraping reliability.

## Features

- **Comprehensive Data Extraction**: Scrapes HTML, links, images, videos, CSS, JS, emails, phone numbers, social media, and metadata.
- **Anti-Detection Measures**: Includes User-Agent rotation, random delays, and proxy support to avoid being blocked.
- **Organized Output**: Saves scraped data into a well-structured folder system.
- **Summary Report**: Generates a `summary.md` file with statistics and extracted metadata for each scraped website.
- **User-Friendly GUI**: Provides a graphical interface for easy interaction.

## Installation

To get started with the Web Scraper, follow these steps:

1.  **Clone the repository (if applicable) or download the project files.**

2.  **Navigate to the project directory.**

3.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    ```

4.  **Activate the virtual environment:**
    *   **On Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    *   **On macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```

5.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To run the web scraper, execute the `main.py` file:

```bash
python main.py
```

This will launch the graphical user interface (GUI).

### GUI Instructions:

1.  **URL Input Tab**:
    *   Enter the full URL of the website you want to scrape (e.g., `https://example.com`).
    *   Click "Start Scraping" to begin the process.
    *   Click "Stop" to halt an ongoing scraping process.

2.  **Save Settings Tab**:
    *   Choose the directory where you want to save the scraped data. By default, it saves in the current project directory.
    *   Review the preview of the folder structure that will be created for each scraped website.
    *   Optionally, check "Open folder after scraping completes" to automatically open the output directory.

3.  **Scraping Options Tab**:
    *   **Anti-Detection Settings**:
        *   `Rotate User-Agent headers`: Enable/disable rotation of User-Agent strings to mimic different browsers.
        *   `Use random delays between requests`: Enable/disable random pauses between requests to avoid detection.
        *   `Use proxy rotation`: (Requires configuration in `constants.py`) Enable/disable proxy usage.
        *   `Max retry attempts`: Set the number of times the scraper will retry a failed request.
    *   **Scraping Depth**:
        *   Set the depth for link traversal (0 = current page only, 1 = current page + linked pages, etc.). Be cautious with deeper scraping as it can take a long time and may trigger anti-scraping measures.
    *   **Data Extraction Options**:
        *   Select which types of data you want to extract (emails, phone numbers, social media, images, CSS/JS files).

4.  **Log Tab**:
    *   View real-time logs of the scraping process, including information, warnings, and errors.

## Project Structure

```
web_scrapper/
├── main.py             # Main entry point for the GUI application
├── gui.py              # Implements the Tkinter GUI
├── scraper.py          # Core scraping logic and data extraction
├── file_handler.py     # Handles saving of various file types (HTML, media, data)
├── utils.py            # Utility functions for URL parsing, data extraction (emails, social media, meta data, CSS/JS URLs)
├── constants.py        # Configuration for User-Agents, proxies, and anti-detection settings
├── requirements.txt    # List of Python dependencies
└── README.md           # This file
```

## Responsibilities and Ethical Use

Please be aware of your responsibilities when using this web scraper:

*   **Respect `robots.txt`**: Always check and respect the `robots.txt` file of any website you intend to scrape. This file provides guidelines on what parts of a website should not be accessed by bots.
*   **Terms of Service**: Adhere to the Terms of Service of the websites you scrape. Many websites prohibit automated scraping.
*   **Rate Limiting**: Implement appropriate delays and rate limits to avoid overwhelming website servers. Excessive requests can be seen as a Denial-of-Service (DoS) attack. This tool includes random delays, but you should adjust them based on the target website's policies.
*   **Data Privacy**: Be mindful of privacy laws and regulations (e.g., GDPR, CCPA) when collecting and storing personal data. Do not collect sensitive information without explicit consent.
*   **Legal Compliance**: Ensure your scraping activities comply with all applicable local, national, and international laws.
*   **Non-Malicious Use**: This tool is intended for legitimate purposes such as data analysis, research, and personal archiving. Do not use it for any illegal, unethical, or malicious activities.

**Disclaimer**: The developer of this tool is not responsible for any misuse or illegal activities conducted by users. Users are solely responsible for ensuring their scraping activities are legal and ethical.