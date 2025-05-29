import shutil
from pathlib import Path
from typing import Annotated

from loguru import logger
from zenml import get_step_context, step

from offline.domain import InstructDataset


@step
def save_data_to_disk(
    dataset: Annotated[InstructDataset, "instruct_dataset"],
    output_dir: Path,
) -> Annotated[str, "output"]:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    logger.info(f"Saving dataset to '{output_dir}'")
    output_dir = dataset.write(output_dir=output_dir)

    step_context = get_step_context()
    step_context.add_output_metadata(
        output_name="output",
        metadata={
            "train_samples": len(dataset.train),
            "validation_samples": len(dataset.validation),
            "test_samples": len(dataset.test),
            "output_dir": str(output_dir),
        },
    )

    return str(output_dir)
