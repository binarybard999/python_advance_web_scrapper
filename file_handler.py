import os
import requests
import random
import time
import logging
import json
import re
import hashlib
from urllib.parse import urlparse, unquote
from constants import USER_AGENTS, ANTI_DETECTION_CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('file_handler')

def get_safe_filename(url, default_extension=None):
    """Generate a safe filename from a URL"""
    try:
        # Try to get the filename from the URL path
        parsed_url = urlparse(url)
        path = unquote(parsed_url.path)
        filename = os.path.basename(path)
        
        # If no filename could be extracted, hash the URL
        if not filename or filename == '/' or '.' not in filename:
            url_hash = hashlib.md5(url.encode()).hexdigest()[:10]
            extension = os.path.splitext(path)[1] or default_extension or '.bin'
            if not extension.startswith('.'):
                extension = '.' + extension
            filename = f"file_{url_hash}{extension}"
            
        # Remove any potentially problematic characters
        filename = ''.join(c for c in filename if c.isalnum() or c in '._-')
        
        # Ensure filename is not too long
        if len(filename) > 100:
            name, ext = os.path.splitext(filename)
            filename = name[:90] + ext
            
        return filename
    except Exception:
        # Fallback to a simple hash if anything goes wrong
        return f"file_{hashlib.md5(url.encode()).hexdigest()[:10]}.bin"

def save_html(html_content, save_folder, filename):
    """Save HTML content to a file.
    
    Args:
        html_content: The HTML content to save
        save_folder: The folder to save the file in
        filename: The name of the file
    """
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
        
    file_path = os.path.join(save_folder, filename)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        logger.info(f"Saved HTML to {file_path}")
        time.sleep(random.uniform(0.1, 0.5))  # Small delay after saving
        return file_path
    except Exception as e:
        logger.error(f"Failed to save HTML to {file_path}: {e}")

def save_links(links, save_folder, filename):
    """Save links to a file.
    
    Args:
        links: List of links to save
        save_folder: The folder to save the file in
        filename: The name of the file
    """
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
        
    file_path = os.path.join(save_folder, filename)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            for link in links:
                f.write(link + "\n")
        logger.info(f"Saved {len(links)} links to {file_path}")
        time.sleep(random.uniform(0.1, 0.5))  # Small delay after saving
        return file_path
    except Exception as e:
        logger.error(f"Failed to save links to {file_path}: {e}")

def save_text_data(data_list, file_path):
    """Save text data to a file.
    
    Args:
        data_list: List of text data to save
        file_path: The full path to the file
    """
    if not data_list:
        logger.info(f"No data to save to {file_path}")
        return
        
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            for item in data_list:
                f.write(str(item) + "\n")
        logger.info(f"Saved {len(data_list)} items to {file_path}")
        time.sleep(random.uniform(0.1, 0.5))  # Small delay after saving
        return file_path
    except Exception as e:
        logger.error(f"Failed to save data to {file_path}: {e}")

def save_media(urls, save_folder, *extensions, session=None):
    """Save media files from URLs.
    
    Args:
        urls: List of URLs to download media from
        save_folder: The folder to save files in
        extensions: File extensions to filter by (e.g., '.jpg', '.png')
        session: Optional requests session to use
    """
    if not urls:
        logger.info(f"No URLs to download for {save_folder}")
        return []
        
    # Ensure the save folder exists
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # Create a session if not provided
    if session is None:
        session = requests.Session()
        session.headers.update({
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        })

    success_count = 0
    saved_files = []
    
    for url in urls:
        try:
            # Skip URLs that don't have the right extension if extensions are specified
            if extensions:
                file_ext = os.path.splitext(url)[1].lower()
                if not any(file_ext.endswith(ext.lower()) for ext in extensions):
                    continue

            # Set headers with more realistic browser behavior
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": url,  # Set the URL as the referer to appear more legitimate
                "DNT": "1"  # Do Not Track
            }
            
            # Add specific headers based on file type
            if any(url.lower().endswith(ext) for ext in ('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                headers["Accept"] = "image/webp,image/apng,image/*,*/*;q=0.8"
            elif any(url.lower().endswith(ext) for ext in ('.css')):
                headers["Accept"] = "text/css,*/*;q=0.1"
            elif any(url.lower().endswith(ext) for ext in ('.js')):
                headers["Accept"] = "*/*"
                
            # Make the request with a timeout
            response = session.get(url, headers=headers, timeout=15, stream=True)
            response.raise_for_status()

            # Generate a safe filename
            filename = get_safe_filename(url)
            file_path = os.path.join(save_folder, filename)
            
            # Save the file
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        
            success_count += 1
            saved_files.append(file_path)
            logger.info(f"Saved {url} to {file_path}")
            
            # Add a random delay between requests to avoid being blocked
            time.sleep(random.uniform(1, 3))
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to download {url}: {e}")
        except Exception as e:
            logger.error(f"Error saving {url}: {e}")
            
    logger.info(f"Successfully downloaded {success_count} out of {len(urls)} files to {save_folder}")
    return saved_files

def save_json_data(data, save_folder, filename):
    """Save JSON data to a file.
    
    Args:
        data: The data to save as JSON
        save_folder: The folder to save the file in
        filename: The name of the file
    """
    import json
    
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
        
    file_path = os.path.join(save_folder, filename)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logger.info(f"Saved JSON data to {file_path}")
        time.sleep(random.uniform(0.1, 0.5))  # Small delay after saving
        return file_path
    except Exception as e:
        logger.error(f"Failed to save JSON data to {file_path}: {e}")