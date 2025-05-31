from pathlib import Path
from typing import List

import click

from online.application.eval import evaluate_agent

# ! Expand more edge cases, ensuring that changes do not degrade its capabilities
EVALUATION_PROMPTS: List[str] = [
    """
    Write me a paragraph on the feature/training/inference (FTI) pipelines architecture following the next structure:

    - introduction
    - what are its main components
    - why it's powerful
    Retrieve the sources when compiling the answer. Also, return the sources you used as context.
    """,
    "What is the feature/training/inference (FTI) pipelines architecture?",
    "What is the Tensorflow Recommenders Python package?",
    """How does RLHF: Reinforcement Learning from Human Feedback work?
    Explain to me:
    - what is RLHF
    - how it works
    - why it's important
    - what are the main components
    - what are the main challenges
    """,
    "List 3 LLM frameworks for building LLM applications and why they are important.",
    "Explain how does Bidirectional Encoder Representations from Transformers (BERT) work. Focus on what architecture it uses, how it's different from other models and how they are trained.",
    "List 5 ways or tools to process PDFs for LLMs and RAG",
    """How can I optimize my LLMs during inference?
    Provide a list of top 3 best practices, while providing a short explanation for each, which contains why it's important.
    """,
    "Explain to me in more detail how does an Agent memory work and why do we need it when building Agentic apps.",
    "What is the difference between a vector database and a vector index?",
    "Recommend me a course on LLMs and RAG",
    "How Document Chunk overlap affects a RAG pipeline and it's performance?",
    """What is the importance of re-ranking chunks for RAG?
    Explain to me:
    - what is re-ranking
    - how it works
    - why it's important
    - what are the main components
    - what are the main trade-offs
    """,
    "List the most popular advanced RAG techniques to optimize RAG performance and why they are important.",
    "List what are the main ways of evaluating a RAG pipeline and why they are important.",
]


@click.command()
@click.option(
    "--retriever-config",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to the retriever configuration file",
)
def main(retriever_config: Path) -> None:
    """Evaluate agent with custom retriever configuration."""
    evaluate_agent(EVALUATION_PROMPTS, retriever_config=retriever_config)


if __name__ == "__main__":
    main()
