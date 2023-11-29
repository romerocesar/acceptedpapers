import logging
import os

import streamlit as st
import pandas as pd

from scrapers import ICCVScraper
from fetchers import ArxivFetcher
from store import EmbeddingStorage

# Initialize the EmbeddingStorage
embedding_storage = EmbeddingStorage(
    os.environ.get("WEAVIATE_CLUSTER_URL"),
    os.environ.get("WEAVIATE_API_KEY"),
    os.environ.get("OPENAI_API_KEY")
)

logger = logging.getLogger('accepted_papers')

# set page config
st.set_page_config(page_title="Accepted conference papers", layout="wide")


# Sidebar for user inputs - Semantic Search
st.sidebar.title("ML Conference Paper Scraper")
st.sidebar.markdown("### Instructions")
st.sidebar.markdown("* Enter the URL of the conference for scraping.")
st.sidebar.markdown("* Use the search field to find papers semantically.")
conference_url = st.sidebar.text_input("Conference URL")
search_query = st.sidebar.text_input("Semantic Search Papers")


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
            # Process and store papers
            papers = df.to_dict('records')
            abstracts = [paper['abstract'] for paper in papers]
            embeddings = embedding_storage.generate_embeddings(abstracts)
            embedding_storage.store_papers(papers, embeddings)
            st.success('Papers stored in database!')

# Semantic search functionality
if search_query:
    with st.spinner("Searching for papers..."):
        search_results = embedding_storage.semantic_search(search_query)

        # Debug line: print the raw search results
        st.write("Raw Search Results:", search_results)

        if search_results:
            # Format and display search results (update this after inspecting the raw results)
            formatted_results = ...
            st.write("Formatted Search Results:", formatted_results)
        else:
            st.warning("No relevant papers found.")

# Simple Check for Data Storage
if st.sidebar.button("Check Stored Papers"):
    query = """
    {
      Paper(limit: 5) {
        title
        url
      }
    }
    """
    results = embedding_storage.client.query.raw(query)
    if results.get('data'):
        stored_papers = results['data']['Paper']
        st.write("Stored Papers:", stored_papers)
    else:
        st.warning("No papers found in the database.")

# Sample query for embedding inspection
sample_query = "machine learning"
sample_query_embedding = embedding_storage.embeddings.embed_query(sample_query)
st.write("Sample Query Embedding:", sample_query_embedding)



# Additional notes or footer
st.markdown("---")
st.markdown("Developed by [Your Name or Organization]")
st.markdown("© 2023 All Rights Reserved")
