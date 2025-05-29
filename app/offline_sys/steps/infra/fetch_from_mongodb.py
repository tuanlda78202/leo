from typing import Annotated

from zenml.steps import get_step_context, step

from offline.domain import Document
from offline.infra.mongo import MongoDBService


@step
def fetch_from_mongodb(
    collection_name: str, limit: int
) -> Annotated[list[Document], "fetched_docs"]:
    """Fetch documents from MongoDB collection.

    Args:
        collection_name: Name of the MongoDB collection to fetch documents from.
        limit: Maximum number of documents to fetch.

    Returns:
        list[Document]: List of fetched documents.
    """
    with MongoDBService(
        model=Document, collection_name=collection_name
    ) as mongo_service:
        fetched_docs = mongo_service.fetch_documents(limit=limit, query={})

    step_context = get_step_context()
    step_context.add_output_metadata(
        output_name="fetched_docs",
        metadata={
            "count": len(fetched_docs),
        },
    )

    return fetched_docs
