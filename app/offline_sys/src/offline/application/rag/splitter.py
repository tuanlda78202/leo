from typing import Callable, Literal, Union

from langchain_text_splitters import RecursiveCharacterTextSplitter
from loguru import logger

from offline.application.agents import (
    ContextualSummarizationAgent,
    SimpleSummarizationAgent,
)

SummarizationType = Literal["contextual", "simple", "none"]
SummarizationAgent = Union[ContextualSummarizationAgent, SimpleSummarizationAgent]


def get_splitter(
    chunk_size: int, summarization_type: SummarizationType = "none", **kwargs
) -> RecursiveCharacterTextSplitter:
    """# ! Returns a token-based text splitter with overlap.

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

    # ! Chunking by token
    if summarization_type == "none":
        return RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            encoding_name="cl100k_base",
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    # ! Chunking by token with summarization for each chunk
    if summarization_type == "contextual":
        handler = ContextualSummarizationAgent(**kwargs)
    # ! just add summary of whole doc to each chunk (not personalization)
    elif summarization_type == "simple":
        handler = SimpleSummarizationAgent(**kwargs)

    # TODO: support Gemini tokenizer
    return HandlerRecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        handler=handler,
    )


class HandlerRecursiveCharacterTextSplitter(RecursiveCharacterTextSplitter):
    """A text splitter that can apply custom handling to chunks after splitting.

    This class extends RecursiveCharacterTextSplitter to allow post-processing of text chunks
    through a handler function. If no handler is provided, chunks are returned unchanged.
    """

    def __init__(
        self,
        handler: Callable[[str, list[str]], list[str]] | None = None,
        *args,
        **kwargs,
    ) -> None:
        """Initialize the splitter with an optional handler function.

        Args:
            handler: Optional callable that takes the original text and list of chunks,
                and returns a modified list of chunks. If None, chunks are returned unchanged.
            *args: Additional positional arguments passed to RecursiveCharacterTextSplitter.
            **kwargs: Additional keyword arguments passed to RecursiveCharacterTextSplitter.
        """
        super().__init__(*args, **kwargs)

        self.handler = handler if handler is not None else lambda _, x: x

    def split_text(self, text: str) -> list[str]:
        """Split text into chunks and apply the handler function.

        Args:
            text: The input text to split.

        Returns:
            list[str]: The processed text chunks after splitting and handling.
        """
        chunks = super().split_text(text)
        parsed_chunks = self.handler(text, chunks)

        return parsed_chunks
