import os

import opik
from loguru import logger
from opik import Dataset, Opik
from opik.configurator.configure import OpikConfigurator

from online.config import settings


def configure() -> None:
    if settings.COMET_API_KEY and settings.COMET_PROJECT:
        try:
            client = OpikConfigurator(api_key=settings.COMET_API_KEY)
            default_workspace = client._get_default_workspace()
        except Exception:
            logger.warning(
                "Default workspace not found. Setting workspace to None and enabling interactive mode."
            )
            default_workspace = None

        os.environ["OPIK_PROJECT_NAME"] = settings.COMET_PROJECT

        opik.configure(
            api_key=settings.COMET_API_KEY,
            workspace=default_workspace,
            use_local=False,
            force=True,
        )
        logger.info(
            f"Opik configured successfully using workspace '{default_workspace}'"
        )
    else:
        logger.warning(
            "COMET_API_KEY and COMET_PROJECT are not set. Set them to enable prompt monitoring with Opik (powered by Comet ML)."
        )


def get_or_create_dataset(name: str, prompts: list[str]) -> Dataset | None:
    client = Opik()
    try:
        dataset = client.get_dataset(name=name)
    except Exception:
        dataset = None

    if dataset:
        logger.warning(f"Dataset '{name}' already exists. Skipping dataset creation.")

        return dataset

    assert prompts, "Prompts are required to create a dataset."

    dataset_items = []
    for prompt in prompts:
        dataset_items.append(
            {
                "input": prompt,
            }
        )

    dataset = create_dataset(
        name=name,
        description="Dataset for evaluating the agentic app.",
        items=dataset_items,
    )

    return dataset


def create_dataset(name: str, description: str, items: list[dict]) -> opik.Dataset:
    client = Opik()

    dataset = client.get_or_create_dataset(name=name, description=description)
    dataset.insert(items)

    dataset = client.get_dataset(name=name)

    return dataset
