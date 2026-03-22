"""Documentation fetcher with priority chain."""

import json
import os
import sys
import argparse
from pathlib import Path
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from scraper.chunker import DocumentChunker
from scraper.embedder import DocumentEmbedder
from db.qdrant_client import QdrantDB


class DocumentFetcher:
    """Fetch documentation with priority chain."""

    MAX_CONTENT_SIZE = 500 * 1024  # 500KB max per library

    def __init__(self):
        self.client = httpx.Client(
            timeout=30.0,
            follow_redirects=True,
            headers={"User-Agent": "DCP-Bot/1.0 (Documentation Context Provider)"},
        )
        self.chunker = DocumentChunker(chunk_size=512, overlap=50)
        self.embedder = DocumentEmbedder()

    def fetch_library(self, library: str, config: Dict[str, Any]) -> Optional[str]:
        """
        Fetch documentation for a library using priority chain.

        Priority:
        1. llms_full_txt (most complete)
        2. llms_txt (AI-optimized)
        3. Crawl docs site (fallback)
        4. GitHub /docs folder (last resort)

        Args:
            library: Library name
            config: Library configuration from provider.json

        Returns:
            Documentation content or None if all methods fail
        """
        print(f"Fetching documentation for {library}...")

        # Try llms_full_txt first
        if config.get("llms_full_txt"):
            print(f"  Trying llms_full_txt: {config['llms_full_txt']}")
            content = self._fetch_url(config["llms_full_txt"])
            if content:
                print(f"  [OK] Successfully fetched from llms_full_txt")
                return content

        # Try llms_txt
        if config.get("llms_txt"):
            print(f"  Trying llms_txt: {config['llms_txt']}")
            content = self._fetch_url(config["llms_txt"])
            if content:
                print(f"  [OK] Successfully fetched from llms_txt")
                return content

        # Try crawling docs site
        if config.get("docs"):
            print(f"  Trying to crawl docs site: {config['docs']}")
            content = self._crawl_docs_site(config["docs"])
            if content:
                print(f"  [OK] Successfully crawled docs site")
                return content

        print(f"  [FAIL] Failed to fetch documentation for {library}")
        return None

    def _fetch_url(self, url: str) -> Optional[str]:
        """Fetch content from a URL."""
        try:
            response = self.client.get(url)
            response.raise_for_status()

            content = response.text

            # Check size limit
            if len(content.encode("utf-8")) > self.MAX_CONTENT_SIZE:
                print(f"    Warning: Content exceeds {self.MAX_CONTENT_SIZE} bytes, truncating")
                content = content[: self.MAX_CONTENT_SIZE]

            return content
        except Exception as e:
            print(f"    Error fetching {url}: {e}")
            return None

    def _crawl_docs_site(self, base_url: str) -> Optional[str]:
        """
        Crawl a documentation site and extract text content.

        Args:
            base_url: Base URL of docs site

        Returns:
            Combined text content from all pages
        """
        try:
            # Fetch the main page
            response = self.client.get(base_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove navigation, footer, header elements
            for element in soup.find_all(["nav", "footer", "header", "script", "style"]):
                element.decompose()

            # Extract main content
            main_content = soup.find("main") or soup.find("article") or soup.body

            if not main_content:
                return None

            # Get text content
            text = main_content.get_text(separator="\n", strip=True)

            # Clean up excessive whitespace
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            content = "\n".join(lines)

            # Check size limit
            if len(content.encode("utf-8")) > self.MAX_CONTENT_SIZE:
                print(f"    Warning: Content exceeds {self.MAX_CONTENT_SIZE} bytes, truncating")
                content = content[: self.MAX_CONTENT_SIZE]

            return content if content else None

        except Exception as e:
            print(f"    Error crawling {base_url}: {e}")
            return None

    def process_and_store(self, library: str, content: str, source_url: str, db: QdrantDB):
        """
        Process content and store in vector database.

        Args:
            library: Library name
            content: Documentation content
            source_url: Source URL
            db: Qdrant database client
        """
        print(f"Processing {library}...")

        # Chunk the content
        chunks = self.chunker.chunk_text(content, source_url)
        print(f"  Created {len(chunks)} chunks")

        # Embed the chunks
        chunks_with_embeddings = self.embedder.embed_chunks(chunks)
        print(f"  Generated embeddings")

        # Store in database
        db.upsert_chunks(library, chunks_with_embeddings)
        print(f"  [OK] Stored in Qdrant")

    def sync_library(self, library: str, config: Dict[str, Any], db: QdrantDB) -> bool:
        """
        Sync a single library to the database.

        Args:
            library: Library name
            config: Library configuration
            db: Qdrant database client

        Returns:
            True if successful, False otherwise
        """
        # Fetch documentation
        content = self.fetch_library(library, config)

        if not content:
            return False

        # Determine source URL
        source_url = (
            config.get("llms_full_txt")
            or config.get("llms_txt")
            or config.get("docs")
            or "unknown"
        )

        # Delete existing chunks for this library (idempotent)
        print(f"Removing old chunks for {library}...")
        db.delete_library(library)

        # Process and store
        self.process_and_store(library, content, source_url, db)

        return True

    def close(self):
        """Close HTTP client."""
        self.client.close()


def load_providers() -> Dict[str, Dict[str, Any]]:
    """Load provider configuration."""
    providers_path = Path(__file__).parent.parent / "providers" / "provider.json"

    with open(providers_path, "r") as f:
        return json.load(f)


def main():
    """CLI entry point for syncing documentation."""
    parser = argparse.ArgumentParser(description="Sync documentation to DCP")
    parser.add_argument(
        "--library",
        type=str,
        help="Sync a specific library (default: sync all)",
    )
    parser.add_argument(
        "--sync-all",
        action="store_true",
        help="Sync all libraries",
    )

    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Load providers
    providers = load_providers()

    # Initialize database
    db = QdrantDB()

    # Initialize fetcher
    fetcher = DocumentFetcher()

    try:
        if args.library:
            # Sync single library
            if args.library not in providers:
                print(f"Error: Library '{args.library}' not found in provider.json")
                sys.exit(1)

            config = providers[args.library]
            success = fetcher.sync_library(args.library, config, db)

            if success:
                print(f"\n[OK] Successfully synced {args.library}")
            else:
                print(f"\n[FAIL] Failed to sync {args.library}")
                sys.exit(1)

        elif args.sync_all:
            # Sync all libraries
            total = len(providers)
            successful = 0
            failed = []

            for idx, (library, config) in enumerate(providers.items(), 1):
                print(f"\n[{idx}/{total}] Syncing {library}...")
                success = fetcher.sync_library(library, config, db)

                if success:
                    successful += 1
                else:
                    failed.append(library)

            print(f"\n{'='*60}")
            print(f"Sync complete: {successful}/{total} successful")
            if failed:
                print(f"Failed libraries: {', '.join(failed)}")

        else:
            parser.print_help()
            sys.exit(1)

    finally:
        fetcher.close()


if __name__ == "__main__":
    main()
