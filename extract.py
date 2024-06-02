import requests
import pandas as pd
from bs4 import BeautifulSoup
import os


df = pd.read_excel('input.xlsx')

# create a directory for saving articles
output_dir = 'extracted_articles'
os.makedirs(output_dir, exist_ok=True)

# function to extract article title and text
def extract(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # extract the title
        title_tag = soup.find('h1')
        title = title_tag.get_text(strip=True)if title_tag else 'No Title Found'
        
        # attempt to find article text based on common patterns
        article_text = None
        possible_selectors = [
            {'name': 'div', 'attrs': {'class': 'td-post-content'}},
            {'name': 'div', 'attrs': {'class': 'entry-content'}},
            {'name': 'article'},
            {'name': 'div', 'attrs': {'class': 'post-content'}},
            {'name': 'div', 'attrs': {'class': 'content'}},
            {'name': 'div', 'attrs': {'id': 'content'}}
        ]
        
        for selector in possible_selectors:
            article = soup.find(selector['name'], selector['attrs'])
            if article:
                elements = article.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
                article_text = "\n".join([el.get_text(strip=True) for el in elements])
                break
        
        if not article_text:
            article_text = 'No Article Text Found'
        
        return title, article_text
    except Exception as e:
        print(f"Error extracting article from {url}: {e}")
        return None, None

# iterate over each row in the dataset
for index, row in df.iterrows():
    url_id = row['URL_ID']
    url = row['URL']
    
    title, article_text = extract(url)
    
    if title and article_text:
        output_file = os.path.join(output_dir, f"{url_id}.txt")
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(title + "\n\n" + article_text)
        print(f"Article {url_id} extracted and saved.")
    else:
        print(f"Failed to extract article {url_id}.")

print("Data extraction completed.")
