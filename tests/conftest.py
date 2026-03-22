"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import Mock, MagicMock
from pathlib import Path
import json


@pytest.fixture
def mock_qdrant_client():
    """Mock Qdrant client for testing."""
    client = Mock()
    client.get_collections.return_value = Mock(collections=[])
    client.create_collection.return_value = None
    client.upsert.return_value = None
    client.query_points.return_value = Mock(points=[])
    client.scroll.return_value = ([], None)
    return client


@pytest.fixture
def sample_provider_config():
    """Sample provider configuration."""
    return {
        "test-library": {
            "llms_txt": "https://example.com/llms.txt",
            "llms_full_txt": None,
            "docs": "https://example.com/docs",
            "version": "latest",
            "description": "Test library"
        }
    }


@pytest.fixture
def sample_chunks():
    """Sample document chunks for testing."""
    return [
        {
            "text": "This is a test chunk",
            "embedding": [0.1] * 384,
            "metadata": {
                "source_url": "https://example.com",
                "chunk_index": 0,
                "total_chunks": 2
            }
        },
        {
            "text": "This is another test chunk",
            "embedding": [0.2] * 384,
            "metadata": {
                "source_url": "https://example.com",
                "chunk_index": 1,
                "total_chunks": 2
            }
        }
    ]


@pytest.fixture
def mock_embedder():
    """Mock embedder for testing."""
    embedder = Mock()
    embedder.embed_chunks.return_value = [
        {
            "text": "test",
            "embedding": [0.1] * 384,
            "metadata": {"source_url": "test", "chunk_index": 0, "total_chunks": 1}
        }
    ]
    embedder.embed_query.return_value = [0.1] * 384
    return embedder
