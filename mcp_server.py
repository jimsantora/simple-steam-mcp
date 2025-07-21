#!/usr/bin/env python3
"""Steam Library MCP Server - Provides access to Steam game library data"""

import os
from typing import Annotated, Optional, List, Dict, Any
from datetime import datetime
import pandas as pd
from fastmcp import FastMCP

# Create the server instance
mcp = FastMCP("steam-library-mcp")

# Load the Steam library data at startup
# Use absolute path to ensure CSV is found regardless of working directory
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "steam_library.csv")
try:
    df = pd.read_csv(csv_path)
    # Convert playtime from minutes to hours
    df['playtime_forever_hours'] = df['playtime_forever'] / 60
    df['playtime_2weeks_hours'] = df['playtime_2weeks'] / 60
    # Handle "Never" dates
    df['rtime_last_played'] = pd.to_datetime(df['rtime_last_played'], errors='coerce')
    # Don't print to stdout as it interferes with STDIO protocol
    pass
except Exception as e:
    # Don't print to stdout as it interferes with STDIO protocol
    df = pd.DataFrame()  # Empty dataframe as fallback

@mcp.tool
def search_games(
    query: Annotated[str, "Search term to match against game name, genre, developer, or publisher"]
) -> List[Dict[str, Any]]:
    """Search for games by name, genre, developer, or publisher"""
    if df.empty:
        return []
    
    query_lower = query.lower()
    # Search across multiple fields
    mask = (
        df['name'].str.lower().str.contains(query_lower, na=False) |
        df['genres'].str.lower().str.contains(query_lower, na=False) |
        df['developers'].str.lower().str.contains(query_lower, na=False) |
        df['publishers'].str.lower().str.contains(query_lower, na=False)
    )
    
    results = df[mask][['appid', 'name', 'genres', 'review_summary', 'playtime_forever_hours']].to_dict('records')
    return results

@mcp.tool
def filter_games(
    playtime_min: Annotated[Optional[float], "Minimum playtime in hours"] = None,
    playtime_max: Annotated[Optional[float], "Maximum playtime in hours"] = None,
    review_summary: Annotated[Optional[str], "Review summary to filter by (e.g., 'Very Positive', 'Overwhelmingly Positive')"] = None,
    maturity_rating: Annotated[Optional[str], "Maturity rating to filter by (e.g., 'Everyone', 'Teen (13+)')"] = None
) -> List[Dict[str, Any]]:
    """Filter games by playtime, review summary, or maturity rating"""
    if df.empty:
        return []
    
    filtered = df.copy()
    
    if playtime_min is not None:
        filtered = filtered[filtered['playtime_forever_hours'] >= playtime_min]
    
    if playtime_max is not None:
        filtered = filtered[filtered['playtime_forever_hours'] <= playtime_max]
    
    if review_summary:
        filtered = filtered[filtered['review_summary'].str.lower() == review_summary.lower()]
    
    if maturity_rating:
        filtered = filtered[filtered['maturity_rating'].str.lower() == maturity_rating.lower()]
    
    results = filtered[['appid', 'name', 'genres', 'review_summary', 'playtime_forever_hours']].to_dict('records')
    return results

@mcp.tool
def get_game_details(
    game_identifier: Annotated[str, "Game name or appid to get details for"]
) -> Optional[Dict[str, Any]]:
    """Get comprehensive details about a specific game"""
    if df.empty:
        return None
    
    # Try to match by appid first (if it's a number)
    try:
        appid = int(game_identifier)
        game = df[df['appid'] == appid]
    except ValueError:
        # Otherwise search by name (case-insensitive)
        game = df[df['name'].str.lower() == game_identifier.lower()]
    
    if game.empty:
        # Try partial match on name
        game = df[df['name'].str.lower().str.contains(game_identifier.lower(), na=False)]
    
    if game.empty:
        return None
    
    # Return the first match
    result = game.iloc[0].to_dict()
    # Add the hours fields
    result['playtime_forever_hours'] = result['playtime_forever'] / 60
    result['playtime_2weeks_hours'] = result['playtime_2weeks'] / 60
    return result

@mcp.tool
def get_game_reviews(
    game_identifier: Annotated[str, "Game name or appid to get review data for"]
) -> Optional[Dict[str, Any]]:
    """Get detailed review statistics for a game"""
    game = get_game_details(game_identifier)
    if not game:
        return None
    
    return {
        'name': game['name'],
        'appid': game['appid'],
        'review_summary': game['review_summary'],
        'review_score': game['review_score'],
        'total_reviews': game['total_reviews'],
        'positive_reviews': game['positive_reviews'],
        'negative_reviews': game['negative_reviews'],
        'positive_percentage': (game['positive_reviews'] / game['total_reviews'] * 100) if game['total_reviews'] > 0 else 0
    }

@mcp.tool
def get_library_stats() -> Dict[str, Any]:
    """Get overview statistics about the entire game library"""
    if df.empty:
        return {
            'total_games': 0,
            'total_hours_played': 0,
            'average_hours_per_game': 0,
            'top_genres': {},
            'top_developers': {},
            'review_distribution': {}
        }
    
    # Basic stats
    total_games = len(df)
    total_hours = df['playtime_forever_hours'].sum()
    avg_hours = total_hours / total_games if total_games > 0 else 0
    
    # Genre distribution (split comma-separated genres)
    genre_counts = {}
    for genres in df['genres'].dropna():
        for genre in genres.split(', '):
            genre = genre.strip()
            genre_counts[genre] = genre_counts.get(genre, 0) + 1
    top_genres = dict(sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:10])
    
    # Developer distribution
    dev_counts = df['developers'].value_counts().head(10).to_dict()
    
    # Review distribution
    review_dist = df['review_summary'].value_counts().to_dict()
    
    return {
        'total_games': total_games,
        'total_hours_played': round(total_hours, 2),
        'average_hours_per_game': round(avg_hours, 2),
        'top_genres': top_genres,
        'top_developers': dev_counts,
        'review_distribution': review_dist
    }

@mcp.tool
def get_recently_played() -> List[Dict[str, Any]]:
    """Get games played in the last 2 weeks"""
    if df.empty:
        return []
    
    recent = df[df['playtime_2weeks'] > 0].copy()
    recent = recent.sort_values('playtime_2weeks', ascending=False)
    
    results = recent[['appid', 'name', 'playtime_2weeks_hours', 'playtime_forever_hours', 'rtime_last_played']].to_dict('records')
    return results

@mcp.tool
def get_recommendations() -> List[Dict[str, Any]]:
    """Get personalized game recommendations based on playtime patterns"""
    if df.empty:
        return []
    
    recommendations = []
    
    # Get user's top genres by playtime
    played_games = df[df['playtime_forever'] > 0].copy()
    if played_games.empty:
        # If no games played, recommend highest rated games
        top_rated = df[df['review_summary'].isin(['Overwhelmingly Positive', 'Very Positive'])].head(5)
        for _, game in top_rated.iterrows():
            recommendations.append({
                'appid': game['appid'],
                'name': game['name'],
                'reason': f"Highly rated game ({game['review_summary']}) you haven't played yet"
            })
        return recommendations
    
    # Find favorite genres
    genre_playtime = {}
    for _, game in played_games.iterrows():
        if pd.notna(game['genres']):
            playtime = game['playtime_forever_hours']
            for genre in game['genres'].split(', '):
                genre = genre.strip()
                genre_playtime[genre] = genre_playtime.get(genre, 0) + playtime
    
    top_genres = sorted(genre_playtime.items(), key=lambda x: x[1], reverse=True)[:3]
    
    # Find unplayed games in favorite genres
    unplayed = df[df['playtime_forever'] == 0].copy()
    
    for genre, hours in top_genres:
        genre_games = unplayed[unplayed['genres'].str.contains(genre, na=False)]
        # Get highest rated games in this genre
        genre_games = genre_games[genre_games['review_summary'].isin(['Overwhelmingly Positive', 'Very Positive'])]
        
        for _, game in genre_games.head(2).iterrows():
            recommendations.append({
                'appid': game['appid'],
                'name': game['name'],
                'reason': f"Similar genre ({genre}) to games you've played {round(hours, 1)} hours"
            })
    
    # Find games from favorite developers
    top_devs = played_games.groupby('developers')['playtime_forever_hours'].sum().sort_values(ascending=False).head(3)
    
    for dev, hours in top_devs.items():
        dev_games = unplayed[unplayed['developers'] == dev]
        for _, game in dev_games.head(1).iterrows():
            recommendations.append({
                'appid': game['appid'],
                'name': game['name'],
                'reason': f"From {dev} who made games you've played {round(hours, 1)} hours"
            })
    
    # Remove duplicates
    seen = set()
    unique_recs = []
    for rec in recommendations:
        if rec['appid'] not in seen:
            seen.add(rec['appid'])
            unique_recs.append(rec)
    
    return unique_recs[:10]  # Limit to 10 recommendations

if __name__ == "__main__":
    mcp.run()