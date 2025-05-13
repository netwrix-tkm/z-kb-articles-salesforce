import os
import subprocess
import sys
import time

def format_html_files():
    # Find all HTML files recursively
    html_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    
    total_files = len(html_files)
    print(f"Found {total_files} HTML files to format")
    
    # Format each file
    for index, html_file in enumerate(html_files, 1):
        try:
            print(f"\nProcessing file {index}/{total_files}: {html_file}")
            start_time = time.time()
            
            # Run prettier on the file using the full path to npx
            result = subprocess.run(
                [r'C:\Program Files\nodejs\npx.cmd', 'prettier', '--write', html_file],
                check=True,
                capture_output=True,
                text=True
            )
            
            end_time = time.time()
            print(f"✓ Formatted in {end_time - start_time:.2f} seconds")
            
        except subprocess.CalledProcessError as e:
            print(f"Error formatting {html_file}:")
            print(f"Error code: {e.returncode}")
            print(f"Output: {e.output}")
            print(f"Error: {e.stderr}")
        except Exception as e:
            print(f"Unexpected error with {html_file}: {str(e)}")
    
    print("\nFormatting complete!")

if __name__ == "__main__":
    print("Checking Prettier installation...")
    try:
        result = subprocess.run(
            [r'C:\Program Files\nodejs\npx.cmd', 'prettier', '--version'],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"Prettier version: {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print("Installing prettier...")
        try:
            subprocess.run(
                [r'C:\Program Files\nodejs\npm.cmd', 'install', '--save-dev', 'prettier'],
                check=True,
                capture_output=True,
                text=True
            )
            print("Prettier installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install Prettier: {e.stderr}")
            sys.exit(1)
    
    format_html_files() 