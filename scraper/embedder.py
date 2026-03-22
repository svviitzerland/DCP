"""Document embedding using Fastembed."""

from typing import List, Dict, Any
from fastembed import TextEmbedding


class DocumentEmbedder:
    """Embed document chunks using Fastembed."""

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        """
        Initialize embedder.

        Args:
            model_name: Fastembed model name (default: BAAI/bge-small-en-v1.5)
        """
        self.model = TextEmbedding(model_name=model_name)

    def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Embed document chunks.

        Args:
            chunks: List of chunks with text and metadata

        Returns:
            List of chunks with embeddings added
        """
        texts = [chunk["text"] for chunk in chunks]

        # Generate embeddings (returns generator)
        embeddings = list(self.model.embed(texts))

        # Add embeddings to chunks
        for chunk, embedding in zip(chunks, embeddings):
            chunk["embedding"] = embedding.tolist()

        return chunks

    def embed_query(self, query: str) -> List[float]:
        """
        Embed a search query.

        Args:
            query: Query text

        Returns:
            Query embedding vector
        """
        embeddings = list(self.model.embed([query]))
        return embeddings[0].tolist()
