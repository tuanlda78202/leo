import boto3
import botocore
import botocore.exceptions
from loguru import logger


def get_aws_id() -> None:
    """
    Fetch and log the identity information of the currently authenticated user.

    Returns:
        None
    """

    try:
        sts_client = boto3.client("sts")

        identity = sts_client.get_caller_identity()

        logger.info("AWS Identity Information:")
        logger.info(f"Account ID: {identity['Account']}")
        logger.info(f"User ID: {identity['UserId']}")
        logger.info(f"ARN: {identity['Arn']}")
    except botocore.exceptions.NoCredentialsError:
        logger.error(
            "No AWS credentials were found. Make sure your environment is configured correctly."
        )
    except botocore.exceptions.PartialCredentialsError:
        logger.error(
            "Incomplete AWS credentials were found. Ensure both Access Key and Secret Key are set."
        )
    except Exception as e:
        logger.error(f"An error occurred: {e}")


if __name__ == "__main__":
    get_aws_id()
