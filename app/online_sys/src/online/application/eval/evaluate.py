from pathlib import Path

from loguru import logger
from opik.evaluation import evaluate
from opik.evaluation.metrics import AnswerRelevance, Hallucination, Moderation

from online import opik_utils
from online.application.agents import agents, extract_tool_responses
from online.config import settings

from .sum_heuristic import SummaryHeuristic
from .sum_judge import SummaryJudge

opik_utils.configure()


def evaluate_agent(prompts: list[str], retriever_config: Path) -> None:
    assert settings.COMET_API_KEY, (
        "COMET_API_KEY is not set. We need it to track the experiment with Opik."
    )

    logger.info("Starting evaluation...")
    logger.info(f"Evaluating agent with {len(prompts)} prompts.")

    def evaluation_task(sample: dict) -> dict:
        """Call agentic app logic to evaluate."""

        agent = agents.get_agent(retriever_config=retriever_config)
        response = agent.run(sample["input"])
        context = extract_tool_responses(agent)

        return {
            "input": sample["input"],
            "context": context,
            "output": response,
        }

    # Get or create dataset
    dataset_name = "leo_rag_agentic_app_eval_dataset"
    dataset = opik_utils.get_or_create_dataset(name=dataset_name, prompts=prompts)

    # Evaluate
    agent = agents.get_agent(retriever_config=retriever_config)

    # ! don't hard fix GEMINI_MODEL_ID
    experiment_config = {
        "model_id": settings.GEMINI_MODEL_ID,
        "retriever_config": retriever_config,
        "agent_config": {
            "max_steps": agent.max_steps,
            "agent_name": agent.name,
        },
    }
    scoring_metrics = [
        Hallucination(model=settings.GEMINI_MODEL_ID),
        AnswerRelevance(model=settings.GEMINI_MODEL_ID),
        Moderation(model=settings.GEMINI_MODEL_ID),
        SummaryHeuristic(),
        SummaryJudge(),
    ]

    if dataset:
        logger.info("Evaluation details:")
        logger.info(f"Dataset: {dataset_name}")
        logger.info(f"Metrics: {[m.__class__.__name__ for m in scoring_metrics]}")

        evaluate(
            dataset=dataset,
            task=evaluation_task,
            scoring_metrics=scoring_metrics,
            experiment_config=experiment_config,
            task_threads=2,
        )
    else:
        logger.error("Can't run the evaluation as the dataset items are empty.")
