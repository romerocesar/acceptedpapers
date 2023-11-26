import logging

import streamlit as st
import pandas as pd

from scrapers import ICCVScraper
from fetchers import ArxivFetcher

logger = logging.getLogger('accepted_papers')

# set page config
st.set_page_config(page_title="Accepted conference papers", layout="wide")

# sidebar for user inputs
st.sidebar.title("Accepted conference papers")
st.sidebar.markdown("### Instructions")
st.sidebar.markdown("* Enter the URL of the conference.")
conference_url = st.sidebar.text_input("Conference URL")  # TODO: do this async and update a db rather than scraping every time

# Main area
st.markdown("""
## Accepted conference papers

This tool allows you to scrape abstracts from major ML conference websites.
Enter the URL of the conference in the sidebar and click 'Scrape Papers' to begin.
""")


def scrape_and_display(url):
    fetcher = ArxivFetcher()  # Initialize your ArxivFetcher
    scraper = ICCVScraper(fetcher, num_papers_to_scrape=5)

    try:
        papers = scraper.get_publications(url)
        return pd.DataFrame(papers)
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return pd.DataFrame()


if st.sidebar.button("Scrape Papers"):
    if conference_url:
        with st.spinner('Scraping papers...'):
            df = scrape_and_display(conference_url)
            st.success('Scraping complete!')
    else:
        st.warning("Please enter the conference URL.")

# Search functionality
if 'df' in locals():
    search_query = st.sidebar.text_input("Search Papers")
    if search_query:
        search_results = df[df['title'].str.contains(search_query, case=False)]
        st.dataframe(search_results)
    else:
        st.dataframe(df)

# Additional notes or footer
st.markdown("---")
st.markdown("Developed by [Your Name or Organization]")
st.markdown("© 2023 All Rights Reserved")
