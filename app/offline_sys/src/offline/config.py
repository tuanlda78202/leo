from loguru import logger
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    A Pydantic-based settings class for managing application configurations.
    """

    # --- Pydantic Settings ---
    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )

    # --- AWS Configuration ---
    AWS_ACCESS_KEY: str | None = Field(
        default=None, description="AWS access key for authentication."
    )
    AWS_SECRET_KEY: str | None = Field(
        default=None, description="AWS secret key for authentication."
    )
    AWS_DEFAULT_REGION: str = Field(
        default="ap-southeast-1", description="AWS region for cloud services."
    )
    AWS_S3_BUCKET_NAME: str = Field(
        default="tuanlda78202-data",
        description="Name of the S3 bucket for storing application data.",
    )

    # --- Comet ML & Opik Configuration ---
    COMET_API_KEY: str | None = Field(
        default=None, description="API key for Comet ML and Opik services."
    )
    COMET_PROJECT: str = Field(
        default="leo-tracker",
        description="Project name for Comet ML and Opik tracking.",
    )

    # --- Hugging Face Configuration ---
    HUGGINGFACE_ACCESS_TOKEN: str | None = Field(
        default=None, description="Access token for Hugging Face API authentication."
    )
    HUGGINGFACE_DEDICATED_ENDPOINT: str | None = Field(
        default=None,
        description="Dedicated endpoint URL for real-time inference. "
        "If provided, we will use the dedicated endpoint instead of OpenAI. "
        "For example, https://um18v2aeit3f6g1b.eu-west-1.aws.endpoints.huggingface.cloud/v1/, "
        "with /v1 after the endpoint URL.",
    )

    # --- MongoDB Atlas Configuration ---
    MONGODB_DATABASE_NAME: str = Field(
        default="leo-database",
        description="Name of the MongoDB database.",
    )
    MONGODB_URI: str = Field(
        default="",
        description="Connection URI for the local MongoDB Atlas instance.",
    )

    # --- Notion API Configuration ---
    NOTION_SECRET_KEY: str | None = Field(
        default=None, description="Secret key for Notion API authentication."
    )

    # --- Gemini API Configuration ---
    GEMINI_API_KEY: str | None = Field(
        default=None, description="API key for Gemini service authentication."
    )
    GOOGLE_API_KEY: str | None = Field(
        default=None, description="API key for Google services."
    )

    # # --- OpenAI API Configuration ---
    # OPENAI_API_KEY: str = Field(
    #     description="API key for OpenAI service authentication.",
    # )

    # @field_validator("OPENAI_API_KEY")
    # @classmethod
    # def check_not_empty(cls, value: str, info) -> str:
    #     if not value or value.strip() == "":
    #         logger.error(f"{info.field_name} cannot be empty.")
    #         raise ValueError(f"{info.field_name} cannot be empty.")
    #     return value


try:
    settings = Settings()
except Exception as e:
    logger.error(f"Failed to load configuration: {e}")
    raise SystemExit(e)
