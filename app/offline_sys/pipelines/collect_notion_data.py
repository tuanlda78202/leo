from pathlib import Path

from loguru import logger
from zenml import pipeline

from steps.collect_notion_data import extract_notion_docs, extract_notion_docs_metadata
from steps.infra import save_docs_to_disk, upload_to_s3


@pipeline
def collect_notion_data(
    database_ids: list[str], data_dir: Path, to_s3: bool = False
) -> None:
    """Pipeline to collect data from Notion databases."""

    notion_data_dir = data_dir / "notion"
    notion_data_dir.mkdir(parents=True, exist_ok=True)

    for index, database_id in enumerate(database_ids):
        logger.info(
            f"Collecting data from Notion database {database_id} ({index + 1}/{len(database_ids)})"
        )

        # Min: 2 API calls
        documents_metadata = extract_notion_docs_metadata(
            database_id=database_id
        )  # raw metadata of database
        documents_data = extract_notion_docs(
            documents_metadata=documents_metadata
        )  # get content from database id

        save_docs_to_disk(
            documents=documents_data,
            output_dir=notion_data_dir / f"database_{index + 1}",
        )

    if to_s3:
        upload_to_s3(
            folder_path=notion_data_dir,
            s3_prefix="leo/notion",
        )
