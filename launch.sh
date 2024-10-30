pip install uv
uv venv
source .venv/bin/activate
uv sync
uv pip install -e .
uv pip list
uv run python experiments/data_utils.
source .venv/bin/activate