.PHONY: help install verify sync sync-library server clean test format lint docker-build docker-run docker-stop deploy-railway deploy-render deploy-fly

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
	@echo ""
	@echo "Docker commands:"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run with docker-compose"
	@echo "  make docker-stop    - Stop docker-compose"

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

# Docker commands
docker-build:
	@echo "Building Docker image..."
	docker build -t dcp-server .

docker-run:
	@echo "Starting server with docker-compose..."
	docker-compose up -d
	@echo "Server running at http://localhost:8000"
	@echo "View logs: docker-compose logs -f"

docker-stop:
	@echo "Stopping docker-compose..."
	docker-compose down

# Deployment commands
deploy-railway:
	@echo "Deploying to Railway..."
	@echo "1. Push to GitHub: git push origin master"
	@echo "2. Go to railway.app and connect your repo"
	@echo "3. Add environment variables: QDRANT_URL, QDRANT_API_KEY"
	@echo "Railway will auto-detect Dockerfile and deploy"

deploy-render:
	@echo "Deploying to Render..."
	@echo "1. Push to GitHub: git push origin master"
	@echo "2. Go to render.com and create new Web Service"
	@echo "3. Connect your repo and select Docker runtime"
	@echo "4. Add environment variables: QDRANT_URL, QDRANT_API_KEY"

deploy-fly:
	@echo "Deploying to Fly.io..."
	@if ! command -v flyctl &> /dev/null; then \
		echo "Installing flyctl..."; \
		curl -L https://fly.io/install.sh | sh; \
	fi
	flyctl launch --name dcp-server --yes
	@echo "Set secrets:"
	@echo "  flyctl secrets set QDRANT_URL='your-url'"
	@echo "  flyctl secrets set QDRANT_API_KEY='your-key'"
	flyctl deploy
