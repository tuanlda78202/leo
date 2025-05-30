from pathlib import Path

import click
from smolagents import GradioUI

from online.application.agents import get_agent


@click.command()
@click.option(
    "--retriever-config",
    type=click.Path(exists=True),
    required=True,
    help="Path to the retriever config file",
)
@click.option(
    "--ui",
    is_flag=True,
    default=False,
    help="Launch with Gradio UI instead of CLI mode",
)
@click.option(
    "--query",
    "-q",
    type=str,
    default=False,
    help="Query to run in CLI mode",
)
def main(retriever_config: Path, ui: bool, query: str) -> None:
    """Run the agent either in Gradio UI or CLI mode.

    Args:
        ui: If True, launches Gradio UI. If False, runs in CLI mode
        query: Query string to run in CLI mode
    """
    agent = get_agent(retriever_config=Path(retriever_config))
    
    if ui:
        GradioUI(agent).launch()
    else:
        assert query, "Query is required in CLI mode"

        result = agent.run(query)

        print(result)


if __name__ == "__main__":
    main()
