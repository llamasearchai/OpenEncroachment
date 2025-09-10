Contributing to OpenEncroachment

Prerequisites:
- Python 3.10–3.12
- uv (https://docs.astral.sh/uv/)
- Git

Setup:
- ~/.local/bin/uv sync --all-extras --dev

Quality gates:
- Lint: ~/.local/bin/uvx ruff check .
- Type: ~/.local/bin/uvx mypy --strict src/open_encroachment
- Tests: ~/.local/bin/uvx tox -q

Commit hooks:
- ~/.local/bin/uvx pre-commit install
- ~/.local/bin/uvx pre-commit run --all-files

Running the pipeline:
- ~/.local/bin/uv run open-encroachment --config config/settings.yaml run-pipeline --sample-data

Serving Datasette:
- ~/.local/bin/uv run datasette -c datasette.yaml --reload

Agent:
- export OPENAI_API_KEY=...
- ~/.local/bin/uv run open-encroachment agent run "Summarize latest case status"

Security:
- Do not commit secrets (.env is gitignored)
- HTTPS webhook dispatcher supports mTLS; see config/dispatcher.yaml

Releases:
- Bump version in src/open_encroachment/__init__.py
- Tag: git tag -a v0.1.0 -m "v0.1.0"; git push --tags
