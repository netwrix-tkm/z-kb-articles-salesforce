import os
import re
from bs4 import BeautifulSoup
import shutil

def get_product_from_meta(soup):
    # Find all meta tags with name="label"
    meta_tags = soup.find_all('meta', attrs={'name': 'label'})
    if meta_tags:
        # Get all label values
        labels = [tag.get('content') for tag in meta_tags if tag.get('content')]
        
        # Map the product label to directory
        product_dirs = {
            'data_classification': 'data_classification',
            'auditor': 'auditor',
            'activity_monitor': 'access_analyzer',
            'threat_management': 'threat_management',
            'platform_governance': 'platform_governance',
            'endpoint_protector': 'endpoint_management/endpoint_protector',
            'vulnerability_tracker': 'vulnerability_tracker',
            'recovery_ad': 'recovery_ad',
            'onesecure': 'onesecure',
            'log_tracker': 'log_tracker',
            'identity_manager': 'identity_manager',
            'change_tracker': 'change_tracker',
            'access_analyzer': 'access_analyzer',
            'directory_manager': 'directory_manager',
            'privilege_secure': 'privilege_secure',
            'password_secure': 'password_management/password_secure',
            'password_reset': 'password_management/password_reset',
            'password_policy': 'password_management/password_policy_enforcer',
            'groupid': 'directory_manager',
            'usercube': 'identity_manager',
            'threat_prevention': 'threat_management/threat_prevention',
            'threat_manager': 'threat_management/threat_manager',
            'enterprise_auditor': 'access_analyzer'
        }
        
        # Check each label for a matching product
        for label in labels:
            if label in product_dirs:
                return product_dirs[label]
    return 'other'  # Return 'other' instead of None for uncategorized articles

def find_image_file(image_name):
    """Search recursively for an image file in all directories."""
    for root, dirs, files in os.walk('.'):
        if image_name in files:
            return os.path.join(root, image_name)
    return None

def organize_articles():
    # Recursively find all HTML files
    html_files = []
    for root, dirs, files in os.walk('.'):
        for f in files:
            if f.endswith('.html'):
                html_files.append(os.path.join(root, f))
    
    for html_path in html_files:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        soup = BeautifulSoup(content, 'html.parser')
        product_dir = get_product_from_meta(soup)
        
        # Create the product directory if it doesn't exist
        os.makedirs(product_dir, exist_ok=True)
        
        # Create a subfolder for the article inside the product directory
        html_filename = os.path.basename(html_path)
        article_name = os.path.splitext(html_filename)[0]
        article_folder = os.path.join(product_dir, article_name)
        os.makedirs(article_folder, exist_ok=True)
        
        # Move the HTML file into the article folder
        new_html_path = os.path.join(article_folder, html_filename)
        shutil.move(html_path, new_html_path)
        
        # Find all image sources in the HTML
        img_srcs = set()
        for img in soup.find_all('img'):
            src = img.get('src')
            if src and not src.lower().startswith(('http://', 'https://', 'data:')):
                img_srcs.add(os.path.basename(src))
        
        # Move each image file into the article folder if it exists
        for img_name in img_srcs:
            # Search for the image file in all directories
            img_path = find_image_file(img_name)
            if img_path:
                print(f"Found image {img_name} at {img_path}")
                shutil.move(img_path, os.path.join(article_folder, img_name))
                print(f"Moved image to {article_folder}/")
            else:
                print(f"Image file not found: {img_name}")
        
        print(f"Organized {html_filename} and its images into {article_folder}/")

if __name__ == "__main__":
    organize_articles() 