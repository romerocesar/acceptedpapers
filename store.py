import os
import weaviate
from langchain.embeddings.openai import OpenAIEmbeddings
from dotenv import load_dotenv
import logging

load_dotenv()

class EmbeddingStorage:
    def __init__(self, weaviate_url, weaviate_api_key, openai_api_key):
        self.client = weaviate.Client(url=weaviate_url, auth_client_secret=weaviate.AuthApiKey(weaviate_api_key))
        self.embeddings = OpenAIEmbeddings(api_key=openai_api_key)
        self._create_schema()

    def _create_schema(self):
        schema = self.client.schema.get()
        
        # Check if the schema is empty or uninitialized
        if 'classes' not in schema:
            schema['classes'] = []

        existing_class_names = [cls['class'] for cls in schema['classes']]

        paper_schema = {
            "class": "Paper",
            "description": "A class to store information about ML conference papers",
            "properties": [
                {"name": "title", "dataType": ["string"], "indexInverted": True},
                {"name": "url", "dataType": ["string"]},
                {"name": "abstract", "dataType": ["text"], "indexInverted": True},
                {"name": "embedding", "dataType": ["number[]"]}  # Vector of numbers
            ]
        }

        # Check if 'Paper' class already exists
        if 'Paper' not in existing_class_names:
            self.client.schema.create_class(paper_schema)

    def generate_embeddings(self, abstracts):
        # Embedding a list of abstracts (documents)
        return self.embeddings.embed_documents(abstracts)

    def store_papers(self, papers, embeddings):
        for paper, embedding in zip(papers, embeddings):
            paper_object = {
                "title": paper['title'],
                "url": paper['url'],
                "abstract": paper['abstract'],
                "embedding": embedding
            }
            self.client.data_object.create(paper_object, class_name="Paper")

    def clear_database(self):
        schema = self.client.schema.get()
        classes = schema['classes']
        for class_info in classes:
            class_name = class_info['class']
            self.client.schema.delete_class(class_name)
        
    def semantic_search(self, query_text, limit=1):
        # Convert the query text into an embedding
        query_embedding = self.embeddings.embed_query(query_text)

        # Perform a semantic search in Weaviate using nearVector
        results = self.client.query.get(
            "Paper", 
            ["title", "url", "abstract"]
        ).with_near_vector({
            "vector": query_embedding,
            "certainty": 0.7  # You can adjust the certainty as needed
        }).with_limit(limit).do()

        return results

# Example Usage
load_dotenv()
embedding_storage = EmbeddingStorage(
    os.environ.get("WEAVIATE_CLUSTER_URL"),
    os.environ.get("WEAVIATE_API_KEY"),
    os.environ.get("OPENAI_API_KEY")
)

# papers = <result from your scraping logic>
# abstracts = [paper['abstract'] for paper in papers]
# paper_embeddings = embedding_storage.generate_embeddings(abstracts)
# embedding_storage.store_papers(papers, paper_embeddings)