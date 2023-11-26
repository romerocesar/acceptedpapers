'''This module contains classes that fetch publication content from
various sources. Basically strategy pattern.

TODO: Add fetchers for google scholar, dblp, semantic scholar, etc.
TODO: create a publication class that holds the content and metadata.
'''
from abc import ABCMeta, abstractmethod
from io import BytesIO
import logging

import requests
from bs4 import BeautifulSoup
import PyPDF2

logger = logging.getLogger('accepted_papers')


class PublicationFetcher(metaclass=ABCMeta):
    '''Abstract base class for publication fetchers.'''
    @abstractmethod
    def fetch(self, publication_id):
        '''Fetches the publication content from the source and returns it.'''
        raise NotImplementedError("Subclasses must implement this method!")


class ArxivFetcher(PublicationFetcher):
    def fetch(self, arxiv_id):
        logger.debug(f"Fetching publication {arxiv_id} from arxiv.org")
        api_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"

        # TODO: catch and raise a more specific exception whenever an
        # http error occurs
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

        logger.info(f"Fetched publication {arxiv_id} from arxiv.org")
        return abstract, content
