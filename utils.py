import re
import os
import logging
from urllib.parse import urlparse
from bs4 import BeautifulSoup

# Configure logging
logger = logging.getLogger('web_scraper.utils')

def sanitize_folder_name(name):
    """Sanitize folder name by removing invalid characters"""
    # Remove invalid characters for folder names
    sanitized = re.sub(r'[\\/*?:"<>|]', '_', name)
    # Replace spaces with underscores
    sanitized = re.sub(r'\s+', '_', sanitized)
    # Remove any leading/trailing dots or spaces
    sanitized = sanitized.strip('. ')
    # Ensure the name is not empty
    if not sanitized:
        sanitized = "unnamed"
    return sanitized

def get_domain_from_url(url):
    """Extract domain from URL"""
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    # Remove www. prefix if present
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain

def extract_emails(text):
    """Extract email addresses from text"""
    # Regular expression for matching email addresses
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    # Remove duplicates and sort
    unique_emails = sorted(set(emails))
    logger.info(f"Extracted {len(unique_emails)} unique email addresses")
    return unique_emails

# This is a duplicate function that was already defined above
# Keeping this commented out to avoid confusion

# Add the missing functions
def extract_js_urls(html_content, base_url=None):
    """Extract JavaScript file URLs from HTML content.
    
    Args:
        html_content: HTML content as string or BeautifulSoup object
        base_url: Base URL for converting relative URLs to absolute URLs
    """
    # Check if html_content is a string or BeautifulSoup object
    if isinstance(html_content, str):
        # Use regex for string input
        js_pattern = r'<script[^>]*?src=["\']([^"\']*.js)["\'][^>]*?>'
        js_urls = re.findall(js_pattern, html_content)
    else:
        # Assume BeautifulSoup object
        soup = html_content
        js_urls = []
        # Find all script tags with src attribute
        for script in soup.find_all('script', src=True):
            js_url = script['src']
            js_urls.append(js_url)
    
    # Convert relative URLs to absolute URLs if base_url is provided
    if base_url:
        from urllib.parse import urljoin
        js_urls = [urljoin(base_url, url) for url in js_urls]
    
    # Remove duplicates
    unique_js_urls = list(set(js_urls))
    logger.info(f"Extracted {len(unique_js_urls)} JavaScript URLs")
    return unique_js_urls

def extract_meta_data(html_content):
    """Extract metadata from HTML content.
    
    Args:
        html_content: HTML content as string or BeautifulSoup object
    """
    meta_data = {
        'title': None,
        'description': None,
        'keywords': None,
        'author': None,
        'og_tags': {},
        'twitter_tags': {},
        'other_meta': {}
    }
    
    # Check if html_content is a string or BeautifulSoup object
    if isinstance(html_content, str):
        # Convert to BeautifulSoup object for easier parsing
        soup = BeautifulSoup(html_content, "html.parser")
    else:
        # Assume BeautifulSoup object
        soup = html_content
    
    # Extract title
    title_tag = soup.find('title')
    if title_tag:
        meta_data['title'] = title_tag.string
    
    # Extract meta tags
    for meta in soup.find_all('meta'):
        if meta.has_attr('name') and meta.has_attr('content'):
            name = meta['name'].lower()
            content = meta['content']
            
            if name == 'description':
                meta_data['description'] = content
            elif name == 'keywords':
                meta_data['keywords'] = content
            elif name == 'author':
                meta_data['author'] = content
            else:
                meta_data['other_meta'][name] = content
        
        # Extract Open Graph tags
        elif meta.has_attr('property') and meta.has_attr('content'):
            prop = meta['property'].lower()
            content = meta['content']
            
            if prop.startswith('og:'):
                meta_data['og_tags'][prop[3:]] = content
            elif prop.startswith('twitter:'):
                meta_data['twitter_tags'][prop[8:]] = content
    
    logger.info(f"Extracted metadata with {len(meta_data['other_meta'])} custom meta tags")
    return meta_data

def create_folder_structure(base_folder):
    """Create folder structure for saving scraped data"""
    folders = {
        'html': os.path.join(base_folder, 'html'),
        'css': os.path.join(base_folder, 'css'),
        'js': os.path.join(base_folder, 'js'),
        'images': os.path.join(base_folder, 'images'),
        'videos': os.path.join(base_folder, 'videos'),
        'data': os.path.join(base_folder, 'data')
    }
    
    # Create base folder
    os.makedirs(base_folder, exist_ok=True)
    
    # Create subfolders
    for folder_path in folders.values():
        os.makedirs(folder_path, exist_ok=True)
    
    logger.info(f"Created folder structure at {base_folder}")
    return folders

def extract_social_media(html_content):
    """Extract social media links from HTML content.
    
    Args:
        html_content: HTML content as string or BeautifulSoup object
    """
    # Check if html_content is a BeautifulSoup object and convert to string if needed
    if not isinstance(html_content, str):
        # Convert BeautifulSoup to string
        html_content = str(html_content)
    
    social_media_patterns = {
        'facebook': r'facebook\.com/[\w.-]+',
        'twitter': r'twitter\.com/[\w.-]+',
        'instagram': r'instagram\.com/[\w.-]+',
        'linkedin': r'linkedin\.com/(?:in|company)/[\w.-]+',
        'youtube': r'youtube\.com/(?:user|channel|c)/[\w.-]+',
        'pinterest': r'pinterest\.com/[\w.-]+',
        'github': r'github\.com/[\w.-]+',
        'tiktok': r'tiktok\.com/@[\w.-]+',
        'snapchat': r'snapchat\.com/add/[\w.-]+',
        'reddit': r'reddit\.com/(?:r|user)/[\w.-]+',
        'whatsapp': r'wa\.me/[\d]+',
        'telegram': r't\.me/[\w.-]+',
        'discord': r'discord\.gg/[\w.-]+',
        'medium': r'medium\.com/@[\w.-]+',
        'tumblr': r'[\w.-]+\.tumblr\.com',
        'flickr': r'flickr\.com/photos/[\w.-]+',
        'vimeo': r'vimeo\.com/[\w.-]+',
        'quora': r'quora\.com/profile/[\w.-]+',
        'twitch': r'twitch\.tv/[\w.-]+',
        'soundcloud': r'soundcloud\.com/[\w.-]+'
    }
    
    social_media_links = {}
    
    for platform, pattern in social_media_patterns.items():
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        if matches:
            # Remove duplicates and clean up URLs
            unique_matches = list(set(matches))
            # Add proper protocol if missing
            clean_matches = [f"https://{match}" if not match.startswith(('http://', 'https://')) else match for match in unique_matches]
            social_media_links[platform] = clean_matches
    
    logger.info(f"Extracted social media links from {len(social_media_links)} platforms")
    return social_media_links

def extract_css_urls(html_content, base_url=None):
    """Extract CSS file URLs from HTML content.
    
    Args:
        html_content: HTML content as string or BeautifulSoup object
        base_url: Base URL for converting relative URLs to absolute URLs
    """
    # Check if html_content is a string or BeautifulSoup object
    if isinstance(html_content, str):
        # Use regex for string input
        css_pattern = r'<link[^>]*?href=["\']([^"\']*.css)["\'][^>]*?>'
        css_urls = re.findall(css_pattern, html_content)
    else:
        # Assume BeautifulSoup object
        soup = html_content
        css_urls = []
        # Find all link tags with rel="stylesheet"
        for link in soup.find_all('link', rel="stylesheet"):
            if link.has_attr('href'):
                css_url = link['href']
                css_urls.append(css_url)
        
        # Find all style tags with src attribute
        for style in soup.find_all('style', src=True):
            css_url = style['src']
            css_urls.append(css_url)
    
    # Convert relative URLs to absolute URLs if base_url is provided
    if base_url:
        from urllib.parse import urljoin
        css_urls = [urljoin(base_url, url) for url in css_urls]
    
    # Remove duplicates
    unique_css_urls = list(set(css_urls))
    logger.info(f"Extracted {len(unique_css_urls)} CSS URLs")
    return unique_css_urls

def extract_phone_numbers(text):
    """Extract phone numbers from text.
    Matches various formats including international numbers.
    """
    # This pattern matches various phone number formats
    phone_pattern = r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
    return list(set(re.findall(phone_pattern, text)))