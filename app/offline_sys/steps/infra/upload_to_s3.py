from pathlib import Path
from typing import Annotated

from zenml import get_step_context, step

from offline.config import settings
from offline.infra.aws.s3 import S3Client


@step
def upload_to_s3(
    folder_path: Path,
    s3_prefix: str = " ",
) -> Annotated[str, "output"]:
    """Upload documents to S3 bucket"""

    # call the S3 client
    s3_client = S3Client(bucket_name=settings.AWS_S3_BUCKET_NAME)
    s3_client.upload_folder(
        local_path=folder_path,
        s3_prefix=s3_prefix,
    )

    # orchestrator log step metadata
    step_context = get_step_context()
    step_context.add_output_metadata(
        output_name="output",
        meta_data={
            "folder_path": str(folder_path),
            "s3_prefix": s3_prefix,
        },
    )

    return str(folder_path)
