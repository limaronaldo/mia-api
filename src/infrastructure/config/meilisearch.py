import meilisearch
from decouple import config

meilisearch_client = meilisearch.Client(
    url=config("MEILI_HTTP_ADDR"),
    api_key=config("MEILI_API_KEY"),
)
