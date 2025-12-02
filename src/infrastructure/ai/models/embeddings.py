from langchain_google_vertexai.embeddings import VertexAIEmbeddings
from decouple import config

embeddings = VertexAIEmbeddings(
    model_name="text-multilingual-embedding-002",
    # api_key=config("GCLOUD_API_KEY"),
)
