# DCP (Docs Context Provider)

**A single MCP endpoint that serves documentation from multiple libraries to AI agents and IDEs.**

DCP is an open-source Model Context Protocol (MCP) server that provides instant access to up-to-date documentation for any registered library. When you use an AI agent with DCP configured, it can seamlessly query documentation for agno, strands, supabase, and any other library you add — all through one endpoint.

## Why DCP?

- **Single endpoint, multiple libraries**: No need to configure separate MCP servers for each library
- **Zero configuration**: Connect to the hosted service at dcp.farhanaulianda.my.id - no setup required
- **Easy to extend**: Add a new library by editing one JSON file
- **Semantic search**: Vector-based search powered by embeddings
- **IDE-agnostic**: Works with Cursor, Claude Code, Windsurf, and any MCP-compatible tool

## Features

- **Semantic search** across documentation using vector embeddings
- **Multi-library support** with a single configuration
- **AI-optimized** with support for llms.txt and llms-full.txt
- **Auto-sync** via GitHub Actions when libraries are added/updated
- **100% free** using open-source tools and free tiers

---

## Quick Start

DCP is hosted at **https://dcp.farhanaulianda.my.id** - no installation or configuration needed.

### Cursor

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "dcp": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-everything", "https://dcp.farhanaulianda.my.id"]
    }
  }
}
```

### Claude Code

Add to `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "dcp": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-everything", "https://dcp.farhanaulianda.my.id"]
    }
  }
}
```

### Windsurf

Add to `mcp_config.json`:

```json
{
  "mcpServers": {
    "dcp": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-everything", "https://dcp.farhanaulianda.my.id"]
    }
  }
}
```

That's it! Restart your IDE and start using DCP.

---

## MCP Tools

DCP exposes 4 tools to AI agents:

### `list_libraries()`
List all available libraries with descriptions.

```python
# Returns:
[
  {
    "name": "agno",
    "description": "AI agent framework by Agno",
    "version": "latest",
    "docs_url": "https://docs.agno.com"
  },
  ...
]
```

### `get_docs(library: str)`
Get full documentation for a specific library.

```python
get_docs("agno")
# Returns: Full concatenated documentation text
```

### `search_docs(library: str, query: str, limit: int = 5)`
Semantic search within a specific library.

```python
search_docs("supabase", "how to create a table", limit=3)
# Returns: Top 3 relevant chunks with scores
```

### `search_all_docs(query: str, limit: int = 5)`
Search across all libraries.

```python
search_all_docs("authentication", limit=5)
# Returns: Top 5 results from any library
```

---

## Contributing

We welcome contributions! Here's how you can help:

### Adding a New Library

Adding a new library is as simple as editing `providers/provider.json`:

```json
{
  "your-library": {
    "llms_txt": "https://your-library.com/llms.txt",
    "llms_full_txt": "https://your-library.com/llms-full.txt",
    "docs": "https://docs.your-library.com",
    "version": "latest",
    "description": "Your library description"
  }
}
```

**Priority chain** (DCP tries in this order):
1. `llms_full_txt` - Most complete AI-optimized documentation
2. `llms_txt` - Condensed AI-optimized documentation
3. `docs` - Crawls the documentation site

Set any field to `null` if not available.

**After editing `provider.json`:**
1. Fork the repository
2. Edit `providers/provider.json` to add your library
3. Submit a pull request
4. GitHub Actions will automatically sync the new library to the hosted service

### Development Setup

If you want to contribute code:

```bash
# Clone the repository
git clone https://github.com/svvitzerland/DCP.git
cd DCP

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Run tests
uv run pytest

# Format code
uv run black .

# Lint code
uv run ruff check .
```

### Reporting Issues

Found a bug or have a feature request? [Open an issue](https://github.com/svvitzerland/DCP/issues)

---

## Tech Stack

- **Language**: Python 3.11+
- **MCP Framework**: [FastMCP](https://github.com/jlowin/fastmcp)
- **Scraping**: httpx + BeautifulSoup4
- **Embedding**: [Fastembed](https://github.com/qdrant/fastembed) (BAAI/bge-small-en-v1.5, runs locally)
- **CI/CD**: GitHub Actions
- **Package Manager**: [uv](https://github.com/astral-sh/uv)

**Total cost: $0** (all free tiers)

---

## Roadmap

- [ ] Support for GitHub `/docs` folder fetching
- [ ] Web UI for browsing documentation
- [ ] Support for versioned documentation
- [ ] Incremental updates (only sync changed docs)
- [ ] Support for private documentation sources
- [ ] Docker image for easy deployment
- [ ] Metrics and analytics dashboard

---

## License

MIT License - see [LICENSE](LICENSE) file for details

---

## Acknowledgments

- [FastMCP](https://github.com/jlowin/fastmcp) for the MCP framework
- [Fastembed](https://github.com/qdrant/fastembed) for local embeddings
- All the library maintainers who provide llms.txt files

---

## Support

- [Documentation](https://github.com/svvitzerland/DCP/wiki)
- [Discussions](https://github.com/svvitzerland/DCP/discussions)
- [Issues](https://github.com/svvitzerland/DCP/issues)

---

**Made by the DCP community**
