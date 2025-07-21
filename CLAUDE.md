# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a fully functional Steam Library MCP (Model Context Protocol) server that provides access to Steam game library data through Claude Desktop. The project is built using FastMCP and provides 7 tools for interacting with Steam library data.

## Key Commands

### Running the Server
```bash
# Install dependencies
pip install -r requirements.txt

# Run the MCP server (uses STDIO transport for Claude Desktop)
python mcp_server.py

# Fetch fresh Steam library data (requires .env with STEAM_ID and STEAM_API_KEY)
python steam_library_fetcher.py
```

### Configuration
```bash
# Create configuration from example
cp claude_desktop_config.example.json claude_desktop_config.json
# Edit paths in claude_desktop_config.json to match your system
# Copy to Claude Desktop location (macOS): ~/Library/Application Support/Claude/claude_desktop_config.json
```

## Architecture & Structure

### Core Components

1. **mcp_server.py**: Fully functional MCP server with 7 Steam library tools
   - Loads `steam_library.csv` at startup using pandas
   - Converts playtime from minutes to hours for readability
   - Uses STDIO transport (not HTTP) for Claude Desktop integration
   - **CRITICAL**: Never print to stdout during operation as it breaks STDIO protocol

2. **steam_library_fetcher.py**: Steam API data fetcher
   - Fetches comprehensive game data from Steam API
   - Requires `.env` file with `STEAM_ID` and `STEAM_API_KEY`
   - Outputs to `steam_library.csv`

3. **steam_library.csv**: Primary data source (not in git due to .gitignore)
   - 18 columns including playtime, reviews, genres, developers, publishers
   - Handles "Never" for rtime_last_played dates

### Implemented MCP Tools

1. **search_games**: Case-insensitive partial search across name, genres, developers, publishers
2. **filter_games**: Filter by playtime range, review summary, maturity rating
3. **get_game_details**: Get full game details by name or appid (supports partial matching)
4. **get_game_reviews**: Get review statistics including calculated positive percentage
5. **get_library_stats**: Structured dict with totals, top genres/developers, review distribution
6. **get_recently_played**: Games with playtime_2weeks > 0, sorted by recent playtime
7. **get_recommendations**: Personalized suggestions with reasons based on favorite genres/developers

### Configuration Files

- **claude_desktop_config.example.json**: Template for users to customize
- **claude_desktop_config.json**: Personal config (gitignored)
- **.env**: Steam API credentials (gitignored)

## Important Development Notes

- **STDIO Protocol**: Never use `print()` statements in mcp_server.py as they interfere with Claude Desktop communication
- **Data Loading**: CSV is loaded once at startup with absolute paths to avoid working directory issues
- **Error Handling**: Tools return empty lists/None for missing data rather than raising exceptions
- **Performance**: Data is cached in memory after CSV load for fast tool responses
- **Path Resolution**: Uses `os.path.abspath(__file__)` to find CSV regardless of working directory

## Claude Desktop Integration

- Server name: "steam-library-mcp"
- Transport: STDIO (not HTTP/SSE)
- Config location (macOS): `~/Library/Application Support/Claude/claude_desktop_config.json`
- Requires restart of Claude Desktop after config changes