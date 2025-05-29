from pathlib import Path

from zenml import pipeline

from steps.gen_data import gen_sum, hist
from steps.infra import fetch_from_mongodb, push_hf, save_data_to_disk


@pipeline
def gen_data(
    extract_collection_name: str,
    load_dataset_id: str,
    fetch_limit: int = 1000,
    summarization_agent_model_id: str = "gpt-4o-mini",
    summarization_agent_mock: bool = False,
    summarization_max_characters: int = 256,
    val_split_ratio: float = 0.1,
    test_split_ratio: float = 0.1,
    min_document_characters: int = 50,
    min_quality_score: float = 0.3,
    augmentation_loops: int = 4,
    max_workers: int = 10,
    data_dir: Path = Path("data/"),
) -> None:
    documents = fetch_from_mongodb(
        collection_name=extract_collection_name, limit=fetch_limit
    )

    # EDA
    hist(documents, model_id=summarization_agent_model_id)

    # Generate summarization dataset
    dataset = gen_sum(
        documents=documents,
        summarization_model=summarization_agent_model_id,
        val_split_ratio=val_split_ratio,
        test_split_ratio=test_split_ratio,
        min_document_characters=min_document_characters,
        min_quality_score=min_quality_score,
        augmentation_loops=augmentation_loops,
        max_workers=max_workers,
        mock=summarization_agent_mock,
        summarization_max_characters=summarization_max_characters,
    )

    # Push to Hugging Face and save to disk
    push_hf(dataset, load_dataset_id)
    save_data_to_disk(
        dataset, output_dir=data_dir / "instruct_datasets" / load_dataset_id
    )
