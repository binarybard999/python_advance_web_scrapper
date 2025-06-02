import requests
import random
import time
import os
import json
import logging
import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from constants import USER_AGENTS, PROXIES, ANTI_DETECTION_CONFIG, REFERRERS
from file_handler import save_html, save_links, save_media, save_text_data, save_json_data
from utils import (
    sanitize_folder_name, get_domain_from_url, extract_emails, extract_phone_numbers,
    extract_social_media, extract_css_urls, extract_js_urls, extract_meta_data,
    create_folder_structure
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('web_scraper')

def create_session(use_proxy=False, max_retries=3):
    """Create a requests session with retry capabilities and anti-detection measures"""
    session = requests.Session()
    
    # Configure retry strategy with exponential backoff
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=0.5,  # Exponential backoff
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Set default headers with random User-Agent
    session.headers.update({
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',  # Do Not Track
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
        'Referer': random.choice(REFERRERS) if REFERRERS else 'https://www.google.com/'
    })
    
    # Use proxy if specified
    if use_proxy and PROXIES:
        proxy = random.choice(PROXIES)
        session.proxies.update({
            'http': proxy,
            'https': proxy
        })
    
    return session

def scrape_website(url, save_folder, use_proxy=False, use_random_delay=True, max_retries=3):
    """Scrape website and save all data in organized folder structure.
    
    Args:
        url: The URL to scrape
        save_folder: Base folder to save data
        use_proxy: Whether to use proxy rotation
        use_random_delay: Whether to use random delays between requests
        max_retries: Maximum number of retry attempts
    """
    domain = get_domain_from_url(url)
    base_folder = os.path.join(save_folder, domain)
    
    # Create folder structure
    folders = create_folder_structure(base_folder)
    logger.info(f"Created folder structure at {base_folder}")
    
    # Initialize retry counter
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Create a session with anti-detection measures
            session = create_session(use_proxy, max_retries)
            logger.info(f"Starting to scrape: {url}")
            
            # Add a random delay between requests if enabled
            if use_random_delay:
                delay = random.uniform(2, 7)
                logger.info(f"Waiting for {delay:.2f} seconds before request")
                time.sleep(delay)

            # Make the request with session to maintain cookies
            response = session.get(url, timeout=30)
            response.raise_for_status()
            logger.info(f"Successfully fetched {url} (Status: {response.status_code})")

            # Parse HTML content
            html_content = response.text
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Save HTML to index.html in the base folder
            save_html(html_content, base_folder, "index.html")
            logger.info(f"Saved main HTML to {os.path.join(base_folder, 'index.html')}")
            
            # Save HTML to the html subfolder as well
            save_html(html_content, folders['html'], "main.html")

            # Extract and save links
            links = [urljoin(url, a.get("href")) for a in soup.find_all("a", href=True)]
            save_links(links, folders['data'], "links.txt")
            logger.info(f"Saved {len(links)} links")

            # Extract and save images
            images = [urljoin(url, img.get("src")) for img in soup.find_all("img", src=True)]
            save_media(images, folders['images'], ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", session=session)
            logger.info(f"Saved {len(images)} images")

            # Extract and save videos
            videos = [urljoin(url, video.get("src")) for video in soup.find_all("video", src=True)]
            videos.extend([urljoin(url, source.get("src")) for source in soup.find_all("source", src=True)])
            save_media(videos, folders['videos'], ".mp4", ".mov", ".avi", ".webm", ".ogg", session=session)
            logger.info(f"Saved {len(videos)} videos")
            
            # Extract and save CSS files
            css_urls = extract_css_urls(html_content)
            css_urls = [urljoin(url, css_url) for css_url in css_urls]
            save_media(css_urls, folders['css'], ".css", session=session)
            logger.info(f"Saved {len(css_urls)} CSS files")
            
            # Extract and save JavaScript files
            js_urls = extract_js_urls(html_content)
            js_urls = [urljoin(url, js_url) for js_url in js_urls]
            save_media(js_urls, folders['js'], ".js", session=session)
            logger.info(f"Saved {len(js_urls)} JavaScript files")
            
            # Extract and save emails
            emails = extract_emails(html_content)
            save_text_data(emails, os.path.join(folders['data'], "emails.txt"))
            logger.info(f"Saved {len(emails)} email addresses")
            
            # Extract and save phone numbers
            phone_numbers = extract_phone_numbers(html_content)
            save_text_data(phone_numbers, os.path.join(folders['data'], "phone_numbers.txt"))
            logger.info(f"Saved {len(phone_numbers)} phone numbers")
            
            # Extract and save social media links
            social_media = extract_social_media(html_content)
            with open(os.path.join(folders['data'], "social_media.json"), "w", encoding="utf-8") as f:
                json.dump(social_media, f, indent=4)
            logger.info(f"Saved social media links")
            
            # Extract and save meta data
            meta_data = extract_meta_data(html_content)
            with open(os.path.join(folders['data'], "meta_data.json"), "w", encoding="utf-8") as f:
                json.dump(meta_data, f, indent=4)
            logger.info(f"Saved website metadata")
            
            # Create a summary file
            create_summary_file(base_folder, {
                'url': url,
                'domain': domain,
                'links_count': len(links),
                'images_count': len(images),
                'videos_count': len(videos),
                'css_files_count': len(css_urls),
                'js_files_count': len(js_urls),
                'emails_count': len(emails),
                'phone_numbers_count': len(phone_numbers),
                'social_media': social_media.keys(),
                'meta_data': meta_data
            })
            logger.info(f"Created summary file at {os.path.join(base_folder, 'summary.md')}")
            
            return base_folder
            
        except requests.exceptions.RequestException as e:
            retry_count += 1
            logger.warning(f"Request error (attempt {retry_count}/{max_retries}): {str(e)}")
            if retry_count >= max_retries:
                logger.error(f"Failed to scrape {url} after {max_retries} attempts: {str(e)}")
                raise Exception(f"Failed to scrape {url} after {max_retries} attempts: {str(e)}")
            
            # Exponential backoff for retries
            wait_time = 2 ** retry_count
            logger.info(f"Waiting {wait_time} seconds before retry")
            time.sleep(wait_time)
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {str(e)}")
            raise Exception(f"Failed to scrape {url}: {str(e)}")

def create_summary_file(base_folder, data):
    """Create a summary file with information about the scraped data."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    summary = f"""# Website Scraping Summary

URL: {data['url']}
Domain: {data['domain']}
Scraped on: {timestamp}

## Statistics
- Links: {data['links_count']}
- Images: {data['images_count']}
- Videos: {data['videos_count']}
- CSS Files: {data['css_files_count']}
- JavaScript Files: {data['js_files_count']}
- Emails: {data['emails_count']}
- Phone Numbers: {data['phone_numbers_count']}
- Social Media Platforms: {', '.join(data['social_media']) if data['social_media'] else 'None'}

## Meta Data
- Title: {data['meta_data'].get('title', 'N/A')}
- Description: {data['meta_data'].get('description', 'N/A')}
- Keywords: {data['meta_data'].get('keywords', 'N/A')}

## Folder Structure
- /html - HTML files
- /css - CSS files
- /js - JavaScript files
- /images - Image files
- /videos - Video files
- /data - Extracted data (links, emails, phone numbers, etc.)
"""
    
    with open(os.path.join(base_folder, "summary.md"), "w", encoding="utf-8") as f:
        f.write(summary)