"""Qdrant Cloud client for vector storage and retrieval."""

import os
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)


class QdrantDB:
    """Qdrant vector database client for DCP."""

    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        collection_name: str = "dcp_docs",
    ):
        self.url = url or os.getenv("QDRANT_URL")
        self.api_key = api_key or os.getenv("QDRANT_API_KEY")
        self.collection_name = collection_name or os.getenv("QDRANT_COLLECTION", "dcp_docs")

        if not self.url or not self.api_key:
            raise ValueError("QDRANT_URL and QDRANT_API_KEY must be set")

        self.client = QdrantClient(url=self.url, api_key=self.api_key)
        self._ensure_collection()

    def _ensure_collection(self):
        """Create collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]

        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )

    def upsert_chunks(self, library: str, chunks: List[Dict[str, Any]]):
        """
        Upsert document chunks for a library.

        Args:
            library: Library name
            chunks: List of dicts with keys: text, embedding, metadata
        """
        points = []
        for chunk in chunks:
            # Create deterministic ID from library + chunk_index
            # Use abs() and modulo to ensure unsigned 64-bit integer
            chunk_id = abs(hash(f"{library}_{chunk['metadata']['chunk_index']}")) % (2**63)

            point = PointStruct(
                id=chunk_id,
                vector=chunk["embedding"],
                payload={
                    "library": library,
                    "text": chunk["text"],
                    "source_url": chunk["metadata"]["source_url"],
                    "chunk_index": chunk["metadata"]["chunk_index"],
                    "total_chunks": chunk["metadata"]["total_chunks"],
                },
            )
            points.append(point)

        self.client.upsert(collection_name=self.collection_name, points=points)

    def search(
        self,
        query_vector: List[float],
        library: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks.

        Args:
            query_vector: Query embedding vector
            library: Optional library filter
            limit: Max results to return

        Returns:
            List of search results with score, text, and metadata
        """
        query_filter = None
        if library:
            query_filter = Filter(
                must=[FieldCondition(key="library", match=MatchValue(value=library))]
            )

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=query_filter,
            limit=limit,
        ).points

        return [
            {
                "score": result.score,
                "text": result.payload["text"],
                "library": result.payload["library"],
                "source_url": result.payload["source_url"],
                "chunk_index": result.payload["chunk_index"],
            }
            for result in results
        ]

    def get_all_chunks(self, library: str) -> List[Dict[str, Any]]:
        """
        Retrieve all chunks for a library, ordered by chunk_index.

        Args:
            library: Library name

        Returns:
            List of chunks with text and metadata
        """
        # Scroll through all points for the library
        results = []
        offset = None

        while True:
            response = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[FieldCondition(key="library", match=MatchValue(value=library))]
                ),
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False,
            )

            points, offset = response

            if not points:
                break

            for point in points:
                results.append({
                    "text": point.payload["text"],
                    "chunk_index": point.payload["chunk_index"],
                    "source_url": point.payload["source_url"],
                })

            if offset is None:
                break

        # Sort by chunk_index to maintain document order
        results.sort(key=lambda x: x["chunk_index"])
        return results

    def delete_library(self, library: str):
        """Delete all chunks for a library."""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[FieldCondition(key="library", match=MatchValue(value=library))]
            ),
        )

    def list_libraries(self) -> List[str]:
        """Get list of all libraries in the database."""
        # Scroll through all points and collect unique library names
        libraries = set()
        offset = None

        while True:
            response = self.client.scroll(
                collection_name=self.collection_name,
                limit=100,
                offset=offset,
                with_payload=["library"],
                with_vectors=False,
            )

            points, offset = response

            if not points:
                break

            for point in points:
                libraries.add(point.payload["library"])

            if offset is None:
                break

        return sorted(list(libraries))
