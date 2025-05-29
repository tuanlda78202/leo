from typing import Annotated

from zenml import step

from offline.application.dataset import SummarizationDatasetGenerator
from offline.domain import Document, InstructDataset


@step
def gen_sum(
    documents: list[Document],
    summarization_model: str,
    val_split_ratio: float = 0.1,
    test_split_ratio: float = 0.1,
    min_document_characters: int = 50,
    min_quality_score: float = 0.3,
    augmentation_loops: int = 4,
    max_workers: int = 10,
    mock: bool = False,
    summarization_max_characters: int = 256,
) -> Annotated[InstructDataset, "gen_summary_dataset"]:
    """pre-filter -> augment summarization dataset -> post-filter -> instruct pydantic dataset -> split"""

    dataset_generator = SummarizationDatasetGenerator(
        summarization_model=summarization_model,
        summarization_max_characters=summarization_max_characters,
        val_split_ratio=val_split_ratio,
        test_split_ratio=test_split_ratio,
        max_workers=max_workers,
        mock=mock,
        min_document_length=min_document_characters,
        min_quality_score=min_quality_score,
        augmentation_loops=augmentation_loops,
    )
    dataset = dataset_generator.generate(documents=documents)

    return dataset
