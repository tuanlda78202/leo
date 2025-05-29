from typing import Annotated

from loguru import logger
from zenml import get_step_context, step

from offline.config import settings
from offline.domain import InstructDataset


@step
def push_hf(
    dataset: Annotated[InstructDataset, "instruct_dataset"],
    dataset_id: Annotated[str, "dataset_id"],
) -> Annotated[str, "data_gen_output"]:
    assert settings.HUGGINGFACE_ACCESS_TOKEN is not None, (
        "HF access token must be provided for pushing to HF"
    )

    logger.info(f"Pushing dataset {dataset_id} to Hugging Face.")

    hf_dataset = dataset.to_huggingface()
    hf_dataset.push_to_hub(dataset_id, token=settings.HUGGINGFACE_ACCESS_TOKEN)

    step_context = get_step_context()
    step_context.add_output_metadata(
        output_name="data_gen_output",
        metadata={
            "dataset_id": dataset_id,
            "train_samples": len(hf_dataset["train"]),
            "validation_samples": len(hf_dataset["validation"]),
            "test_samples": len(hf_dataset["test"]),
        },
    )

    return dataset_id
