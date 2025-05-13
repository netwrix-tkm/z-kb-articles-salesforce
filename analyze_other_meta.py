import os
from bs4 import BeautifulSoup
import csv

def analyze_other_meta():
    # Create a list to store our findings
    findings = []
    
    # Walk through the _other directory
    other_dir = '_other'
    for root, dirs, files in os.walk(other_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Find all meta tags with name="label"
                    meta_tags = soup.find_all('meta', attrs={'name': 'label'})
                    for tag in meta_tags:
                        content_value = tag.get('content', '')
                        if content_value and content_value not in ('skb', 'employees_v'):
                            findings.append({
                                'file': file,
                                'meta_content': content_value
                            })
    
    # Write findings to CSV
    with open('other_meta_report.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['file', 'meta_content']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for finding in findings:
            writer.writerow(finding)
    
    print(f"Report generated: other_meta_report.csv")
    print(f"Found {len(findings)} unique meta tags")

if __name__ == "__main__":
    analyze_other_meta() 