# DCP Tests

This directory contains the test suite for DCP (Docs Context Provider).

## Running Tests

### Run all tests

```bash
uv run pytest
```

### Run specific test file

```bash
uv run pytest tests/test_chunker.py
```

### Run with coverage

```bash
uv run pytest --cov=. --cov-report=html
```

### Run with verbose output

```bash
uv run pytest -v
```

## Test Structure

- `conftest.py` - Pytest fixtures and configuration
- `test_chunker.py` - Tests for document chunking
- `test_embedder.py` - Tests for document embedding
- `test_qdrant_client.py` - Tests for Qdrant database operations
- `test_server.py` - Tests for MCP server tools
- `test_fetcher.py` - Tests for documentation fetching

## Test Categories

Tests are marked with the following markers:

- `@pytest.mark.unit` - Unit tests (fast, no external dependencies)
- `@pytest.mark.integration` - Integration tests (may require external services)
- `@pytest.mark.slow` - Slow running tests

### Run only unit tests

```bash
uv run pytest -m unit
```

### Run only integration tests

```bash
uv run pytest -m integration
```

## Writing Tests

When writing new tests:

1. Use descriptive test names that explain what is being tested
2. Use fixtures from `conftest.py` for common test data
3. Mock external dependencies (HTTP requests, database calls)
4. Keep tests isolated and independent
5. Add appropriate markers for test categorization

## Example Test

```python
import pytest
from unittest.mock import Mock, patch

def test_example_function():
    """Test that example function works correctly."""
    # Arrange
    input_data = "test"

    # Act
    result = example_function(input_data)

    # Assert
    assert result == "expected output"
```
