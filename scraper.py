import requests
from bs4 import BeautifulSoup
import pandas as pd
# import PyPDF2  # Not needed if only fetching abstracts
# from io import BytesIO  # Not needed if only fetching abstracts

def get_abstract_from_arxiv(arxiv_id):
    # Base URL for the arXiv API
    api_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    
    response = requests.get(api_url)
    response.raise_for_status()
    
    # Parse the XML response
    soup = BeautifulSoup(response.content, 'xml')
    entry = soup.find('entry')
    abstract = entry.find('summary').text.strip()
    
    return abstract  # Only returning the abstract

def scrape_papers(url):
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')
    papers = []
    
    # Gather all anchors with arXiv links
    arxiv_anchors = [anchor for anchor in soup.find_all('a') if 'arXiv' in anchor.text]
    
    for anchor in arxiv_anchors:
        title = anchor.find_previous('dt').text.strip()
        link = anchor['href']
        
        # Extract the arXiv ID from the URL
        arxiv_id = link.split('/')[-1]
        
        # Get the abstract using the arXiv API
        abstract = get_abstract_from_arxiv(arxiv_id)
        papers.append({'title': title, 'url': link, 'abstract': abstract})

    return papers

url = "https://openaccess.thecvf.com/ICCV2023?day=all"
papers = scrape_papers(url)

df = pd.DataFrame(papers)
df.to_csv('papers_with_abstracts.csv', index=False)  # File name changed to reflect content

print(f"Scraped {len(papers)} papers with abstracts and saved to 'papers_with_abstracts.csv'")



#all in one script
#scraping and fetching are intertwined -> changing how we fetch from arxiv would also mean changing how we scrape iccv
#not that flexible -> to adapt to another conference or fetch from a different source like google scholar we'd need to change the whole thing

#new version with OOP
#divided in classes, each focused on a task -> fetching, scraping
#the scraper is independent of the fetcher
#can easely add new fetchers or scrapers without messing up existing code