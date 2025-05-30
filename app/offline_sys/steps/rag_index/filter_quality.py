from typing import Annotated

from zenml import get_step_context
from zenml.steps import step

from offline.domain import Document


@step
def filter_by_quality(
    documents: list[Document],
    content_quality_score_threshold: float,
) -> Annotated[list[Document], "filtered_docs"]:
    """Filter quality data from MongoDB.

    Args:
        documents: List of documents to process.
        collection_name: Name of MongoDB collection to store documents.
        processing_batch_size: Number of documents to process in each batch.
        processing_max_workers: Maximum number of concurrent processing threads.
        embedding_model_id: Identifier for the embedding model.
        embedding_model_type: Type of embedding model to use.
        embedding_model_dim: Dimension of the embedding vectors.
        chunk_size: Size of text chunks for splitting documents.
        device: Device to run embeddings on ('cpu' or 'cuda'). Defaults to 'cpu'.
    """

    assert 0 <= content_quality_score_threshold <= 1, (
        "Content quality score threshold must be between 0 and 1"
    )

    valid_docs = [
        doc
        for doc in documents
        if not doc.content_quality_score
        or doc.content_quality_score > content_quality_score_threshold
    ]

    step_context = get_step_context()
    step_context.add_output_metadata(
        output_name="filtered_docs",
        metadata={
            "len_docs_before_filtering": len(documents),
            "len_docs_after_filtering": len(valid_docs),
        },
    )

    return valid_docs
