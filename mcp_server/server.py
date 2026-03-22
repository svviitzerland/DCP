"""FastMCP server for DCP - Main entry point."""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from db.qdrant_client import QdrantDB
from scraper.embedder import DocumentEmbedder

# Load environment variables
load_dotenv()

# Initialize FastMCP server with HTTP support
mcp = FastMCP(
    "DCP - Docs Context Provider",
    host=os.getenv("HOST", "0.0.0.0"),
    port=int(os.getenv("PORT", "8000")),
    sse_path="/mcp"
)

# Initialize database and embedder (lazy loading)
_db = None
_embedder = None


def get_db() -> QdrantDB:
    """Get or initialize database client."""
    global _db
    if _db is None:
        _db = QdrantDB()
    return _db


def get_embedder() -> DocumentEmbedder:
    """Get or initialize embedder."""
    global _embedder
    if _embedder is None:
        _embedder = DocumentEmbedder()
    return _embedder


def load_providers() -> Dict[str, Dict[str, Any]]:
    """Load provider configuration."""
    providers_path = Path(__file__).parent.parent / "providers" / "provider.json"
    with open(providers_path, "r") as f:
        return json.load(f)


@mcp.tool()
def list_libraries() -> List[Dict[str, str]]:
    """
    List all available libraries in DCP with their descriptions.

    Returns a list of libraries with their metadata from provider.json.
    """
    providers = load_providers()

    return [
        {
            "name": name,
            "description": config.get("description", "No description available"),
            "version": config.get("version", "unknown"),
            "docs_url": config.get("docs", ""),
        }
        for name, config in providers.items()
    ]


@mcp.tool()
def get_docs(library: str) -> str:
    """
    Get full documentation content for a specific library.

    Args:
        library: Name of the library (e.g., "agno", "supabase")

    Returns:
        Full concatenated documentation text for the library.
        Returns error message if library not found.
    """
    db = get_db()

    # Check if library exists in provider.json
    providers = load_providers()
    if library not in providers:
        available = ", ".join(providers.keys())
        return f"Error: Library '{library}' not found. Available libraries: {available}"

    # Retrieve all chunks for the library
    chunks = db.get_all_chunks(library)

    if not chunks:
        return f"Error: No documentation found for '{library}'. The library may not be synced yet."

    # Concatenate all chunks in order
    full_text = "\n\n".join(chunk["text"] for chunk in chunks)

    return full_text


@mcp.tool()
def search_docs(library: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Semantic search within a specific library's documentation.

    Args:
        library: Name of the library to search within
        query: Search query text
        limit: Maximum number of results to return (default: 5)

    Returns:
        List of relevant documentation chunks with scores and metadata.
    """
    db = get_db()
    embedder = get_embedder()

    # Check if library exists
    providers = load_providers()
    if library not in providers:
        available = ", ".join(providers.keys())
        return [
            {
                "error": f"Library '{library}' not found. Available libraries: {available}"
            }
        ]

    # Embed the query
    query_vector = embedder.embed_query(query)

    # Search in Qdrant
    results = db.search(query_vector=query_vector, library=library, limit=limit)

    if not results:
        return [{"message": f"No results found for query '{query}' in library '{library}'"}]

    return results


@mcp.tool()
def search_all_docs(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Semantic search across ALL libraries in DCP.

    Args:
        query: Search query text
        limit: Maximum number of results to return (default: 5)

    Returns:
        List of relevant documentation chunks from all libraries with scores and metadata.
    """
    db = get_db()
    embedder = get_embedder()

    # Embed the query
    query_vector = embedder.embed_query(query)

    # Search without library filter
    results = db.search(query_vector=query_vector, library=None, limit=limit)

    if not results:
        return [{"message": f"No results found for query '{query}'"}]

    return results


def main():
    """Run the MCP server."""
    # Run in SSE mode for HTTP server (App Runner compatible)
    transport = os.getenv("MCP_TRANSPORT", "sse")
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
