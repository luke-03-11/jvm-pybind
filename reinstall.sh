uv pip uninstall jvm || true
deactivate || true
rm -rf .venv
uv sync
uv build
uv pip install dist/jvm-0.1.0-py3-none-any.whl
source .venv/bin/activate
