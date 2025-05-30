from zenml import pipeline

from offline.application.rag import EmbeddingModelType
from offline.application.rag.retriever import RetrieverType
from offline.application.rag.splitter import SummarizationType
from steps.infra import (
    fetch_from_mongodb,
)
from steps.rag_index import chunk_embed_load, filter_by_quality


@pipeline
def rag_index(
    extract_collection_name: str,
    fetch_limit: int,
    load_collection_name: str,
    content_quality_score_threshold: float,
    retriever_type: RetrieverType,
    embedding_model_id: str,
    embedding_model_type: EmbeddingModelType,
    embedding_model_dim: int,
    chunk_size: int,
    contextual_summarization_type: SummarizationType = "none",
    contextual_agent_model_id: str | None = None,
    contextual_agent_max_characters: int | None = None,
    mock: bool = False,
    processing_batch_size: int = 256,
    processing_max_workers: int = 10,
    device: str = "cpu",
) -> None:
    """Computes and stores RAG vector index from documents in MongoDB.

    This pipeline fetches documents from MongoDB, filters them by quality,
    chunks the content, computes embeddings, and stores the results.

    Args:
        extract_collection_name: Name of MongoDB collection to fetch documents from
        fetch_limit: Maximum number of documents to fetch
        load_collection_name: Name of MongoDB collection to store results in
        content_quality_score_threshold: Minimum quality score for documents to be included
        retriever_type: Type of retriever to use for vector search
        embedding_model_id: Identifier for the embedding model
        embedding_model_type: Type of embedding model (e.g. OpenAI, HuggingFace)
        embedding_model_dim: Dimension of the embedding vectors
        chunk_size: Size of text chunks for embedding
        contextual_summarization_type: Type of summarization to apply to chunks
        contextual_agent_model_id: Model ID for contextual summarization agent
        contextual_agent_max_characters: Maximum characters for contextual summaries
        mock: Whether to run in mock mode
        processing_batch_size: Batch size for parallel processing
        processing_max_workers: Number of worker threads for parallel processing
        device: Device to run embeddings on ('cpu' or 'cuda')

    Returns:
        None
    """
    # Fetch
    docs = fetch_from_mongodb(
        collection_name=extract_collection_name, limit=fetch_limit
    )

    # Filter by quality
    filtered_docs = filter_by_quality(
        documents=docs, content_quality_score_threshold=content_quality_score_threshold
    )

    # RAG indexing
    chunk_embed_load(
        documents=filtered_docs,
        collection_name=load_collection_name,
        processing_batch_size=processing_batch_size,
        processing_max_workers=processing_max_workers,
        retriever_type=retriever_type,
        embedding_model_id=embedding_model_id,
        embedding_model_type=embedding_model_type,
        embedding_model_dim=embedding_model_dim,
        chunk_size=chunk_size,
        contextual_summarization_type=contextual_summarization_type,
        contextual_agent_model_id=contextual_agent_model_id,
        contextual_agent_max_characters=contextual_agent_max_characters,
        mock=mock,
        device=device,
    )
