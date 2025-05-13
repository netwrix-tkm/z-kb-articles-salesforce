import os
import re
import shutil
from bs4 import BeautifulSoup
import html2text
from pathlib import Path
from datetime import datetime

def format_frontmatter_value(value):
    """Format a value for YAML frontmatter."""
    if isinstance(value, list):
        return f"[{', '.join(repr(item) for item in value)}]"
    elif isinstance(value, str):
        return f'"{value}"'
    return str(value)

def extract_metadata(html_content):
    """Extract metadata from HTML content and format for Docusaurus."""
    soup = BeautifulSoup(html_content, 'html.parser')
    metadata = {
        'id': '',  # Will be set from filename
        'title': '',
        'description': '',
        'sidebar_position': 1,
        'tags': [],
        'last_update': ''  # Will be set from metadata
    }
    
    # Extract title
    title = soup.find('title')
    if title:
        metadata['title'] = title.text.strip()
    
    # Extract meta tags
    for meta in soup.find_all('meta'):
        name = meta.get('name', meta.get('property', ''))
        content = meta.get('content', '')
        if name and content:
            if name.lower() in ['description', 'og:description']:
                metadata['description'] = content
            elif name.lower() in ['keywords', 'article:tag']:
                metadata['tags'] = [tag.strip() for tag in content.split(',')]
            elif name.lower() in ['last-modified', 'article:modified_time', 'og:updated_time']:
                try:
                    # Try to parse the date in various formats
                    date_str = content.split('T')[0]  # Take just the date part if it's ISO format
                    metadata['last_update'] = date_str
                except:
                    metadata['last_update'] = content
    
    # If no last_update was found, try to get it from the file's modification time
    if not metadata['last_update']:
        try:
            file_path = soup.find('meta', {'name': 'source-file'})
            if file_path:
                mtime = os.path.getmtime(file_path.get('content', ''))
                metadata['last_update'] = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
        except:
            pass
    
    return metadata

def process_images(html_content, source_dir, target_dir, doc_id):
    """Process images in HTML content and copy them to Docusaurus static directory."""
    soup = BeautifulSoup(html_content, 'html.parser')
    image_map = {}
    
    # Create images directory in static folder
    images_dir = os.path.join(target_dir, 'static', 'img', doc_id)
    os.makedirs(images_dir, exist_ok=True)
    
    # Find all images
    for img in soup.find_all('img'):
        src = img.get('src', '')
        if src:
            # Get absolute path of image
            if src.startswith(('http://', 'https://')):
                continue  # Skip external images
            
            # Handle relative paths
            img_path = os.path.normpath(os.path.join(source_dir, src))
            
            if os.path.exists(img_path):
                # Generate new image name
                img_name = os.path.basename(img_path)
                new_img_path = os.path.join(images_dir, img_name)
                
                # Copy image to new location
                shutil.copy2(img_path, new_img_path)
                
                # Update image path for Docusaurus
                new_src = f'/img/{doc_id}/{img_name}'
                img['src'] = new_src
                image_map[src] = new_src
    
    return str(soup), image_map

def convert_html_to_md(html_file, target_dir):
    """Convert HTML file to Docusaurus-compatible Markdown."""
    # Create target directory if it doesn't exist
    os.makedirs(target_dir, exist_ok=True)
    
    # Read HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Add source file path to HTML for metadata extraction
    soup = BeautifulSoup(html_content, 'html.parser')
    meta = soup.new_tag('meta')
    meta['name'] = 'source-file'
    meta['content'] = html_file
    soup.head.append(meta)
    html_content = str(soup)
    
    # Generate document ID from filename
    doc_id = os.path.splitext(os.path.basename(html_file))[0].lower()
    doc_id = re.sub(r'[^a-z0-9-]', '-', doc_id)
    
    # Extract metadata
    metadata = extract_metadata(html_content)
    metadata['id'] = doc_id
    
    # Process images
    source_dir = os.path.dirname(html_file)
    html_content, image_map = process_images(html_content, source_dir, target_dir, doc_id)
    
    # Convert HTML to Markdown
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    h.ignore_emphasis = False
    h.body_width = 0  # Don't wrap text
    markdown_content = h.handle(html_content)
    
    # Clean up markdown content
    markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content)  # Remove excessive newlines
    markdown_content = re.sub(r'\[([^\]]+)\]\(#\)', r'\1', markdown_content)  # Remove empty links
    
    # Add metadata at the top of the markdown file
    metadata_str = "---\n"
    for key, value in metadata.items():
        if value:  # Only include non-empty values
            metadata_str += f"{key}: {format_frontmatter_value(value)}\n"
    metadata_str += "---\n\n"
    
    markdown_content = metadata_str + markdown_content
    
    # Write markdown file
    md_filename = f"{doc_id}.mdx"  # Use .mdx extension for better compatibility
    
    # Get the product directory from the source path
    product_dir = os.path.basename(os.path.dirname(os.path.dirname(html_file)))
    md_path = os.path.join(target_dir, 'docs', product_dir, md_filename)
    os.makedirs(os.path.dirname(md_path), exist_ok=True)
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    return md_path

def main():
    # Create output directory structure
    output_dir = 'docusaurus_output'
    os.makedirs(os.path.join(output_dir, 'docs'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'static', 'img'), exist_ok=True)
    
    # Find all HTML files in onesecure directory
    html_files = []
    onesecure_dir = 'onesecure'
    if os.path.exists(onesecure_dir):
        for root, dirs, files in os.walk(onesecure_dir):
            for file in files:
                if file.endswith('.html'):
                    html_files.append(os.path.join(root, file))
    
    if not html_files:
        print(f"No HTML files found in {onesecure_dir} directory")
        return
        
    print(f"Found {len(html_files)} HTML files to convert in {onesecure_dir}")
    
    # Convert each file
    for index, html_file in enumerate(html_files, 1):
        try:
            print(f"\nProcessing file {index}/{len(html_files)}: {html_file}")
            md_file = convert_html_to_md(html_file, output_dir)
            print(f"✓ Converted to: {md_file}")
        except Exception as e:
            print(f"Error converting {html_file}: {str(e)}")
    
    print("\nConversion complete!")
    print("\nNext steps:")
    print("1. Copy the contents of 'docusaurus_output/docs' to your Docusaurus docs directory")
    print("2. Copy the contents of 'docusaurus_output/static' to your Docusaurus static directory")
    print("3. Update your Docusaurus configuration to include the new documents")

if __name__ == "__main__":
    main() 