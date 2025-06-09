import asyncio
import os

import psutil
from litellm import acompletion
from loguru import logger
from openai import AsyncOpenAI
from pydantic import BaseModel
from tqdm.asyncio import tqdm

from offline.config import settings


class ContextualDocument(BaseModel):
    """A document with its chunk and contextual summarization.

    Attributes:
        content: The full document content
        chunk: A specific portion of the document
        contextual_summarization: Optional summary providing context for the chunk
    """

    content: str
    chunk: str | None = None
    contextual_summarization: str | None = None

    def add_contextual_summarization(self, summary: str) -> "ContextualDocument":
        """Adds a contextual summary to the document.

        Args:
            summary: The contextual summary to add

        Returns:
            ContextualDocument: The document with added summary
        """
        self.contextual_summarization = summary
        return self


class ContextualSummarizationAgent:
    """Generates summaries for documents using LiteLLM with async support.

    This class handles the interaction with language models through LiteLLM to
    generate concise summaries while preserving key information from the original
    documents. It supports both single and batch document processing.

    Attributes:
        max_characters: Maximum number of characters for the summary.
        model_id: The ID of the language model to use for summarization.
        mock: If True, returns mock summaries instead of using the model.
        max_concurrent_requests: Maximum number of concurrent API requests.
    """

    SYSTEM_PROMPT_TEMPLATE = """You are a helpful assistant specialized in summarizing documents relative to a given chunk.
    <document>
    {content}
    </document>

    Here is the chunk we want to situate within the whole document
    <chunk>
    {chunk}
    </chunk>

    Please give a short succinct context of maximum {characters} characters to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk. Answer only with the succinct context and nothing else.
    """

    def __init__(
        self,
        model_id: str = "gpt-4o-mini",
        max_characters: int = 128,
        mock: bool = False,
        max_concurrent_requests: int = 4,
    ) -> None:
        self.model_id = model_id
        self.max_characters = max_characters
        self.mock = mock
        self.max_concurrent_requests = max_concurrent_requests

    def __call__(self, content: str, chunks: list[str]) -> list[str]:
        """Process document chunks for contextual summarization.

        Args:
            content: The full document content
            chunks: List of document chunks to summarize

        Returns:
            list[str]: List of chunks with added contextual summaries
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            results = asyncio.run(self.__summarize_context_batch(content, chunks))
        else:
            results = loop.run_until_complete(
                self.__summarize_context_batch(content, chunks)
            )

        return results

    async def __summarize_context_batch(
        self, content: str, chunks: list[str]
    ) -> list[str]:
        """Asynchronously summarize multiple document chunks.

        Args:
            content: The full document content
            chunks: List of document chunks to summarize

        Returns:
            list[str]: List of chunks with added contextual summaries
        """

        process = psutil.Process(os.getpid())
        start_mem = process.memory_info().rss
        total_chunks = len(chunks)
        logger.debug(
            f"Starting contextual summarization for {total_chunks} chunks with {self.max_concurrent_requests} concurrent requests. "
            f"Initial memory usage: {start_mem // (1024 * 1024)} MB"
        )

        documents = [
            ContextualDocument(content=content, chunk=chunk) for chunk in chunks
        ]

        summarized_documents = await self.__process_batch(
            documents, await_time_seconds=7
        )
        documents_with_summaries = [
            doc
            for doc in summarized_documents
            if doc.contextual_summarization is not None
        ]
        documents_without_summaries = [
            doc for doc in documents if doc.contextual_summarization is None
        ]

        # Retry failed documents with increased await time
        if documents_without_summaries:
            logger.info(
                f"Retrying {len(documents_without_summaries)} failed documents with increased await time..."
            )
            retry_results = await self.__process_batch(
                documents_without_summaries, await_time_seconds=20
            )
            documents_with_summaries += retry_results

        end_mem = process.memory_info().rss
        memory_diff = end_mem - start_mem
        logger.debug(
            f"Contextual summarization completed. "
            f"Final memory usage: {end_mem // (1024 * 1024)} MB, "
            f"Memory difference: {memory_diff // (1024 * 1024)} MB"
        )

        success_count = len(documents_with_summaries)
        failed_count = total_chunks - success_count
        logger.info(
            f"Contextual summarization results: "
            f"{success_count}/{total_chunks} chunks summarized successfully ✓ | "
            f"{failed_count}/{total_chunks} chunks failed ✗"
        )

        contextual_chunks = []
        for doc in documents_with_summaries:
            if doc.contextual_summarization is not None:
                chunk = f"{doc.contextual_summarization}\n\n{doc.chunk}"
            else:
                chunk = f"{doc.chunk}"

            contextual_chunks.append(chunk)

        return contextual_chunks

    async def __process_batch(
        self, documents: list[ContextualDocument], await_time_seconds: int
    ) -> list[ContextualDocument]:
        """Process a batch of documents with specified await time.

        Args:
            documents: List of documents to summarize
            await_time_seconds: Time in seconds to wait between requests

        Returns:
            list[ContextualDocument]: Processed documents with summaries
        """

        semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        tasks = [
            self.__summarize_context(
                document, semaphore, await_time_seconds=await_time_seconds
            )
            for document in documents
        ]
        results = []
        for coro in tqdm(
            asyncio.as_completed(tasks),
            total=len(documents),
            desc="Processing documents",
            unit="doc",
        ):
            result = await coro
            results.append(result)

        return results

    async def __summarize_context(
        self,
        document: ContextualDocument,
        semaphore: asyncio.Semaphore | None = None,
        await_time_seconds: int = 2,
    ) -> ContextualDocument:
        """Generate a contextual summary for a single document.

        Args:
            document: The document to summarize
            semaphore: Optional semaphore for controlling concurrent requests
            await_time_seconds: Time in seconds to wait between requests

        Returns:
            ContextualDocument: Document with generated summary
        """

        if self.mock:
            return document.add_contextual_summarization("This is a mock summary")

        async def process_document() -> ContextualDocument:
            try:
                response = await acompletion(
                    model=self.model_id,
                    messages=[
                        {
                            "role": "user",  # TODO: gemini model don't support system role
                            "content": self.SYSTEM_PROMPT_TEMPLATE.format(
                                characters=self.max_characters,
                                content=document.content[
                                    :6000
                                ],  # TODO: Keep it short to lower latency and costs.
                                chunk=document.chunk,
                            ),
                        },
                    ],
                    stream=False,
                    temperature=0,
                )
                await asyncio.sleep(await_time_seconds)  # Rate limiting

                if not response.choices:
                    logger.warning("No contextual summary generated for chunk")
                    return document

                context_summary: str = response.choices[0].message.content
                return document.add_contextual_summarization(context_summary)
            except Exception as e:
                logger.warning(f"Failed to generate contextual summary: {str(e)}")
                return document

        if semaphore:
            async with semaphore:
                return await process_document()

        return await process_document()


class SimpleSummarizationAgent:
    """Generates summaries for documents using LiteLLM with async support.

    This class handles the interaction with language models through LiteLLM to
    generate concise summaries while preserving key information from the original
    documents. It supports both single and batch document processing.

    Attributes:
        max_characters: Maximum number of characters for the summary.
        model_id: The ID of the language model to use for summarization.
        mock: If True, returns mock summaries instead of using the model.
        max_concurrent_requests: Maximum number of concurrent API requests.
    """

    SYSTEM_PROMPT_TEMPLATE = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

    ### Instruction:
    You are a helpful assistant specialized in summarizing documents for the purposes of improving semantic and keyword search retrieval.
    Generate a concise TL;DR summary in plain text format having a maximum of {characters} characters of the key findings from the provided documents,
    highlighting the most significant insights. Answer only with the succinct context and nothing else.

    ### Input:
    {content}

    ### Response:
    """

    def __init__(
        self,
        model_id: str = "gpt-4o-mini",
        base_url: str | None = settings.HUGGINGFACE_DEDICATED_ENDPOINT,
        api_key: str | None = settings.HUGGINGFACE_ACCESS_TOKEN,
        max_characters: int = 128,
        mock: bool = False,
        max_concurrent_requests: int = 4,
    ) -> None:
        self.model_id = model_id
        self.base_url = base_url
        self.api_key = api_key
        self.max_characters = max_characters
        self.mock = mock
        self.max_concurrent_requests = max_concurrent_requests

        if self.model_id == "tgi":
            assert self.base_url and self.api_key, (
                "Base URL and API key are required for TGI Hugging Face Dedicated Endpoint"
            )

            self.client = AsyncOpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
            )
        else:
            self.client = AsyncOpenAI()

    def __call__(self, content: str, chunks: list[str]) -> list[str]:
        """Process document chunks for contextual summarization.

        Args:
            content: The full document content
            chunks: List of document chunks to summarize

        Returns:
            list[str]: List of chunks with added contextual summaries
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            results = asyncio.run(self.__summarize_context_batch(content, chunks))
        else:
            results = loop.run_until_complete(
                self.__summarize_context_batch(content, chunks)
            )

        return results

    async def __summarize_context_batch(
        self, content: str, chunks: list[str]
    ) -> list[str]:
        """Asynchronously summarize multiple document chunks.

        Args:
            content: The full document content
            chunks: List of document chunks to summarize

        Returns:
            list[str]: List of chunks with added contextual summaries
        """

        process = psutil.Process(os.getpid())
        start_mem = process.memory_info().rss
        logger.debug(
            f"Starting summarizing document."
            f"Initial memory usage: {start_mem // (1024 * 1024)} MB"
        )

        document = await self.__summarize(
            document=ContextualDocument(content=content), await_time_seconds=20
        )

        end_mem = process.memory_info().rss
        memory_diff = end_mem - start_mem
        logger.debug(
            f"Summarization completed. "
            f"Final memory usage: {end_mem // (1024 * 1024)} MB, "
            f"Memory difference: {memory_diff // (1024 * 1024)} MB"
        )

        contextual_chunks = []
        for chunk in chunks:
            if document.contextual_summarization is not None:
                chunk = f"{document.contextual_summarization}\n\n{chunk}"
            else:
                chunk = f"{chunk}"

            contextual_chunks.append(chunk)

        return contextual_chunks

    async def __summarize(
        self,
        document: ContextualDocument,
        await_time_seconds: int = 2,
    ) -> ContextualDocument:
        """Generate a contextual summary for a single document.

        Args:
            document: The document to summarize
            await_time_seconds: Time in seconds to wait between requests

        Returns:
            ContextualDocument: Document with generated summary
        """

        if self.mock:
            return document.add_contextual_summarization("This is a mock summary")

        async def process_document() -> ContextualDocument:
            try:
                response = await self.client.chat.completions.create(
                    model=self.model_id,
                    messages=[
                        {
                            "role": "user",  # TODO: gemini model don't support system role
                            "content": self.SYSTEM_PROMPT_TEMPLATE.format(
                                characters=self.max_characters, content=document.content
                            ),
                        },
                    ],
                    stream=False,
                    temperature=0,
                )
                await asyncio.sleep(await_time_seconds)  # Rate limiting

                if not response.choices:
                    logger.warning("No contextual summary generated for chunk")
                    return document

                context_summary: str = response.choices[0].message.content
                return document.add_contextual_summarization(context_summary)
            except Exception as e:
                logger.warning(f"Failed to generate contextual summary: {str(e)}")
                return document

        return await process_document()
