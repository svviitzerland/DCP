# Multi-stage build for smaller image
FROM python:3.11-slim as builder

WORKDIR /app

# Install uv for faster dependency installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./
COPY README.md ./

# Copy source code needed for installation
COPY mcp_server ./mcp_server
COPY db ./db
COPY scraper ./scraper
COPY providers ./providers

# Install dependencies
RUN uv pip install --system --no-cache .

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY mcp_server ./mcp_server
COPY db ./db
COPY scraper ./scraper
COPY providers ./providers

# Expose port (FastMCP default is 8000)
EXPOSE 8000

# Add healthcheck endpoint support
ENV PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import httpx; httpx.get('http://localhost:8000/health', timeout=2)" || exit 1

# Run the server
CMD ["python", "-m", "mcp_server.server"]
