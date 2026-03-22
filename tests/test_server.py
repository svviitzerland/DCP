"""Tests for MCP server tools."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from mcp_server.server import list_libraries, get_docs, search_docs, search_all_docs


@patch('mcp_server.server.load_providers')
def test_list_libraries(mock_load_providers):
    """Test listing all libraries."""
    mock_load_providers.return_value = {
        "test-lib1": {
            "description": "Test library 1",
            "version": "1.0",
            "docs": "https://test1.com"
        },
        "test-lib2": {
            "description": "Test library 2",
            "version": "2.0",
            "docs": "https://test2.com"
        }
    }

    result = list_libraries()

    assert len(result) == 2
    assert result[0]["name"] == "test-lib1"
    assert result[0]["description"] == "Test library 1"
    assert result[1]["name"] == "test-lib2"


@patch('mcp_server.server.get_db')
@patch('mcp_server.server.load_providers')
def test_get_docs_success(mock_load_providers, mock_get_db):
    """Test getting documentation for a library."""
    mock_load_providers.return_value = {
        "test-lib": {"description": "Test"}
    }

    mock_db = Mock()
    mock_db.get_all_chunks.return_value = [
        {"text": "chunk 1", "chunk_index": 0},
        {"text": "chunk 2", "chunk_index": 1}
    ]
    mock_get_db.return_value = mock_db

    result = get_docs("test-lib")

    assert "chunk 1" in result
    assert "chunk 2" in result


@patch('mcp_server.server.get_db')
@patch('mcp_server.server.load_providers')
def test_get_docs_library_not_found(mock_load_providers, mock_get_db):
    """Test getting docs for non-existent library."""
    mock_load_providers.return_value = {
        "test-lib": {"description": "Test"}
    }

    result = get_docs("non-existent")

    assert "Error" in result
    assert "not found" in result


@patch('mcp_server.server.get_embedder')
@patch('mcp_server.server.get_db')
@patch('mcp_server.server.load_providers')
def test_search_docs(mock_load_providers, mock_get_db, mock_get_embedder):
    """Test searching within a library."""
    mock_load_providers.return_value = {
        "test-lib": {"description": "Test"}
    }

    mock_embedder = Mock()
    mock_embedder.embed_query.return_value = [0.1] * 384
    mock_get_embedder.return_value = mock_embedder

    mock_db = Mock()
    mock_db.search.return_value = [
        {
            "score": 0.9,
            "text": "test result",
            "library": "test-lib",
            "source_url": "https://test.com",
            "chunk_index": 0
        }
    ]
    mock_get_db.return_value = mock_db

    result = search_docs("test-lib", "test query", limit=5)

    assert len(result) == 1
    assert result[0]["score"] == 0.9
    assert result[0]["library"] == "test-lib"


@patch('mcp_server.server.get_embedder')
@patch('mcp_server.server.get_db')
def test_search_all_docs(mock_get_db, mock_get_embedder):
    """Test searching across all libraries."""
    mock_embedder = Mock()
    mock_embedder.embed_query.return_value = [0.1] * 384
    mock_get_embedder.return_value = mock_embedder

    mock_db = Mock()
    mock_db.search.return_value = [
        {
            "score": 0.9,
            "text": "result from lib1",
            "library": "lib1",
            "source_url": "https://test1.com",
            "chunk_index": 0
        },
        {
            "score": 0.8,
            "text": "result from lib2",
            "library": "lib2",
            "source_url": "https://test2.com",
            "chunk_index": 0
        }
    ]
    mock_get_db.return_value = mock_db

    result = search_all_docs("test query", limit=5)

    assert len(result) == 2
    assert result[0]["library"] == "lib1"
    assert result[1]["library"] == "lib2"
