from typing import Annotated

from zenml import get_step_context, step

from offline.domain import Document, DocumentMetaData
from offline.infra.notion import NotionDocumentClient


@step
def extract_notion_docs(
    documents_metadata: list[DocumentMetaData],
) -> Annotated[list[Document], "notion_docs"]:
    """Extract content from Notion metadata"""

    client = NotionDocumentClient()
    documents = []

    # add metadata, parse content, and extract URLs from each document
    for document_metadata in documents_metadata:
        documents.append(client.extract_docs(document_metadata))

    step_context = get_step_context()
    step_context.add_output_metadata(
        output_name="notion_docs",
        metadata={
            "num_docs": len(documents),
        },
    )
    return documents
