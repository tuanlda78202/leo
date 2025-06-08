from pathlib import Path
from typing import Any

from loguru import logger
from opik import opik_context, track
from smolagents import (
    LiteLLMModel,
    MessageRole,
    MultiStepAgent,
    ToolCallingAgent,
)

from online.config import settings

from .tools import (
    GeminiSummarizerTool,
    HuggingFaceEndpointSummarizerTool,
    MongoDBRetrieverTool,
    OpenAISummarizerTool,
    iam,
)


def get_agent(
    retriever_config: Path = Path("configs/rag_index.yaml"),
) -> "AgentWrapper":
    agent = AgentWrapper.build_from_smolagents(retriever_config=retriever_config)

    return agent


class AgentWrapper:
    def __init__(self, agent: MultiStepAgent) -> None:
        self.__agent = agent

    @property
    def input_messages(self) -> list[dict]:
        if hasattr(self.__agent, "write_memory_to_messages"):
            return self.__agent.write_memory_to_messages()
        # Fallback or error if method not found; for now, assume it exists based on smolagents docs
        # Or you might need to parse self.__agent.memory.steps manually if this method is unavailable
        # in your specific smolagents version or agent type.
        logger.warning(
            "Agent does not have 'write_memory_to_messages' method. Returning empty message list."
        )
        return []

    @property
    def name(self) -> str:
        return self.__agent.name

    @property
    def max_steps(self) -> str:
        return self.__agent.max_steps

    @classmethod
    def build_from_smolagents(cls, retriever_config: Path) -> "AgentWrapper":
        retriever_tool = MongoDBRetrieverTool(config_path=retriever_config)

        if settings.HUGGINGFACE_DEDICATED_ENDPOINT:
            logger.warning(
                f"Using Hugging Face dedicated endpoint as the summarizer with URL: {settings.HUGGINGFACE_DEDICATED_ENDPOINT}"
            )
            summarizer_tool = HuggingFaceEndpointSummarizerTool()
        elif settings.OPENAI_API_KEY:
            logger.warning(
                f"Using OpenAI as the summarizer with model: {settings.OPENAI_MODEL_ID}"
            )
            summarizer_tool = OpenAISummarizerTool(stream=False)
        else:
            logger.warning(
                f"Using Gemini as the summarizer with model: {settings.GEMINI_MODEL_ID}"
            )
            summarizer_tool = GeminiSummarizerTool()

        model = LiteLLMModel(
            model_id=settings.GEMINI_MODEL_ID,
            # api_base="https://api.openai.com/v1",  # TODO: support vLLM localhost or Gemini API
            api_key=settings.GEMINI_API_KEY,
        )

        agent = ToolCallingAgent(
            tools=[iam, retriever_tool, summarizer_tool],
            model=model,
            max_steps=3,
            verbosity_level=2,
            # planning_interval=2,
            add_base_tools=True,
        )

        return cls(agent)

    @track(name="Agent.run")
    def run(self, task: str, **kwargs) -> Any:
        result = self.__agent.run(task, **kwargs)

        model = self.__agent.model
        metadata = {
            "prompt_templates": self.__agent.prompt_templates,
            "tools": self.__agent.tools,
            "model_id": self.__agent.model.model_id,
            "input_token_count": model.last_input_token_count,
            "output_token_count": model.last_output_token_count,
        }
        if hasattr(self.__agent, "step_number"):
            metadata["step_number"] = self.__agent.step_number

        opik_context.update_current_trace(
            tags=["agent"],
            metadata=metadata,
        )

        return result


def extract_tool_responses(
    agent_wrapper: "AgentWrapper",
) -> str:
    """
    Extracts and concatenates all tool response contents with numbered observation delimiters.

    Args:
        agent_wrapper (AgentWrapper): The agent wrapper containing message dictionaries with 'role' and 'content' keys

    Returns:
        str: Tool response contents separated by numbered observation delimiters

    Example:
        >>> messages = [
        ...     {"role": MessageRole.TOOL_RESPONSE, "content": "First response"},
        ...     {"role": MessageRole.USER, "content": "Question"},
        ...     {"role": MessageRole.TOOL_RESPONSE, "content": "Second response"}
        ... ]
        >>> extract_tool_responses(messages)
        "-------- OBSERVATION 1 --------\nFirst response\n-------- OBSERVATION 2 --------\nSecond response"
    """

    all_messages = agent_wrapper.input_messages

    tool_responses = [
        msg["content"]
        for msg in all_messages
        if msg.get("role") == MessageRole.TOOL_RESPONSE.value
    ]

    return "\n".join(
        f"-------- OBSERVATION {i + 1} --------\n{response}"
        for i, response in enumerate(tool_responses)
    )
