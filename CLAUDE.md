# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Steam Library MCP (Model Context Protocol) server that provides access to Steam game library data through Claude Desktop. The project is built using FastMCP, a Pythonic framework for building MCP servers.

## Key Commands

### Running the Server
```bash
# Install dependencies
pip install -r requirements.txt

# Run the MCP server (for testing)
python mcp_server.py

# Run the Steam library data fetcher
python steam_library_fetcher.py
```

### Development Commands
This is a Python project without traditional build/test/lint commands. Key development tasks:
- Ensure all dependencies are installed via `pip install -r requirements.txt`
- Test the server by running `python mcp_server.py`
- The server runs on `http://0.0.0.0:8000/sse` by default

## Architecture & Structure

### Core Components

1. **mcp_server.py**: Main MCP server implementation using FastMCP
   - Currently a simple example server with basic tools (hello_world, add_numbers, get_current_time)
   - Entry point for the MCP server when integrated with Claude Desktop

2. **steam_library_fetcher.py**: Steam API data fetcher
   - Fetches detailed game information from Steam API
   - Requires `STEAM_ID` and `STEAM_API_KEY` environment variables
   - Outputs data to `steam_library.csv`

3. **steam_library.csv**: Data source for the MCP server
   - Contains columns: appid, name, maturity_rating, review_summary, review_score, total_reviews, positive_reviews, negative_reviews, genres, categories, developers, publishers, release_date, playtime_forever, playtime_2weeks, rtime_last_played

### MCP Server Integration

The server needs to be configured in Claude Desktop's configuration file:
- **macOS/Linux**: `~/.config/claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\claude\claude_desktop_config.json`

### Available MCP Tools (as described in README)

The server should implement these tools for Steam library interaction:
1. `search_games`: Search by name, genre, developer, publisher, review summary, or maturity rating
2. `filter_games`: Filter by playtime thresholds, review summary, or maturity rating
3. `get_game_details`: Get comprehensive info about a specific game
4. `get_game_reviews`: Get detailed review statistics
5. `get_library_stats`: Overview statistics of the library
6. `get_recently_played`: Games played in the last 2 weeks
7. `get_recommendations`: Personalized suggestions based on playtime

## Important Notes

- The current `mcp_server.py` is a minimal example and needs to be extended with the Steam library functionality
- Data processing should use pandas for efficient CSV handling
- The server uses FastMCP framework with FastAPI for web transport and SSE
- Environment variables for Steam API access should be stored in a `.env` file