from datetime import datetime
from pathlib import Path
from typing import Any

import click

from pipelines import collect_notion_data, etl, gen_data, rag_index


@click.command(
    help="""
Leo CLI v0.0.1.

Main entry point for the pipeline execution.
This entrypoint is where everything comes together.

Run a pipeline with the required parameters. This executes
all steps in the pipeline in the correct order using the orchestrator
stack component that is configured in your active ZenML stack.

Examples:

  \b
  # Run the pipeline with default options
  python run.py

  \b
  # Run the pipeline without cache
  python run.py --no-cache

  \b
  # Run only the Notion data collection pipeline
  python run.py --run-collect-notion-data

"""
)
@click.option(
    "--no-cache",
    is_flag=True,
    default=False,
    help="Disable caching for the pipeline run.",
)
@click.option(
    "--run-collect-notion-data-pipeline",
    is_flag=True,
    default=False,
    help="Whether to run the collection data from Notion pipeline.",
)
@click.option(
    "--run-etl-pipeline",
    is_flag=True,
    default=False,
    help="Whether to run the ETL pipeline.",
)
@click.option(
    "--run-gen-data-pipeline",
    is_flag=True,
    default=False,
    help="Whether to run the generate data pipeline.",
)
@click.option(
    "--run-rag-index-pipeline",
    is_flag=True,
    default=False,
    help="Whether to run the RAG indexing pipeline.",
)
def main(
    no_cache: bool = False,
    run_collect_notion_data_pipeline: bool = False,
    run_etl_pipeline: bool = False,
    run_gen_data_pipeline: bool = False,
    run_rag_index_pipeline: bool = False,
) -> None:
    assert (
        run_collect_notion_data_pipeline
        or run_etl_pipeline
        or run_gen_data_pipeline
        or run_rag_index_pipeline
    ), "Please specify an action to run."

    pipeline_args: dict[str, Any] = {
        "enable_cache": not no_cache,
    }
    root_dir = Path(__file__).resolve().parent.parent

    if run_collect_notion_data_pipeline:
        run_args = {}
        pipeline_args["config_path"] = root_dir / "configs" / "collect_notion_data.yaml"
        assert pipeline_args["config_path"].exists(), (
            f"Config file not found: {pipeline_args['config_path']}"
        )
        pipeline_args["run_name"] = (
            f"collect_notion_data_run_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"
        )
        collect_notion_data.with_options(**pipeline_args)(
            **run_args
        )  # log config by zenml

    if run_etl_pipeline:
        run_args = {}
        pipeline_args["config_path"] = root_dir / "configs" / "etl.yaml"
        assert pipeline_args["config_path"].exists(), (
            f"Config file not found: {pipeline_args['config_path']}"
        )
        pipeline_args["run_name"] = (
            f"etl_run_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"
        )
        etl.with_options(**pipeline_args)(**run_args)

    if run_gen_data_pipeline:
        run_args = {}
        pipeline_args["config_path"] = root_dir / "configs" / "gen_data.yaml"
        assert pipeline_args["config_path"].exists(), (
            f"Config file not found: {pipeline_args['config_path']}"
        )
        pipeline_args["run_name"] = (
            f"gen_data_run_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"
        )
        gen_data.with_options(**pipeline_args)(**run_args)

    if run_rag_index_pipeline:
        run_args = {}
        pipeline_args["config_path"] = root_dir / "configs" / "rag_index.yaml"
        assert pipeline_args["config_path"].exists(), (
            f"Config file not found: {pipeline_args['config_path']}"
        )
        pipeline_args["run_name"] = (
            f"rag_index_run_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"
        )
        rag_index.with_options(**pipeline_args)(**run_args)


if __name__ == "__main__":
    main()
