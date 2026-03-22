.PHONY: help install verify sync sync-library server clean test format lint

help:
	@echo "DCP - Docs Context Provider"
	@echo ""
	@echo "Available commands:"
	@echo "  make install        - Install dependencies"
	@echo "  make sync           - Sync all libraries"
	@echo "  make sync-library   - Sync specific library (usage: make sync-library LIB=agno)"
	@echo "  make server         - Start MCP server"
	@echo "  make clean          - Clean cache and build files"
	@echo "  make format         - Format code with black"
	@echo "  make lint           - Lint code with ruff"
	@echo "  make test           - Run tests"

install:
	@echo "Installing dependencies..."
	uv pip install -e ".[dev]"

sync:
	@echo "Syncing all libraries..."
	uv run python -m scraper.fetcher --sync-all

sync-library:
	@ifndef LIB
		@echo "Error: Please specify library with LIB=name"
		@echo "Example: make sync-library LIB=agno"
		@exit 1
	@endif
	@echo "Syncing library: $(LIB)"
	uv run python -m scraper.fetcher --library $(LIB)

server:
	@echo "Starting MCP server..."
	uv run python -m mcp_server.server

clean:
	@echo "Cleaning cache and build files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/
	@echo "Cleaned"

format:
	@echo "Formatting code with black..."
	uv run black .

lint:
	@echo "Linting code with ruff..."
	uv run ruff check .

test:
	@echo "Running tests..."
	uv run pytest -v
