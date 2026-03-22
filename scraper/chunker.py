"""Document chunking with token-based splitting."""

import re
from typing import List, Dict, Any
import tiktoken


class DocumentChunker:
    """Chunk documents into overlapping segments."""

    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        """
        Initialize chunker.

        Args:
            chunk_size: Target chunk size in tokens
            overlap: Overlap between chunks in tokens
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def chunk_text(self, text: str, source_url: str) -> List[Dict[str, Any]]:
        """
        Chunk text into overlapping segments, preserving code blocks.

        Args:
            text: Text to chunk
            source_url: Source URL for metadata

        Returns:
            List of chunks with text and metadata
        """
        # Split into code blocks and text blocks
        blocks = self._split_preserve_code_blocks(text)

        chunks = []
        current_chunk = []
        current_tokens = 0

        for block in blocks:
            block_tokens = len(self.encoding.encode(block))

            # If single block exceeds chunk_size, split it
            if block_tokens > self.chunk_size:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append("".join(current_chunk))
                    current_chunk = []
                    current_tokens = 0

                # Split large block
                sub_chunks = self._split_large_block(block)
                chunks.extend(sub_chunks)
            else:
                # Check if adding this block exceeds chunk_size
                if current_tokens + block_tokens > self.chunk_size:
                    # Save current chunk
                    chunks.append("".join(current_chunk))

                    # Start new chunk with overlap
                    overlap_text = self._get_overlap_text(current_chunk)
                    current_chunk = [overlap_text, block]
                    current_tokens = len(self.encoding.encode("".join(current_chunk)))
                else:
                    # Add block to current chunk
                    current_chunk.append(block)
                    current_tokens += block_tokens

        # Add final chunk
        if current_chunk:
            chunks.append("".join(current_chunk))

        # Create chunk metadata
        total_chunks = len(chunks)
        result = []
        for idx, chunk_text in enumerate(chunks):
            result.append({
                "text": chunk_text.strip(),
                "metadata": {
                    "source_url": source_url,
                    "chunk_index": idx,
                    "total_chunks": total_chunks,
                },
            })

        return result

    def _split_preserve_code_blocks(self, text: str) -> List[str]:
        """Split text while preserving code blocks intact."""
        # Pattern to match code blocks (``` or indented)
        code_block_pattern = r"(```[\s\S]*?```)"

        parts = re.split(code_block_pattern, text)

        # Filter empty strings
        return [part for part in parts if part.strip()]

    def _split_large_block(self, block: str) -> List[str]:
        """Split a large block that exceeds chunk_size."""
        tokens = self.encoding.encode(block)
        chunks = []

        start = 0
        while start < len(tokens):
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoding.decode(chunk_tokens)
            chunks.append(chunk_text)
            start = end - self.overlap

        return chunks

    def _get_overlap_text(self, current_chunk: List[str]) -> str:
        """Get overlap text from current chunk."""
        full_text = "".join(current_chunk)
        tokens = self.encoding.encode(full_text)

        if len(tokens) <= self.overlap:
            return full_text

        overlap_tokens = tokens[-self.overlap :]
        return self.encoding.decode(overlap_tokens)
