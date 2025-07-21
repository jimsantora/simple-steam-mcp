# Steam Library MCP Server

A Model Context Protocol (MCP) server that provides access to your Steam game library data through Claude Desktop.

## Features

- **Search Games**: Find games by name, genre, developer, publisher, review summary, or maturity rating
- **Filter Games**: Filter by playtime, review summary, or maturity rating  
- **Game Details**: Get comprehensive information about specific games
- **Review Analysis**: Detailed review statistics for games
- **Library Statistics**: Overview of your entire game library
- **Recently Played**: See what you've been playing lately
- **Recommendations**: Get game suggestions based on your playtime patterns

## Example Interactions using Claude Desktop (Click the dropdowns to see responses)

<details>
<summary>Suggest games based on recent play history<br><img src="images/recent_games_question.png" style="cursor:pointer;" /></summary>
<br>
<img src="images/recent_games_answer.png" />
</details>

<details>
<summary>Suggest games based on review scores and age ratings<br><img src="images/game_suggestion_question.png" style="cursor:pointer;" /></summary>
<br>
<img src="images/game_suggestion_answer.png" />
</details>

<details>
<summary>Generate a calendar timeline following several rules of games to share over time<br><img src="images/game_sharing_calendar_question.png" style="cursor:pointer;" /></summary>
<br>
<img src="images/game_sharing_calendar_answer.png" />
</details>

## Prerequisites

- Python 3.8 or higher
- A Steam account with a public game library
- Steam API key (get one from https://steamcommunity.com/dev/apikey)
- Your Steam ID

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Fetch Your Steam Library Data

First, create a `.env` file with your Steam credentials:

```bash
# .env
STEAM_ID=your_steam_id_here
STEAM_API_KEY=your_steam_api_key_here
```

Then run the data fetcher:

```bash
python steam_library_fetcher.py
```

This will create a `steam_library.csv` file with all your game data.

### 3. Configure Claude Desktop

Copy the example configuration file and update the paths:

```bash
cp claude_desktop_config.example.json claude_desktop_config.json
```

Edit `claude_desktop_config.json` and update the paths to match your system:

```json
{
  "mcpServers": {
    "Steam Library": {
      "command": "/path/to/your/python",
      "args": ["/path/to/your/steam-mcp/mcp_server.py"],
      "env": {}
    }
  }
}
```

Then copy it to Claude Desktop's configuration location:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux**: `~/.config/claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\claude\claude_desktop_config.json`

### 4. Test the Server

You can test the server directly:

```bash
python mcp_server.py
```

### 5. Restart Claude Desktop

After updating the configuration file, restart Claude Desktop to load the MCP server.

## Usage Examples

Once configured, you can ask Claude Desktop questions like:

- "What are my top 10 most played games?"
- "Show me all my puzzle games" 
- "Find games with 'Very Positive' reviews that I haven't played yet"
- "What are some good games I should try based on what I've played?"
- "Show me details for Half-Life 2"
- "What games have I played recently?"
- "Give me statistics about my Steam library"

## Available Tools

1. **search_games**: Search by name, genre, developer, publisher, review summary, or maturity rating
2. **filter_games**: Filter by playtime thresholds, review summary, or maturity rating
3. **get_game_details**: Get comprehensive info about a specific game
4. **get_game_reviews**: Get detailed review statistics
5. **get_library_stats**: Overview statistics of your library
6. **get_recently_played**: Games played in the last 2 weeks
7. **get_recommendations**: Personalized suggestions based on your playtime

## Data Source

The server reads from `steam_library.csv` which should contain columns:
- appid, name, maturity_rating, review_summary, review_score, total_reviews
- positive_reviews, negative_reviews, genres, categories, developers, publishers
- release_date, playtime_forever, playtime_2weeks, rtime_last_played

## Troubleshooting

1. **Server not connecting**: Check that the path in your Claude Desktop config is correct
2. **CSV not found**: Ensure `steam_library.csv` is in the same directory as the server script
3. **Permission errors**: Make sure Python has read access to the CSV file
4. **Port conflicts**: The server uses port 8000 by default - ensure it's available

## Technical Details

- Built using the official MCP Python SDK
- Uses FastAPI for web transport with SSE (Server-Sent Events)
- Pandas for efficient CSV data processing
- Runs on all network interfaces (0.0.0.0) for flexibility