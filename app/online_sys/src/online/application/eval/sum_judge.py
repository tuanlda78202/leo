import json
from typing import Any

from opik.evaluation.metrics import base_metric, score_result
from opik.evaluation.models import LiteLLMChatModel
from pydantic import BaseModel

from online.config import settings


class LLMJudgeStyleOutputResult(BaseModel):
    score: int
    reason: str


class SummaryJudge(base_metric.BaseMetric):
    """
    A metric that evaluates whether an LLM's output has appropriate length and density.

    This metric uses another LLM to judge if the output length is appropriate for the given instruction.
    It returns a normalized score between 0 and 1, where:
    - 0.0 (Poor): Output is either too short and incomplete, or too long with unnecessary information
    - 0.5 (Good): Output has decent length balance but still slightly too short or too long
    - 1.0 (Excellent): Output length is appropriate, answering the question concisely without being verbose
    """

    def __init__(
        self,
        name: str = "summary_judge",
        model_name: str = settings.GEMINI_MODEL_ID,
    ) -> None:
        self.name = name
        self.llm_client = LiteLLMChatModel(model_name=model_name)

        self.prompt_template = """
        You are an impartial expert judge. Evaluate the quality of a given answer to an instruction based on how long the answer it is.

        How to decide whether the lengths of the answer is appropriate:
        1 (Poor): Too short, does not answer the question OR too long, it contains too much noise and un-required information, where the answer could be more concise.
        2 (Good): Good length balance of the answer, but the answer is still too short OR too long.
        3 (Excellent): The length of the answer is appropriate, it answers the question and is not too long or too short.

        Example of bad answer that is too short:
        <answer>
        LangChain, LlamaIndex, Haystack
        </answer>

        Example of bad answer that is too long:
        <answer>
        LangChain is a powerful and versatile framework designed specifically for building sophisticated LLM applications. It provides comprehensive abstractions for essential components like prompting, memory management, agent behaviors, and chain orchestration. The framework boasts an impressive ecosystem with extensive integrations across various tools and services, making it highly flexible for diverse use cases. However, this extensive functionality comes with a steeper learning curve that might require dedicated time to master.

        LlamaIndex (which was formerly known as GPTIndex) has carved out a specialized niche in the LLM tooling landscape, focusing primarily on data ingestion and advanced indexing capabilities for Large Language Models. It offers a rich set of sophisticated mechanisms to structure and query your data, including vector stores for semantic similarity search, keyword indices for traditional text matching, and tree indices for hierarchical data organization. While it particularly shines in Retrieval-Augmented Generation (RAG) applications, its comprehensive feature set might be excessive for more straightforward implementation needs.

        Haystack stands out as a robust end-to-end framework that places particular emphasis on question-answering systems and semantic search capabilities. It provides a comprehensive suite of document processing tools and comes equipped with production-ready pipelines that can be deployed with minimal configuration. The framework includes advanced features like multi-stage retrieval, document ranking, and reader-ranker architectures. While these capabilities make it powerful for complex information retrieval tasks, new users might find the initial configuration and architecture decisions somewhat challenging to navigate.

        Each of these frameworks brings unique strengths to the table while sharing some overlapping functionality. The choice between them often depends on specific use cases, technical requirements, and team expertise. LangChain offers the broadest general-purpose toolkit, LlamaIndex excels in data handling and RAG, while Haystack provides the most streamlined experience for question-answering systems.
        </answer>

        Example of excellent answer that is appropriate:
        <answer>
        1. LangChain is a powerful framework for building LLM applications that provides abstractions for prompting, memory, agents, and chains. It has extensive integrations with various tools and services, making it highly flexible but potentially complex to learn.
        2. LlamaIndex specializes in data ingestion and indexing for LLMs, offering sophisticated ways to structure and query your data through vector stores, keyword indices, and tree indices. It excels at RAG applications but may be overkill for simpler use cases.
        3. Haystack is an end-to-end framework focused on question-answering and semantic search, with strong document processing capabilities and ready-to-use pipelines. While powerful, its learning curve can be steep for beginners.
        </answer>

        Instruction: {input}

        Answer: {output}

        Provide your evaluation in JSON format with the following structure:
        {{
            "accuracy": {{
                "reason": "...",
                "score": 0
            }},
            "style": {{
                "reason": "...",
                "score": 0
            }}
        }}
        """

    def score(self, input: str, output: str, **ignored_kwargs: Any):
        """
        Score the output of an LLM.

        Args:
            output: The output of an LLM to score.
            **ignored_kwargs: Any additional keyword arguments. This is important so that the metric can be used in the `evaluate` function.
        """

        prompt = self.prompt_template.format(input=input, output=output)

        model_output = self.llm_client.generate_string(
            input=prompt, response_format=LLMJudgeStyleOutputResult
        )

        return self._parse_model_output(model_output)

    def _parse_model_output(self, content: str) -> score_result.ScoreResult:
        dict_content = json.loads(content)

        score = dict_content["score"]
        assert 1 <= score <= 3, f"Invalid score value: {score}"

        score = (score - 1) / 2.0  # Normalize the score to be between 0 and 1

        return score_result.ScoreResult(
            name=self.name,
            value=score,
            reason=dict_content["reason"],
        )
