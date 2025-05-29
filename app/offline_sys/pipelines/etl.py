from pathlib import Path

from loguru import logger
from zenml import pipeline

from steps.etl import add_quality_score, crawl
from steps.infra import (
    ingest_to_mongodb,
    read_docs_from_disk,
    save_docs_to_disk,
    upload_to_s3,
)


# zenml auto handle type conversion
@pipeline
def etl(
    data_dir: Path,
    max_workers: int = 4,
    quality_agent_model_id: str = "gpt-4o-mini",
    quality_agent_mock: bool = False,
    load_collection_name: str = "raw",
    to_s3: bool = False,
):
    """ETL pipeline to crawl, add quality scores, and save documents."""
    notion_data_dir = data_dir / "notion"
    # crawled_data_dir = data_dir / "crawled"
    scored_data_dir = data_dir / "scored"

    raw_docs = read_docs_from_disk(data_dir=notion_data_dir, nesting_level=1)

    crawled_docs = crawl(documents=raw_docs, max_workers=max_workers)

    scored_docs = add_quality_score(
        documents=crawled_docs,
        model_id=quality_agent_model_id,
        mock=quality_agent_mock,
        max_workers=max_workers,
    )

    save_docs_to_disk(documents=scored_docs, output_dir=scored_data_dir)

    ingest_to_mongodb(
        models=scored_docs,
        collection_name=load_collection_name,
        clear_collection=True,
    )

    if to_s3:
        upload_to_s3(
            folder_path=scored_data_dir,  # TODO: need exist dir
            s3_prefix="leo/scored",
        )
