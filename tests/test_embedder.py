"""Tests for document embedder."""

import pytest
from unittest.mock import Mock, patch
from scraper.embedder import DocumentEmbedder


@patch('scraper.embedder.TextEmbedding')
def test_embedder_initialization(mock_text_embedding):
    """Test embedder initialization."""
    embedder = DocumentEmbedder()
    mock_text_embedding.assert_called_once_with(model_name="BAAI/bge-small-en-v1.5")


@patch('scraper.embedder.TextEmbedding')
def test_embedder_custom_model(mock_text_embedding):
    """Test embedder with custom model."""
    embedder = DocumentEmbedder(model_name="custom-model")
    mock_text_embedding.assert_called_once_with(model_name="custom-model")


@patch('scraper.embedder.TextEmbedding')
def test_embed_chunks(mock_text_embedding):
    """Test embedding chunks."""
    # Mock the embedding model
    mock_model = Mock()
    # Create mock embeddings with tolist() method
    mock_embedding1 = Mock()
    mock_embedding1.tolist.return_value = [0.1] * 384
    mock_embedding2 = Mock()
    mock_embedding2.tolist.return_value = [0.2] * 384
    mock_model.embed.return_value = [mock_embedding1, mock_embedding2]
    mock_text_embedding.return_value = mock_model

    embedder = DocumentEmbedder()
    chunks = [
        {
            "text": "First chunk",
            "metadata": {"source_url": "test", "chunk_index": 0, "total_chunks": 2}
        },
        {
            "text": "Second chunk",
            "metadata": {"source_url": "test", "chunk_index": 1, "total_chunks": 2}
        }
    ]

    result = embedder.embed_chunks(chunks)

    assert len(result) == 2
    assert "embedding" in result[0]
    assert "embedding" in result[1]
    assert len(result[0]["embedding"]) == 384
    assert len(result[1]["embedding"]) == 384


@patch('scraper.embedder.TextEmbedding')
def test_embed_query(mock_text_embedding):
    """Test embedding a query."""
    # Mock the embedding model
    mock_model = Mock()
    mock_embedding = Mock()
    mock_embedding.tolist.return_value = [0.5] * 384
    mock_model.embed.return_value = [mock_embedding]
    mock_text_embedding.return_value = mock_model

    embedder = DocumentEmbedder()
    query = "test query"

    result = embedder.embed_query(query)

    assert len(result) == 384
    assert all(isinstance(x, float) for x in result)
