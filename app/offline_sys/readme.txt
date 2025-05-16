# installation
~pwd = app/offline_sys

# uv init --bare --python 3.12
# source activate .venv/bin/activate

UV_PROJECT_ENVIRONMENT=.venv-offline uv sync # if you have a pyproject.toml
uv pip install -e . # offline package inside src

craw4ai-setup
craw4ai-doctor

# infrastructure
make local-infra-up # docker container only start port 27017, if u want UI, download mongo-compass
make local-infra-down

# project structure
```bash
.
├── configs/                   # ZenML configuration files
├── pipelines/                 # ZenML ML pipeline definitions
├── src/second_brain_offline/  # Main package directory
│   ├── application/           # Application layer
│   ├── domain/                # Domain layer
│   ├── infrastructure/        # Infrastructure layer
│   ├── config.py              # Configuration settings
│   └── utils.py               # Utility functions
├── steps/                     # ZenML pipeline steps
├── tests/                     # Test files
├── tools/                     # Entrypoint scripts that use the Python package
├── .env.example               # Environment variables template
├── .python-version            # Python version specification
├── Makefile                   # Project commands
└── pyproject.toml             # Project dependencies
```