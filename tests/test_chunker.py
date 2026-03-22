"""Tests for document chunker."""

import pytest
from scraper.chunker import DocumentChunker


def test_chunker_initialization():
    """Test chunker initialization with default parameters."""
    chunker = DocumentChunker()
    assert chunker.chunk_size == 512
    assert chunker.overlap == 50


def test_chunker_custom_parameters():
    """Test chunker initialization with custom parameters."""
    chunker = DocumentChunker(chunk_size=256, overlap=25)
    assert chunker.chunk_size == 256
    assert chunker.overlap == 25


def test_chunk_small_text():
    """Test chunking of small text that fits in one chunk."""
    chunker = DocumentChunker(chunk_size=512, overlap=50)
    text = "This is a small test document."
    source_url = "https://example.com"

    chunks = chunker.chunk_text(text, source_url)

    assert len(chunks) == 1
    assert chunks[0]["text"] == text
    assert chunks[0]["metadata"]["source_url"] == source_url
    assert chunks[0]["metadata"]["chunk_index"] == 0
    assert chunks[0]["metadata"]["total_chunks"] == 1


def test_chunk_preserves_code_blocks():
    """Test that code blocks are preserved during chunking."""
    chunker = DocumentChunker(chunk_size=100, overlap=10)
    text = """
Some text before code.

```python
def hello():
    print("Hello, World!")
```

Some text after code.
"""
    source_url = "https://example.com"

    chunks = chunker.chunk_text(text, source_url)

    # Check that code block is in one of the chunks
    code_found = any("```python" in chunk["text"] for chunk in chunks)
    assert code_found


def test_chunk_metadata():
    """Test that chunk metadata is correctly set."""
    chunker = DocumentChunker(chunk_size=50, overlap=10)
    # Create text with many words to ensure multiple chunks
    text = " ".join(["word"] * 200)  # This will definitely create multiple chunks
    source_url = "https://example.com/test"

    chunks = chunker.chunk_text(text, source_url)

    assert len(chunks) > 1

    for i, chunk in enumerate(chunks):
        assert chunk["metadata"]["chunk_index"] == i
        assert chunk["metadata"]["total_chunks"] == len(chunks)
        assert chunk["metadata"]["source_url"] == source_url
