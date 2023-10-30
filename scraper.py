import requests
from bs4 import BeautifulSoup
import pandas as pd
import PyPDF2
from io import BytesIO

#separate 
def get_abstract_and_content_from_arxiv(arxiv_id):
    # Base URL for the arXiv API
    api_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    
    response = requests.get(api_url)
    response.raise_for_status()
    
    # Parse the XML response
    soup = BeautifulSoup(response.content, 'xml')
    entry = soup.find('entry')
    abstract = entry.find('summary').text.strip()
    
    # Get the PDF link and download the PDF
    pdf_url = entry.find('link', {'title': 'pdf'})['href']
    pdf_response = requests.get(pdf_url)
    pdf_response.raise_for_status()
    
    # Extract text from the PDF using the new PdfReader class and extract_text method
    with BytesIO(pdf_response.content) as open_pdf_file:
        reader = PyPDF2.PdfReader(open_pdf_file)
        content = ""
        for page_num in range(len(reader.pages)):
            content += reader.pages[page_num].extract_text()
    
    return abstract, content


def scrape_papers(url):
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')
    papers = []
    
    # Gather all anchors with arXiv links and process only the first 2 for testing
    arxiv_anchors = [anchor for anchor in soup.find_all('a') if 'arXiv' in anchor.text][:2]
    
    for anchor in arxiv_anchors:
        title = anchor.find_previous('dt').text.strip()
        link = anchor['href']
        
        # Extract the arXiv ID from the URL
        arxiv_id = link.split('/')[-1]
        
        # Get the abstract and content using the arXiv API
        abstract, content = get_abstract_and_content_from_arxiv(arxiv_id)
        papers.append({'title': title, 'url': link, 'abstract': abstract, 'content': content})

    return papers

url = "https://openaccess.thecvf.com/ICCV2023?day=all"
papers = scrape_papers(url)

df = pd.DataFrame(papers)
df.to_csv('papers_with_abstracts_and_content.csv', index=False)

print(f"Scraped {len(papers)} papers with abstracts and content and saved to 'papers_with_abstracts_and_content.csv'")
