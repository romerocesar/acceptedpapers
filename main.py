import pandas as pd
from fetchers import ArxivFetcher
from scrapers import ICCVScraper

def save_papers_to_csv(papers, file_name):
    df = pd.DataFrame(papers)
    df.to_csv(file_name, index=False)
    print(f"Saved {len(papers)} papers to '{file_name}'")

if __name__ == '__main__':
    #ICCV scraper should use the ArxivFetcher
    fetcher = ArxivFetcher()
    scraper = ICCVScraper(fetcher, num_papers_to_scrape=5)  #test it with 5 papers only

    url = "https://openaccess.thecvf.com/ICCV2023?day=all"
    papers = scraper.get_publications(url)
    save_papers_to_csv(papers, 'papers_with_abstracts_and_content.csv')
