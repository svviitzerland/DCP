"""Tests for Qdrant client."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from db.qdrant_client import QdrantDB


@patch('db.qdrant_client.QdrantClient')
def test_qdrant_initialization(mock_qdrant_client):
    """Test QdrantDB initialization."""
    mock_client = Mock()
    mock_client.get_collections.return_value = Mock(collections=[])
    mock_qdrant_client.return_value = mock_client

    db = QdrantDB(url="https://test.qdrant.io", api_key="test_key")

    assert db.url == "https://test.qdrant.io"
    assert db.api_key == "test_key"
    assert db.collection_name == "dcp_docs"


@patch('db.qdrant_client.QdrantClient')
def test_ensure_collection_creates_if_not_exists(mock_qdrant_client):
    """Test that collection is created if it doesn't exist."""
    mock_client = Mock()
    mock_client.get_collections.return_value = Mock(collections=[])
    mock_qdrant_client.return_value = mock_client

    db = QdrantDB(url="https://test.qdrant.io", api_key="test_key")

    mock_client.create_collection.assert_called_once()


@patch('db.qdrant_client.QdrantClient')
def test_upsert_chunks(mock_qdrant_client, sample_chunks):
    """Test upserting chunks to Qdrant."""
    mock_client = Mock()
    mock_client.get_collections.return_value = Mock(collections=[])
    mock_qdrant_client.return_value = mock_client

    db = QdrantDB(url="https://test.qdrant.io", api_key="test_key")
    db.upsert_chunks("test-library", sample_chunks)

    mock_client.upsert.assert_called_once()
    call_args = mock_client.upsert.call_args
    assert call_args.kwargs["collection_name"] == "dcp_docs"
    assert len(call_args.kwargs["points"]) == 2


@patch('db.qdrant_client.QdrantClient')
def test_search_with_library_filter(mock_qdrant_client):
    """Test searching with library filter."""
    mock_client = Mock()
    mock_client.get_collections.return_value = Mock(collections=[])
    mock_result = Mock()
    mock_result.score = 0.9
    mock_result.payload = {
        "text": "test text",
        "library": "test-library",
        "source_url": "https://test.com",
        "chunk_index": 0
    }
    mock_client.query_points.return_value = Mock(points=[mock_result])
    mock_qdrant_client.return_value = mock_client

    db = QdrantDB(url="https://test.qdrant.io", api_key="test_key")
    results = db.search(query_vector=[0.1] * 384, library="test-library", limit=5)

    assert len(results) == 1
    assert results[0]["score"] == 0.9
    assert results[0]["library"] == "test-library"


@patch('db.qdrant_client.QdrantClient')
def test_get_all_chunks(mock_qdrant_client):
    """Test retrieving all chunks for a library."""
    mock_client = Mock()
    mock_client.get_collections.return_value = Mock(collections=[])

    mock_point1 = Mock()
    mock_point1.payload = {
        "text": "chunk 1",
        "chunk_index": 0,
        "source_url": "https://test.com"
    }
    mock_point2 = Mock()
    mock_point2.payload = {
        "text": "chunk 2",
        "chunk_index": 1,
        "source_url": "https://test.com"
    }

    mock_client.scroll.return_value = ([mock_point1, mock_point2], None)
    mock_qdrant_client.return_value = mock_client

    db = QdrantDB(url="https://test.qdrant.io", api_key="test_key")
    chunks = db.get_all_chunks("test-library")

    assert len(chunks) == 2
    assert chunks[0]["chunk_index"] == 0
    assert chunks[1]["chunk_index"] == 1


@patch('db.qdrant_client.QdrantClient')
def test_delete_library(mock_qdrant_client):
    """Test deleting all chunks for a library."""
    mock_client = Mock()
    mock_client.get_collections.return_value = Mock(collections=[])
    mock_qdrant_client.return_value = mock_client

    db = QdrantDB(url="https://test.qdrant.io", api_key="test_key")
    db.delete_library("test-library")

    mock_client.delete.assert_called_once()
