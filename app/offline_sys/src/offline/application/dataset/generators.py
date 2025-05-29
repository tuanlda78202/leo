import copy
from typing import Callable

from loguru import logger

from offline.application.agents import SummarizationAgent
from offline.domain import Document, InstructDataset
from offline.domain.instruct_data import InstructDatasetSample


class SummarizationDatasetGenerator:
    """Generates an instruction dataset from documents by creating summaries.

    This class takes a list of documents and generates summaries using a specified
    language model. The resulting dataset can be split into training, validation,
    and test sets.

    Args:
        summarization_model: Name/ID of the model to use for summarization.
        summarization_max_characters: Maximum number of characters for the summary.
        val_split_ratio: Fraction of data to use for validation (0-1).
        test_split_ratio: Fraction of data to use for testing (0-1).
        max_workers: Maximum number of parallel workers for processing.
        mock: If True, generates mock summaries instead of using the model.
        min_document_length: Minimum length of document content to be processed.
        min_quality_score: Minimum content quality score for document filtering.
        max_summary_length_factor: Maximum factor to multiply summarization_max_characters for filtering.
        augmentation_loops: Number of loops for summarization.
    """

    def __init__(
        self,
        summarization_model: str,
        summarization_max_characters: int,
        val_split_ratio: float = 0.1,
        test_split_ratio: float = 0.1,
        max_workers: int = 10,
        mock: bool = False,
        min_document_length: int = 50,
        min_quality_score: float = 0.3,
        max_summary_length_factor: float = 2,
        augmentation_loops: int = 4,
    ) -> None:
        self.summarization_model = summarization_model
        self.summarization_max_characters = summarization_max_characters
        self.val_split_ratio = val_split_ratio
        self.test_split_ratio = test_split_ratio
        self.max_workers = max_workers
        self.mock = mock
        self.min_document_length = min_document_length
        self.min_quality_score = min_quality_score
        self.max_summary_length_factor = max_summary_length_factor
        self.augmentation_loops = augmentation_loops

        # ! Filter FUNCTIONS to apply before and after summarization
        self.pre_generation_filters: list[Callable[[Document], bool]] = [
            lambda document: len(document.content) > self.min_document_length,
            lambda document: document.content_quality_score is None
            or document.content_quality_score >= self.min_quality_score,
        ]
        self.post_generation_filters: list[Callable[[Document], bool]] = [
            lambda document: document.summary is not None
            and len(document.summary)
            < int(self.summarization_max_characters * self.max_summary_length_factor),
        ]

    def generate(self, documents: list[Document]) -> InstructDataset:
        """Generates an instruction dataset from the documents.

        Filters, summarizes documents and converts them into instruction-answer pairs.
        Warns if input document count is less than recommended minimum of 10.

        Args:
            documents: List of Document objects to be processed into the dataset.

        Returns:
            InstructDataset containing instruction-answer pairs where instructions are
            document contents and answers are generated summaries.

        Warns:
            If less than 10 documents are provided for processing.
        """

        if len(documents) < 10:
            logger.warning(
                "Less than 10 documents to summarize. For accurate behavior we recommend having at least 10 documents."
            )

        filtered_summarized_documents = self.__summarize_documents(documents)

        # ! Pydantic model validation
        instruct_dataset_samples = [
            self.__to_instruct_dataset_sample(summarized_document)
            for summarized_document in filtered_summarized_documents
            if summarized_document
        ]
        logger.info(f"Num instruct dataset samples: {len(instruct_dataset_samples)}")

        # ! Split into train/val/test sets
        return InstructDataset.from_samples(
            samples=instruct_dataset_samples,
            val_split_ratio=self.val_split_ratio,
            test_split_ratio=self.test_split_ratio,
            seed=42,
        )

    def __summarize_documents(self, documents: list[Document]) -> list[Document]:
        """Summarizes the filtered documents using a summarization agent.

        Args:
            documents: List of documents to summarize

        Returns:
            list[Document]: List of documents with generated summaries that pass
                both pre and post-generation filters
        """

        # ! Pre-generation filtering
        logger.info(f"Num documents before pre-generation filtering: {len(documents)}")
        filtered_documents = self.filter_documents(
            self.pre_generation_filters, documents
        )
        logger.info(
            f"Num documents after pre-generation filtering: {len(filtered_documents)}"
        )

        # ! Summarization loop with augmentation
        summarized_documents: list[Document] = self.__augmented_summarization_loop(
            filtered_documents, loops=self.augmentation_loops
        )

        # ! Post-generation filtering
        logger.info(
            f"Num documents before post-generation filtering: {len(summarized_documents)}"
        )
        filtered_summarized_documents = self.filter_documents(
            self.post_generation_filters, summarized_documents
        )
        logger.info(
            f"Num documents after post-generation filtering: {len(filtered_summarized_documents)}"
        )

        return filtered_summarized_documents

    def __augmented_summarization_loop(
        self, documents: list[Document], loops: int = 3
    ) -> list[Document]:
        """Performs multiple summarization passes with increasing temperature.

        Args:
            documents: List of documents to summarize.
            loops: Number of summarization iterations with different temperatures.

        Returns:
            List of documents with generated summaries, including multiple versions
            of each document summarized with different temperatures.
        """

        summarization_agent = SummarizationAgent(
            max_characters=self.summarization_max_characters,
            model_id=self.summarization_model,
            max_concurrent_requests=self.max_workers,
            mock=self.mock,
        )
        augmented_documents = []
        for i in range(loops):
            temperature = i * 0.5 / loops  # 0.0 to 0.5
            logger.info(
                f"Loop {i + 1} of {loops} - Summarizing documents with temperature {temperature}"
            )

            copied_documents = copy.deepcopy(documents)
            summarized_documents = summarization_agent(
                copied_documents, temperature=temperature
            )
            valid_summarized_documents = [
                doc for doc in summarized_documents if doc.summary is not None
            ]
            augmented_documents.extend(valid_summarized_documents)

        return augmented_documents

    def filter_documents(
        self, filters: list[Callable[[Document], bool]], documents: list[Document]
    ) -> list[Document]:
        """Filters documents using provided filter functions.

        Args:
            filters: List of filter functions that take a Document and return bool.
            documents: List of documents to filter.

        Returns:
            List of documents that pass all filter functions.
        """

        for document_filter in filters:
            documents = [
                document for document in documents if document_filter(document)
            ]

        return documents

    def __to_instruct_dataset_sample(self, document: Document) -> InstructDatasetSample:
        """Converts a summarized document to an instruction dataset sample.

        Args:
            document: A Document object containing both content and summary.

        Returns:
            InstructDatasetSample with document content as instruction and
            summary as answer.

        Raises:
            AssertionError: If the document's summary is None.
        """

        assert document.summary is not None, "Document summary is None"

        return InstructDatasetSample(
            instruction=document.content,
            answer=document.summary,
        )
