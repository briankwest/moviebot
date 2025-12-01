# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

MovieBot is a voice-enabled AI agent that provides movie information using the SignalWire AI Agents SDK and The Movie Database (TMDb) API.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the agent (default port 5000)
python app.py

# Test tools
swaig-test app.py --list-tools
swaig-test app.py --exec search_movie --query "Inception"
swaig-test app.py --dump-swml
```

## Environment Variables

Copy `env.example` to `.env` and configure:
- `TMDB_API_KEY`: TMDb API key (required)
- `HTTP_USERNAME` / `HTTP_PASSWORD`: Basic auth for SWAIG endpoints
- `PORT`: Server port (default 5000)

## Architecture

### Main Agent (`app.py`)

- `MovieBot` class extending `AgentBase` from `signalwire_agents`
- 12 SWAIG tools defined with `@AgentBase.tool` decorator
- Prompt configured via POM (`prompt_add_section()`)
- Voice configured with ElevenLabs TTS and function fillers
- Speech hints and pronunciation rules for movie terms

### TMDb API Module (`tmdb_api.py`)

- Central `tmdb_request(api_key, endpoint, params)` helper at line 13
- Typed wrapper functions for each API endpoint
- Handles None values and error responses
- API base URL: `https://api.themoviedb.org/3`

### SWAIG Tools

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `search_movie` | Search movies by title | `query`, `year` |
| `get_movie_details` | Get movie info | `movie_id` |
| `get_movie_credits` | Get cast/crew | `movie_id` |
| `get_movie_recommendations` | Get recommendations | `movie_id` |
| `get_similar_movies` | Get similar movies | `movie_id` |
| `get_trending_movies` | Get trending | `time_window` |
| `get_now_playing_movies` | In theaters now | `region` |
| `get_upcoming_movies` | Coming soon | `region` |
| `discover_movies` | Filter by criteria | `with_genres`, `primary_release_year`, `sort_by` |
| `get_genre_list` | Get genre IDs | - |
| `get_person_details` | Actor/director info | `person_id` |
| `multi_search` | Search all | `query` |

### Key Code Locations

- Agent initialization: `app.py:36-62`
- Prompt configuration: `app.py:64-102`
- Voice configuration: `app.py:104-115`
- SWAIG tools: `app.py:130-678`
- TMDb API helper: `tmdb_api.py:13-37`

## Adding New Tools

1. Add API function to `tmdb_api.py`:
```python
def new_function(api_key: str, param: str) -> Dict[str, Any]:
    return tmdb_request(api_key, "/endpoint", {"param": param})
```

2. Add tool to `MovieBot` class in `app.py`:
```python
@AgentBase.tool(
    name="new_function",
    description="Clear description for AI",
    parameters={
        "param": {"type": "string", "description": "What this does"}
    }
)
def new_function_tool(self, args, raw_data):
    result = new_function(self.tmdb_api_key, args.get("param"))
    return SwaigFunctionResult(format_result(result))
```

3. Import the function at the top of `app.py`

## Testing Changes

```bash
# Verify all tools are registered
swaig-test app.py --list-tools

# Test specific function
swaig-test app.py --exec new_function --param "value"
```
