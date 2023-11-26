import logging

from bs4 import BeautifulSoup
import requests


class Scraper:
    def get_publications(self, url):
        raise NotImplementedError("Subclasses must implement this method!")
#an attribute is a variable that belongs to an object/instance of the class -> num_papers_to_scrape is an attribute that stores data
#bundle together related methods and variables/data they need to work on -> encapsulation

#separations of concerns: ICCVScraper is only responsible for scraping papers from ICCV
class ICCVScraper(Scraper):
    #initialize the object with fetcher and provided num of papers to scrape
    def __init__(self, fetcher, num_papers_to_scrape=None):
        #attribute with an instance of the fetcher object - it has data about which fetcher to use
        #dependency injection: when we create an instance of ICCVScraper, we pass it the fetcher it should use -> maybe we can make this dynamic?
        self.fetcher = fetcher
        self.num_papers_to_scrape = num_papers_to_scrape

    #when called on an instance of ICCVScraper will use fetcher attribute + num of papers to scrape papers from the provided url
    def get_publications(self, url):
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        papers = []

        arxiv_anchors = [anchor for anchor in soup.find_all('a') if 'arXiv' in anchor.text]

        # If num_papers_to_scrape is defined, limit the number of papers
        if self.num_papers_to_scrape:
            arxiv_anchors = arxiv_anchors[:self.num_papers_to_scrape]

        for anchor in arxiv_anchors:
            title = anchor.find_previous('dt').text.strip()
            link = anchor['href']

            arxiv_id = link.split('/')[-1]

            abstract, content = self.fetcher.fetch(arxiv_id)
            papers.append({'title': title, 'url': link, 'abstract': abstract, 'content': content})

        return papers


    #open/closed principle:
    #keep things open for extension but closed for modification
    #in practice: scraper and get_publications are abstract base classes: they provide a blueprint but not a concrete implementation. If we want to to scrape a new conference we dont modify the base class(closed for modification), we just create a new subclass (open to extension)

    #a module in the context of OOP can be a method, class, package or a whole app.
    #in the contenxt of open/closed principle: a module is any contained piece of software that has a specific responsibility/behaviour.
    #the goal is to build modules in a way that their capabilities can be extended, without changing existing behavior

    #the 5 solid principles of OOP:
    #Single Responsibility Principle: a class should have only one responsibility -> ArxivFetcher has only the job of fetching content from Arxiv
    #Open/Closed Principle: open for extension but closed for modification
    #Liskov substitution Principle: children can always replace the parent class without chaning the behavior of the program
    #Interface Segragation Principle: no client should be forced to depend on interfaces they dont use.
    #           Basically: the abstract/base class for scrapers should only define/promise methods that all scrapers would use and need. Otherwise they would be forced to implement methods they dont need, its better to create another interface/abstract class in that case
    #Dependency Inversion Principle: instead of specific details, parts of the code should rely on general concepts. For example, ICCVScraper is dependent on the abstract fetcher and not the specifc implementation ArxivFetcher. It relies on the general concept of a fetcher.


    #interface is the base class which defines the methods without implementation and sub-classes that implement this interface agree to provide functionality to thsoe methods
    #in practice Scraper acts as our interface and get_publications is the promise/method defined in the interface, each sub-class is expected to provide implementation for that method
