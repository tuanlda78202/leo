from typing import Annotated

from loguru import logger
from zenml import get_step_context, step

from offline.application.agents.quality import HeuristicQualityAgent, QualityScoreAgent
from offline.domain.document import Document


@step
def add_quality_score(
    documents: list[Document],
    model_id: str = "gpt-4o-mini",
    mock: bool = False,
    max_workers: int = 10,
) -> Annotated[list[Document], "scored_docs"]:
    """Adds quality scores to documents using heuristic and model-based scoring agents.

    This function processes documents in two stages:
    1. Applies heuristic-based quality scoring
    2. Uses a model-based quality agent for documents that weren't scored by heuristics

    Args:
        documents: List of documents to evaluate for quality
        model_id: Identifier for the model to use in quality assessment.
        mock: If True, uses mock responses instead of real model calls.
        max_workers: Maximum number of concurrent quality check operations.

    Returns:
        list[Document]: Documents enhanced with quality scores, annotated as
            "scored_docs" for pipeline metadata tracking

    Note:
        The function adds metadata to the step context including the total number
        of documents and how many received quality scores.
    """

    # ! Heuristic scoring
    heuristic_agent = HeuristicQualityAgent()
    scored_docs: list[Document] = heuristic_agent(documents)

    scored_docs_with_heuristics = [
        d for d in scored_docs if d.content_quality_score is not None
    ]
    docs_without_scores = [d for d in scored_docs if d.content_quality_score is None]

    logger.info(f"Documents scored with heuristics: {len(scored_docs_with_heuristics)}")
    logger.info(
        f"Documents without scores after heuristics: {len(docs_without_scores)}"
    )

    # ! Model-based scoring
    logger.info(f"Scoring {len(docs_without_scores)} documents with model {model_id}")
    score_agent = QualityScoreAgent(
        model_id=model_id, mock=mock, max_concurrent_requests=max_workers
    )
    scored_docs_with_model: list[Document] = score_agent(docs_without_scores)

    # Log
    scored_docs: list[Document] = scored_docs_with_heuristics + scored_docs_with_model

    len_documents = len(documents)
    len_documents_with_scores = len(
        [doc for doc in scored_docs if doc.content_quality_score is not None]
    )
    logger.info(f"Total documents: {len_documents}")
    logger.info(f"Total documents that were scored: {len_documents_with_scores}")

    # ZenML logging
    step_context = get_step_context()
    step_context.add_output_metadata(
        output_name="scored_docs",
        metadata={
            "len_documents": len_documents,
            "len_documents_with_scores": len_documents_with_scores,
            "len_documents_scored_with_heuristics": len(scored_docs_with_heuristics),
            "len_documents_scored_with_agents": len(scored_docs_with_model),
        },
    )

    return scored_docs
