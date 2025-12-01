# MovieBot - AI Movie Expert Agent

A voice-enabled AI agent that provides detailed information about movies, directors, actors, genres, and personalized recommendations using the SignalWire AI Agents SDK and The Movie Database (TMDb) API.

## Features

- **Movie Search**: Find movies by title
- **Detailed Movie Information**: Get comprehensive details including plot, ratings, runtime, and budget
- **Movie Discovery**: Discover movies by genre, release year, and popularity
- **Trending Movies**: See what's currently popular
- **Recommendations**: Get movie recommendations based on films you like
- **Cast and Crew**: Access detailed cast and crew information
- **Person Details**: Look up actors and directors with their filmographies
- **Theater Listings**: Find movies currently playing or coming soon
- **Similar Movies**: Discover movies similar to ones you enjoy

## Architecture

The agent is built using:

- **SignalWire AI Agents SDK**: Provides the `AgentBase` framework for building voice AI agents with SWAIG (SignalWire AI Gateway) functions
- **TMDb API**: Supplies real-time movie data
- **ElevenLabs TTS**: Natural voice synthesis for responses

### Project Structure

```
moviebot/
├── app.py              # Main agent (MovieBot class extending AgentBase)
├── tmdb_api.py         # TMDb API module with typed functions
├── requirements.txt    # Python dependencies
├── env.example         # Environment variable template
└── prompt.md           # Reference prompt documentation
```

## Getting Started

### Prerequisites

- Python 3.8+
- TMDb API key ([get one here](https://www.themoviedb.org/settings/api))
- SignalWire account ([sign up](https://signalwire.com))

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/briankwest/moviebot.git
   cd moviebot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   cp env.example .env
   ```

   Edit `.env` and set:
   - `TMDB_API_KEY`: Your TMDb API key
   - `HTTP_USERNAME`: Basic auth username for SWAIG endpoints
   - `HTTP_PASSWORD`: Basic auth password for SWAIG endpoints
   - `PORT`: Server port (default: 5000)

### Running the Agent

```bash
python app.py
```

The agent will start on `http://0.0.0.0:5000/swaig`.

### Testing

Use `swaig-test` to verify the agent:

```bash
# List all available tools
swaig-test app.py --list-tools

# Test a specific function
swaig-test app.py --exec search_movie --query "Inception"

# Dump the generated SWML
swaig-test app.py --dump-swml
```

## SWAIG Functions

The agent provides 12 tools for movie information:

| Function | Description |
|----------|-------------|
| `search_movie` | Search for movies by title |
| `get_movie_details` | Get detailed information about a movie |
| `discover_movies` | Discover movies by genre, year, or sorting criteria |
| `get_trending_movies` | Get currently trending movies |
| `get_movie_recommendations` | Get recommendations based on a movie |
| `get_movie_credits` | Get cast and crew for a movie |
| `get_person_details` | Get information about an actor or director |
| `get_genre_list` | Get the list of movie genres with IDs |
| `get_upcoming_movies` | Get movies coming soon |
| `get_now_playing_movies` | Get movies currently in theaters |
| `get_similar_movies` | Get movies similar to a specified movie |
| `multi_search` | Search across movies, TV shows, and people |

## Deployment

### Using Dokku

1. **Create the app**:
   ```bash
   dokku apps:create moviebot
   ```

2. **Set environment variables**:
   ```bash
   dokku config:set moviebot TMDB_API_KEY=your_api_key
   dokku config:set moviebot HTTP_USERNAME=your_username
   dokku config:set moviebot HTTP_PASSWORD=your_password
   ```

3. **Deploy**:
   ```bash
   git remote add dokku dokku@your-server:moviebot
   git push dokku main
   ```

4. **Enable SSL** (optional):
   ```bash
   dokku letsencrypt:enable moviebot
   ```

### Using Docker

```bash
docker build -t moviebot .
docker run -p 5000:5000 \
  -e TMDB_API_KEY=your_api_key \
  -e HTTP_USERNAME=your_username \
  -e HTTP_PASSWORD=your_password \
  moviebot
```

## SignalWire Integration

To connect the agent to SignalWire:

1. Create an External SWML Handler pointing to your agent URL
2. Create a Subscriber with the handler
3. Assign a phone number or use WebRTC for browser-based access

See the [SignalWire AI documentation](https://signalwire.ai) for detailed setup instructions.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [SignalWire](https://signalwire.com) - AI Gateway and voice infrastructure
- [TMDb](https://www.themoviedb.org) - Movie database API
- [ElevenLabs](https://elevenlabs.io) - Text-to-speech synthesis
