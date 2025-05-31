from langchain_text_splitters import RecursiveCharacterTextSplitter
from loguru import logger


def get_splitter(chunk_size: int) -> RecursiveCharacterTextSplitter:
    """Returns a token-based text splitter with overlap.

    Args:
        chunk_size: Number of tokens for each text chunk.
        summarization_type: Type of summarization to use ("contextual" or "simple").
        **kwargs: Additional keyword arguments passed to the summarization agent.

    Returns:
        RecursiveCharacterTextSplitter: A configured text splitter instance with
            summarization capabilities.
    """

    chunk_overlap = int(0.15 * chunk_size)

    logger.info(
        f"Getting splitter with chunk size: {chunk_size} and overlap: {chunk_overlap}"
    )

    return RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
