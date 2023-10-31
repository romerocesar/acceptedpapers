import requests
from bs4 import BeautifulSoup
import PyPDF2
from io import BytesIO

class PublicationFetcher:
    def fetch_content(self, publication_id):
        #unified interface - consistent method for interacting with objects/subclasses
        #every subclass has to implement this, but has freedom on how to do so - necessary methods with a flexibility
        raise NotImplementedError("Subclasses must implement this method!")

#the goal here is to have a bunch of fetchers and just call fetch_content on each one
#this way the main application doenst need to have special logic for each fetcher or know how it works, it can just call fetch_content, and its fetcher is trusted to do its job

#ArxivFetcher is only responsible for fetching papers from Arxiv
class ArxivFetcher(PublicationFetcher):
    def fetch_content(self, arxiv_id):
        api_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
        
        response = requests.get(api_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'xml')
        entry = soup.find('entry')
        abstract = entry.find('summary').text.strip()

        pdf_url = entry.find('link', {'title': 'pdf'})['href']
        pdf_response = requests.get(pdf_url)
        pdf_response.raise_for_status()

        with BytesIO(pdf_response.content) as open_pdf_file:
            reader = PyPDF2.PdfReader(open_pdf_file)
            content = ""
            for page_num in range(len(reader.pages)):
                content += reader.pages[page_num].extract_text()

        return abstract, content

#google scholar fetcher
