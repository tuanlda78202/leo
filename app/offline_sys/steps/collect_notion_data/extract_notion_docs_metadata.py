from typing import Annotated

from loguru import logger
from zenml import get_step_context, step

from offline.domain import DocumentMetaData
from offline.infra.notion import NotionDatabaseClient


@step
def extract_notion_docs_metadata(
    database_id: str,
) -> Annotated[list[DocumentMetaData], "notion_docs_metadata"]:
    """Extract metadata from Notion database"""

    # query the Notion database to get page metadata
    client = NotionDatabaseClient()
    docs_metadata = client.query_notion_db(database_id)

    logger.info(
        f"Extracted {len(docs_metadata)} documents metadata from Notion database {database_id}"
    )

    # orchestrator log step metadata
    step_context = get_step_context()
    step_context.add_output_metadata(
        output_name="notion_docs_metadata",
        metadata={
            "database_id": database_id,
            "num_docs_metadata": len(docs_metadata),
        },
    )

    return docs_metadata
