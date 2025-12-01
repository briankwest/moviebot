# MovieBot Setup Guide

This guide covers the setup and configuration of the MovieBot AI agent.

## Requirements

- Python 3.8 or higher
- TMDb API key
- SignalWire account (for production deployment)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `signalwire-agents` - SignalWire AI Agents SDK
- `requests` - HTTP client for TMDb API
- `python-dotenv` - Environment variable management
- `Flask` - Web framework (for static file serving)

### 2. Configure Environment

Copy the example environment file:

```bash
cp env.example .env
```

Edit `.env` with your credentials:

```bash
TMDB_API_KEY=your_tmdb_api_key_here
SWML_BASIC_AUTH_USER=your_basic_auth_username
SWML_BASIC_AUTH_PASSWORD=your_basic_auth_password
PORT=5000
```

### 3. Run the Agent

```bash
python app.py
```

You should see:

```
Starting MovieBot Agent
----------------------------------------
URL: http://0.0.0.0:5000/swaig
----------------------------------------
Press Ctrl+C to stop the agent
```

## Testing

### List Available Tools

```bash
swaig-test app.py --list-tools
```

### Test a Function

```bash
swaig-test app.py --exec search_movie --query "The Matrix"
swaig-test app.py --exec get_trending_movies --time_window "week"
swaig-test app.py --exec get_genre_list
```

### View Generated SWML

```bash
swaig-test app.py --dump-swml
```

## Configuration Options

### Agent Configuration

The agent is configured in `app.py` via the `MovieBot` class constructor:

```python
super().__init__(
    name="moviebot",
    route="/swaig",
    host="0.0.0.0",
    port=int(os.getenv("PORT", 5000)),
    basic_auth=(os.getenv("SWML_BASIC_AUTH_USER"), os.getenv("SWML_BASIC_AUTH_PASSWORD"))
)
```

### Voice Configuration

The agent uses ElevenLabs for text-to-speech:

```python
self.add_language(
    name="English",
    code="en-US",
    voice="elevenlabs.josh",
    function_fillers=[
        "Let me search for that movie information...",
        "One moment while I look that up...",
        "Searching the movie database..."
    ]
)
```

To change the voice, modify the `voice` parameter. Available options include:
- `elevenlabs.josh`, `elevenlabs.rachel`
- `openai.alloy`, `openai.nova`
- `gcloud.en-US-Neural2-A`

### AI Parameters

Adjust speech detection and timeout settings:

```python
self.set_params({
    "end_of_speech_timeout": 1000,    # ms of silence to end turn
    "attention_timeout": 10000         # ms before "are you there?"
})
```

## Connecting to SignalWire

### 1. Create an External SWML Handler

In the SignalWire dashboard:
1. Go to **Voice** > **SWML Scripts**
2. Create a new **External SWML Handler**
3. Set the URL to your agent endpoint (e.g., `https://your-domain.com/swaig`)
4. Add basic auth credentials if configured

### 2. Create a Subscriber

1. Go to **Subscribers**
2. Create a new subscriber
3. Assign the SWML handler
4. Note the subscriber address (e.g., `/public/moviebot`)

### 3. Connect a Phone Number

1. Go to **Phone Numbers**
2. Assign a number to the subscriber
3. Calls to this number will now reach your agent

### 4. WebRTC (Browser-Based)

For browser-based voice interaction:
1. Create a Guest Token with the subscriber address
2. Use the SignalWire WebRTC SDK to connect

## Troubleshooting

### Agent Not Starting

- Verify `TMDB_API_KEY` is set in your environment
- Check that port 5000 (or your configured port) is available
- Ensure all dependencies are installed

### TMDb API Errors

- Verify your API key is valid at [TMDb](https://www.themoviedb.org/settings/api)
- Check API rate limits (TMDb allows ~40 requests/10 seconds)

### No Voice Output

- Ensure a language is configured with `add_language()`
- Verify the voice name is correct for your TTS provider

### Function Not Being Called

- Check the function description is clear enough for the AI
- Verify parameters match the expected types
- Test the function directly with `swaig-test`

## File Overview

| File | Purpose |
|------|---------|
| `app.py` | Main agent class with SWAIG tools |
| `tmdb_api.py` | TMDb API wrapper functions |
| `requirements.txt` | Python dependencies |
| `env.example` | Environment variable template |
| `Procfile` | Heroku/Dokku deployment config |
| `runtime.txt` | Python version specification |
