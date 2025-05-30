from typing import Literal, Union

from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_mongodb.retrievers import (
    MongoDBAtlasHybridSearchRetriever,
    MongoDBAtlasParentDocumentRetriever,
)
from loguru import logger

from offline.config import settings

from .embedding import EmbeddingModelType, EmbeddingsModel, get_embedding_model
from .splitter import get_splitter

RetrieverType = Literal["contextual", "parent"]
RetrieverModel = Union[
    MongoDBAtlasHybridSearchRetriever, MongoDBAtlasParentDocumentRetriever
]


def get_retriever(
    embedding_model_id: str,
    embedding_model_type: EmbeddingModelType = "huggingface",
    retriever_type: RetrieverType = "contextual",
    k: int = 3,
    device: str = "cpu",
) -> RetrieverModel:
    logger.info(
        f"Getting '{retriever_type}' retriever for '{embedding_model_type}' - '{embedding_model_id}' on '{device}' "
        f"with {k} top results"
    )

    embedding_model = get_embedding_model(
        embedding_model_id, embedding_model_type, device
    )

    if retriever_type == "contextual":
        return get_hybrid_search_retriever(embedding_model, k)
    elif retriever_type == "parent":
        return get_parent_document_retriever(embedding_model, k)
    else:
        raise ValueError(f"Invalid retriever type: {retriever_type}")


# ! Hybrid search
def get_hybrid_search_retriever(
    embedding_model: EmbeddingsModel, k: int
) -> MongoDBAtlasHybridSearchRetriever:
    vector_store = MongoDBAtlasVectorSearch.from_connection_string(
        connection_string=settings.MONGODB_URI,
        embedding=embedding_model,
        namespace=f"{settings.MONGODB_DATABASE_NAME}.rag",
        text_key="chunk",
        embedding_key="embedding",
        relevance_score_fn="dotProduct",
    )

    retriever = MongoDBAtlasHybridSearchRetriever(
        vectorstore=vector_store,
        search_index_name="chunk_text_search",
        top_k=k,
        vector_penalty=50,
        fulltext_penalty=50,
    )

    return retriever


# ! Parent document retriever
def get_parent_document_retriever(
    embedding_model: EmbeddingsModel, k: int = 3
) -> MongoDBAtlasParentDocumentRetriever:
    retriever = MongoDBAtlasParentDocumentRetriever.from_connection_string(
        connection_string=settings.MONGODB_URI,
        embedding_model=embedding_model,
        child_splitter=get_splitter(200),
        parent_splitter=get_splitter(800),
        database_name=settings.MONGODB_DATABASE_NAME,
        collection_name="rag",
        text_key="page_content",
        search_kwargs={"k": k},
    )

    return retriever
