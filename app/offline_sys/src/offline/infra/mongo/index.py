from langchain_mongodb.index import create_fulltext_search_index

from offline.infra.mongo.service import MongoDBService


class MongoDbIndex:
    """Create hybrid search index (vector and full-text) for MongoDB."""

    def __init__(
        self,
        retriever,
        mongodb_client: MongoDBService,
    ) -> None:
        self.retriever = retriever
        self.mongodb_client = mongodb_client

    def create(
        self,
        embedding_dim: int,
        is_hybrid: bool = False,
    ) -> None:
        vector_store = self.retriever.vectorstore

        # ! Vector search indexing
        vector_store.create_vector_search_index(
            dimensions=embedding_dim,
        )
        if is_hybrid:
            # ! Full-text search indexing
            create_fulltext_search_index(
                collection=self.mongodb_client.collection,
                field=vector_store._text_key,
                index_name=self.retriever.search_index_name,
            )
