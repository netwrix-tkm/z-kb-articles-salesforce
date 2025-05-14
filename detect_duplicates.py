import os
import re
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

class KBDuplicateDetector:
    def __init__(self, directory_path, similarity_threshold=0.7):
        self.directory_path = directory_path
        self.similarity_threshold = similarity_threshold
        self.articles = {}
        self.similarity_matrix = None
        
    def clean_text(self, text):
        """Clean and normalize text content."""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters
        text = re.sub(r'[^\w\s]', '', text)
        return text.strip().lower()
    
    def extract_content(self, html_content):
        """Extract meaningful content from HTML."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract title
        title = soup.find('title')
        title = title.text if title else ''
        
        # Extract main content
        content_div = soup.find('div', class_='Content__c')
        if not content_div:
            return title, ''
            
        # Extract text from all sections
        sections = []
        for section in content_div.find_all(['h2', 'h3', 'p', 'ul', 'ol']):
            sections.append(section.get_text())
            
        content = ' '.join(sections)
        return title, content
    
    def load_articles(self):
        """Load and process all HTML articles in the directory."""
        for root, _, files in os.walk(self.directory_path):
            for file in files:
                if file.endswith('.html'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                            title, content = self.extract_content(html_content)
                            if content:
                                self.articles[file_path] = {
                                    'title': title,
                                    'content': self.clean_text(content)
                                }
                    except Exception as e:
                        print(f"Error processing {file_path}: {str(e)}")
    
    def calculate_similarity(self):
        """Calculate similarity between all articles."""
        if not self.articles:
            return
            
        # Create TF-IDF matrix
        vectorizer = TfidfVectorizer(stop_words='english')
        content_list = [article['content'] for article in self.articles.values()]
        tfidf_matrix = vectorizer.fit_transform(content_list)
        
        # Calculate cosine similarity
        self.similarity_matrix = cosine_similarity(tfidf_matrix)
    
    def find_duplicates(self):
        """Find potential duplicate articles."""
        if self.similarity_matrix is None:
            return []
            
        duplicates = []
        file_paths = list(self.articles.keys())
        
        for i in range(len(file_paths)):
            for j in range(i + 1, len(file_paths)):
                similarity = self.similarity_matrix[i][j]
                if similarity >= self.similarity_threshold:
                    duplicates.append({
                        'file1': file_paths[i],
                        'file2': file_paths[j],
                        'similarity': similarity,
                        'title1': self.articles[file_paths[i]]['title'],
                        'title2': self.articles[file_paths[j]]['title']
                    })
        
        return sorted(duplicates, key=lambda x: x['similarity'], reverse=True)
    
    def generate_report(self, duplicates):
        """Generate a CSV report of potential duplicates."""
        if not duplicates:
            print("No potential duplicates found.")
            return
            
        # Create a DataFrame from the duplicates list
        df = pd.DataFrame(duplicates)
        
        # Reorder columns for better readability
        df = df[['similarity', 'title1', 'file1', 'title2', 'file2']]
        
        # Format similarity as percentage
        df['similarity'] = df['similarity'].apply(lambda x: f"{x:.2%}")
        
        # Generate output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"duplicate_articles_{timestamp}.csv"
        
        # Save to CSV
        df.to_csv(output_file, index=False)
        print(f"\nReport saved to: {output_file}")
        print(f"Found {len(duplicates)} potential duplicate pairs")

def main():
    # Set the directory path to your KB articles
    directory_path = "auditor"
    
    # Create detector instance
    detector = KBDuplicateDetector(directory_path, similarity_threshold=0.7)
    
    # Process articles
    print("Loading articles...")
    detector.load_articles()
    print(f"Loaded {len(detector.articles)} articles")
    
    # Calculate similarities
    print("Calculating similarities...")
    detector.calculate_similarity()
    
    # Find and report duplicates
    print("Finding duplicates...")
    duplicates = detector.find_duplicates()
    detector.generate_report(duplicates)

if __name__ == "__main__":
    main() 