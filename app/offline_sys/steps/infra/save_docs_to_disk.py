import shutil
from pathlib import Path
from typing import Annotated

from zenml import get_step_context, step

from offline.domain import Document


@step
def save_docs_to_disk(
    documents: Annotated[list[Document], "docs"],
    output_dir: Path,
) -> Annotated[str, "output"]:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    # save docs from infra class
    for document in documents:
        document.write(output_dir, obfuscate=True, also_save_as_txt=True)

    # orchestrator log step metadata
    step_context = get_step_context()
    step_context.add_output_metadata(
        output_name="output",
        metadata={
            "number_of_documents": len(documents),
            "output_dir": str(output_dir),
        },
    )

    return str(output_dir)
