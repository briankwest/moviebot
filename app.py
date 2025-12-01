#!/usr/bin/env python3
"""
MovieBot - An AI agent that provides movie information using TMDB API.

This agent uses the SignalWire AI Agents SDK to provide real-time movie data
via The Movie Database (TMDB) API.
"""

import os
from dotenv import load_dotenv

from signalwire_agents import AgentBase
from signalwire_agents.core.function_result import SwaigFunctionResult

from tmdb_api import (
    search_movie, get_movie_details, discover_movies, get_trending_movies,
    get_movie_recommendations, get_movie_credits, get_person_details,
    get_genre_list, get_upcoming_movies, get_now_playing_movies,
    get_similar_movies, multi_search
)

load_dotenv()


class MovieBot(AgentBase):
    """
    AI Agent specialized in providing movie information using TMDB API.

    Features:
    - Movie search and detailed information
    - Trending and upcoming movie recommendations
    - Actor and director information
    - Genre-based movie discovery
    """

    def __init__(self):
        """Initialize the MovieBot agent."""
        super().__init__(
            name="moviebot",
            route="/swaig",
            host="0.0.0.0",
            port=int(os.getenv("PORT", 5000)),
            basic_auth=(os.getenv("SWML_BASIC_AUTH_USER"), os.getenv("SWML_BASIC_AUTH_PASSWORD"))
        )

        # Store API key for use in tools
        self.tmdb_api_key = os.getenv("TMDB_API_KEY")

        # Configure agent personality and behavior
        self._configure_prompt()

        # Configure voice and language
        self._configure_voice()

        # Add hints for movie-related terms
        self._add_hints()

        # Set AI parameters
        self.set_params({
            "end_of_speech_timeout": 1000,
            "attention_timeout": 10000
        })

    def _configure_prompt(self):
        """Configure the agent's prompt using POM."""

        self.prompt_add_section(
            "Personality",
            body="You are MovieBot, a friendly and knowledgeable movie expert. You're passionate about films "
                 "and love to discuss all aspects of cinema including plots, actors, directors, genres, "
                 "and making recommendations based on user preferences."
        )

        self.prompt_add_section(
            "Goal",
            body="Help users discover movies, learn about films they're interested in, and find "
                 "recommendations based on their tastes. Provide accurate and up-to-date information "
                 "about movies, actors, directors, and current releases."
        )

        self.prompt_add_section(
            "Instructions",
            bullets=[
                "Always use the available tools to get accurate and current movie information",
                "When a user asks about a movie, search for it and provide details",
                "For specific actors or directors, look up their filmography and information",
                "When recommending movies, ask about user preferences first (genres, actors, etc.)",
                "If a user mentions a movie but you're not sure which one, use search to clarify",
                "Provide concise but informative responses that focus on the user's question",
                "If information is not available or unclear, be honest about limitations",
                "When listing movies, include the year of release for clarity",
                "For trending or popular movie requests, use get_trending_movies",
                "For current movies in theaters, use get_now_playing_movies"
            ]
        )

        self.prompt_add_section(
            "Knowledge",
            body="You have access to The Movie Database (TMDB) API through various tools. These tools "
                 "allow you to search for movies, get details about specific films, find similar movies, "
                 "get information about actors and directors, and discover trending or upcoming releases."
        )

    def _configure_voice(self):
        """Configure voice and language settings."""
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

    def _add_hints(self):
        """Add hints for common movie-related terms."""
        self.add_hints([
            "TMDB", "MCU", "Marvel", "DC", "Oscar", "Academy Award",
            "Hollywood", "Bollywood", "Netflix", "HBO", "Disney Plus",
            "Spielberg", "Tarantino", "Nolan", "Scorsese"
        ])

        # Add pronunciation rules for common abbreviations
        self.add_pronunciation("MCU", "M C U", ignore_case=True)
        self.add_pronunciation("TMDB", "T M D B", ignore_case=True)
        self.add_pronunciation("IMDB", "I M D B", ignore_case=True)

    # -------------------------------------------------------------------------
    # SWAIG Tool Functions
    # -------------------------------------------------------------------------

    @AgentBase.tool(
        name="search_movie",
        description="Search for movies by title",
        parameters={
            "query": {
                "type": "string",
                "description": "The movie title to search for"
            },
            "language": {
                "type": "string",
                "description": "Language of the results",
                "default": "en-US"
            },
            "year": {
                "type": "integer",
                "description": "Filter results by release year"
            },
            "primary_release_year": {
                "type": "integer",
                "description": "Filter results by primary release year"
            }
        }
    )
    def search_movie_tool(self, args, raw_data):
        """Search for movies by title."""
        query = args.get("query", "")
        language = args.get("language", "en-US")
        year = args.get("year")
        primary_release_year = args.get("primary_release_year")

        result = search_movie(
            self.tmdb_api_key, query, language,
            year=year, primary_release_year=primary_release_year
        )

        if "error" in result:
            return SwaigFunctionResult(f"Error searching for movies: {result['error']}")

        if not result.get("results"):
            return SwaigFunctionResult(f"No movies found for '{query}'.")

        formatted = "Search results for movies:\n"
        for movie in result.get("results", [])[:5]:
            title = movie.get("title", "Unknown")
            year = movie.get("release_date", "")[:4] if movie.get("release_date") else "N/A"
            movie_id = movie.get("id", "")
            genre_ids = movie.get("genre_ids", [])
            formatted += f"id: {movie_id} title: {title} release_date: {year} genre_ids: {', '.join(map(str, genre_ids))}\n"

        return SwaigFunctionResult(formatted)

    @AgentBase.tool(
        name="get_movie_details",
        description="Retrieve detailed information about a movie",
        parameters={
            "movie_id": {
                "type": "integer",
                "description": "The TMDB ID of the movie"
            },
            "language": {
                "type": "string",
                "description": "Language of the results",
                "default": "en-US"
            }
        }
    )
    def get_movie_details_tool(self, args, raw_data):
        """Get detailed information about a specific movie."""
        movie_id = args.get("movie_id")
        language = args.get("language", "en-US")

        if not movie_id:
            return SwaigFunctionResult("Error: Movie ID is required.")

        result = get_movie_details(self.tmdb_api_key, movie_id, language)

        if "error" in result or "id" not in result:
            return SwaigFunctionResult(f"No details found for movie ID {movie_id}.")

        genres = ', '.join(genre['name'] for genre in result.get('genres', []))
        production_companies = ', '.join(company['name'] for company in result.get('production_companies', []))
        spoken_languages = ', '.join(lang['name'] for lang in result.get('spoken_languages', []))

        formatted = (
            f"Movie details:\n"
            f"id: {result['id']}\n"
            f"title: {result['title']}\n"
            f"original_title: {result.get('original_title', 'N/A')}\n"
            f"release_date: {result.get('release_date', 'N/A')}\n"
            f"runtime: {result.get('runtime', 'N/A')} minutes\n"
            f"overview: {result.get('overview', 'N/A')}\n"
            f"vote_average: {result.get('vote_average', 'N/A')}\n"
            f"vote_count: {result.get('vote_count', 'N/A')}\n"
            f"popularity: {result.get('popularity', 'N/A')}\n"
            f"genres: {genres}\n"
            f"original_language: {result.get('original_language', 'N/A')}\n"
            f"spoken_languages: {spoken_languages}\n"
            f"production_companies: {production_companies}\n"
            f"budget: ${result.get('budget', 0)}\n"
            f"revenue: ${result.get('revenue', 0)}\n"
            f"status: {result.get('status', 'N/A')}\n"
            f"tagline: {result.get('tagline', 'N/A')}"
        )

        return SwaigFunctionResult(formatted)

    @AgentBase.tool(
        name="get_movie_recommendations",
        description="Get recommendations based on a specific movie",
        parameters={
            "movie_id": {
                "type": "integer",
                "description": "The TMDB ID of the movie"
            },
            "language": {
                "type": "string",
                "description": "Language of the results",
                "default": "en-US"
            }
        }
    )
    def get_movie_recommendations_tool(self, args, raw_data):
        """Get movie recommendations based on a specific movie."""
        movie_id = args.get("movie_id")
        language = args.get("language", "en-US")

        if not movie_id:
            return SwaigFunctionResult("Error: Movie ID is required.")

        result = get_movie_recommendations(self.tmdb_api_key, movie_id, language)

        if "error" in result:
            return SwaigFunctionResult(f"Error getting recommendations: {result['error']}")

        if not result.get("results"):
            return SwaigFunctionResult(f"No recommendations found for movie ID {movie_id}.")

        formatted = "Recommended movies:\n"
        for movie in result.get("results", [])[:5]:
            title = movie.get("title", "Unknown")
            year = movie.get("release_date", "")[:4] if movie.get("release_date") else "N/A"
            movie_id = movie.get("id", "")
            genre_ids = movie.get("genre_ids", [])
            formatted += f"id: {movie_id} title: {title} release_date: {year} genre_ids: {', '.join(map(str, genre_ids))}\n"

        return SwaigFunctionResult(formatted)

    @AgentBase.tool(
        name="get_trending_movies",
        description="Retrieve a list of movies that are currently trending",
        parameters={
            "time_window": {
                "type": "string",
                "description": "Time window for trending (day or week)",
                "default": "week"
            },
            "language": {
                "type": "string",
                "description": "Language of the results",
                "default": "en-US"
            }
        }
    )
    def get_trending_movies_tool(self, args, raw_data):
        """Get currently trending movies."""
        time_window = args.get("time_window", "week")
        language = args.get("language", "en-US")

        result = get_trending_movies(self.tmdb_api_key, time_window, language)

        if "error" in result:
            return SwaigFunctionResult(f"Error getting trending movies: {result['error']}")

        if not result.get("results"):
            return SwaigFunctionResult("No trending movies found.")

        formatted = f"Trending movies for this {time_window}:\n"
        for movie in result.get("results", [])[:5]:
            title = movie.get("title", "Unknown")
            year = movie.get("release_date", "")[:4] if movie.get("release_date") else "N/A"
            movie_id = movie.get("id", "")
            genre_ids = movie.get("genre_ids", [])
            formatted += f"id: {movie_id} title: {title} release_date: {year} genre_ids: {', '.join(map(str, genre_ids))}\n"

        return SwaigFunctionResult(formatted)

    @AgentBase.tool(
        name="discover_movies",
        description="Discover movies by different criteria like genre, year, or sorting",
        parameters={
            "with_genres": {
                "type": "string",
                "description": "Comma-separated genre IDs to filter by"
            },
            "primary_release_year": {
                "type": "integer",
                "description": "Filter movies released in a specific year"
            },
            "sort_by": {
                "type": "string",
                "description": "Sort results by criteria (e.g., popularity.desc, vote_average.desc)",
                "default": "popularity.desc"
            },
            "language": {
                "type": "string",
                "description": "Language of the results",
                "default": "en-US"
            },
            "with_cast": {
                "type": "string",
                "description": "Comma-separated person IDs to filter by cast"
            },
            "with_crew": {
                "type": "string",
                "description": "Comma-separated person IDs to filter by crew"
            }
        }
    )
    def discover_movies_tool(self, args, raw_data):
        """Discover movies based on different criteria."""
        with_genres = args.get("with_genres")
        primary_release_year = args.get("primary_release_year")
        sort_by = args.get("sort_by", "popularity.desc")
        language = args.get("language", "en-US")
        with_cast = args.get("with_cast")
        with_crew = args.get("with_crew")

        result = discover_movies(
            self.tmdb_api_key,
            language=language,
            sort_by=sort_by,
            primary_release_year=primary_release_year,
            with_genres=with_genres,
            with_cast=with_cast,
            with_crew=with_crew
        )

        if "error" in result:
            return SwaigFunctionResult(f"Error discovering movies: {result['error']}")

        if not result.get("results"):
            return SwaigFunctionResult("No movies found matching the criteria.")

        formatted = "Discovered movies:\n"
        for movie in result.get("results", [])[:5]:
            title = movie.get("title", "Unknown")
            year = movie.get("release_date", "")[:4] if movie.get("release_date") else "N/A"
            movie_id = movie.get("id", "")
            genre_ids = movie.get("genre_ids", [])
            formatted += f"id: {movie_id} title: {title} release_date: {year} genre_ids: {', '.join(map(str, genre_ids))}\n"

        return SwaigFunctionResult(formatted)

    @AgentBase.tool(
        name="get_genre_list",
        description="Retrieve the list of official movie genres with their IDs",
        parameters={
            "language": {
                "type": "string",
                "description": "Language of the results",
                "default": "en-US"
            }
        }
    )
    def get_genre_list_tool(self, args, raw_data):
        """Get the list of official movie genres."""
        language = args.get("language", "en-US")

        result = get_genre_list(self.tmdb_api_key, language)

        if "error" in result:
            return SwaigFunctionResult(f"Error getting genre list: {result['error']}")

        if not result.get("genres"):
            return SwaigFunctionResult("No genre information available.")

        formatted = "Available movie genres:\n"
        for genre in result.get("genres", []):
            formatted += f"name: {genre['name']} id: {genre['id']}\n"

        return SwaigFunctionResult(formatted)

    @AgentBase.tool(
        name="get_upcoming_movies",
        description="Retrieve movies that are soon to be released",
        parameters={
            "language": {
                "type": "string",
                "description": "Language of the results",
                "default": "en-US"
            },
            "region": {
                "type": "string",
                "description": "Specify a region to filter release dates (e.g., US)"
            }
        }
    )
    def get_upcoming_movies_tool(self, args, raw_data):
        """Get movies that will be released soon."""
        language = args.get("language", "en-US")
        region = args.get("region")

        result = get_upcoming_movies(self.tmdb_api_key, language, region)

        if "error" in result:
            return SwaigFunctionResult(f"Error getting upcoming movies: {result['error']}")

        if not result.get("results"):
            return SwaigFunctionResult("No upcoming movie releases found.")

        formatted = "Upcoming movies:\n"
        for movie in result.get("results", [])[:10]:
            title = movie.get("title", "Unknown")
            release_date = movie.get("release_date", "N/A")
            movie_id = movie.get("id", "")
            genre_ids = movie.get("genre_ids", [])
            formatted += f"id: {movie_id} title: {title} release_date: {release_date} genre_ids: {', '.join(map(str, genre_ids))}\n"

        return SwaigFunctionResult(formatted)

    @AgentBase.tool(
        name="get_now_playing_movies",
        description="Retrieve movies currently playing in theaters",
        parameters={
            "language": {
                "type": "string",
                "description": "Language of the results",
                "default": "en-US"
            },
            "region": {
                "type": "string",
                "description": "Specify a region to filter release dates (e.g., US)"
            }
        }
    )
    def get_now_playing_movies_tool(self, args, raw_data):
        """Get movies that are currently in theaters."""
        language = args.get("language", "en-US")
        region = args.get("region")

        result = get_now_playing_movies(self.tmdb_api_key, language, region)

        if "error" in result:
            return SwaigFunctionResult(f"Error getting now playing movies: {result['error']}")

        if not result.get("results"):
            return SwaigFunctionResult("No movies currently playing in theaters found.")

        formatted = "Movies currently playing in theaters:\n"
        for movie in result.get("results", [])[:10]:
            title = movie.get("title", "Unknown")
            release_date = movie.get("release_date", "N/A")
            movie_id = movie.get("id", "")
            genre_ids = movie.get("genre_ids", [])
            formatted += f"id: {movie_id} title: {title} release_date: {release_date} genre_ids: {', '.join(map(str, genre_ids))}\n"

        return SwaigFunctionResult(formatted)

    @AgentBase.tool(
        name="get_similar_movies",
        description="Retrieve movies similar to a specified movie",
        parameters={
            "movie_id": {
                "type": "integer",
                "description": "The TMDB ID of the movie"
            },
            "language": {
                "type": "string",
                "description": "Language of the results",
                "default": "en-US"
            }
        }
    )
    def get_similar_movies_tool(self, args, raw_data):
        """Get movies similar to a specified movie."""
        movie_id = args.get("movie_id")
        language = args.get("language", "en-US")

        if not movie_id:
            return SwaigFunctionResult("Error: Movie ID is required.")

        result = get_similar_movies(self.tmdb_api_key, movie_id, language)

        if "error" in result:
            return SwaigFunctionResult(f"Error getting similar movies: {result['error']}")

        if not result.get("results"):
            return SwaigFunctionResult(f"No similar movies found for movie ID {movie_id}.")

        formatted = "Similar movies:\n"
        for movie in result.get("results", [])[:5]:
            title = movie.get("title", "Unknown")
            year = movie.get("release_date", "")[:4] if movie.get("release_date") else "N/A"
            mid = movie.get("id", "")
            genre_ids = movie.get("genre_ids", [])
            formatted += f"id: {mid} title: {title} release_date: {year} genre_ids: {', '.join(map(str, genre_ids))}\n"

        return SwaigFunctionResult(formatted)

    @AgentBase.tool(
        name="multi_search",
        description="Search for movies, TV shows, and people with a single query",
        parameters={
            "query": {
                "type": "string",
                "description": "The search query"
            },
            "language": {
                "type": "string",
                "description": "Language of the results",
                "default": "en-US"
            }
        }
    )
    def multi_search_tool(self, args, raw_data):
        """Search for movies, TV shows, and people."""
        query = args.get("query", "")
        language = args.get("language", "en-US")

        result = multi_search(self.tmdb_api_key, query, language)

        if "error" in result:
            return SwaigFunctionResult(f"Error in multi-search: {result['error']}")

        if not result.get("results"):
            return SwaigFunctionResult(f"No results found for '{query}'.")

        formatted = "Multi-search results:\n"
        for item in result.get("results", [])[:10]:
            media_type = item.get("media_type", "unknown")

            if media_type == "movie":
                title = item.get("title", "Unknown")
                year = item.get("release_date", "")[:4] if item.get("release_date") else "N/A"
                genre_ids = item.get("genre_ids", [])
                formatted += f"movie: id: {item['id']} title: {title} release_date: {year} genre_ids: {', '.join(map(str, genre_ids))}\n"

            elif media_type == "tv":
                name = item.get("name", "Unknown")
                year = item.get("first_air_date", "")[:4] if item.get("first_air_date") else "N/A"
                genre_ids = item.get("genre_ids", [])
                formatted += f"tv show: id: {item['id']} name: {name} first_air_date: {year} genre_ids: {', '.join(map(str, genre_ids))}\n"

            elif media_type == "person":
                name = item.get("name", "Unknown")
                known_for = item.get("known_for_department", "N/A")
                known_for_titles = ', '.join([
                    k.get('title', k.get('name', 'Unknown'))
                    for k in item.get('known_for', [])
                ])
                formatted += f"person: id: {item['id']} name: {name} known_for: {known_for_titles} department: {known_for}\n"

        return SwaigFunctionResult(formatted)

    @AgentBase.tool(
        name="get_movie_credits",
        description="Retrieve cast and crew information for a movie",
        parameters={
            "movie_id": {
                "type": "integer",
                "description": "The TMDB ID of the movie"
            },
            "language": {
                "type": "string",
                "description": "Language of the results",
                "default": "en-US"
            }
        }
    )
    def get_movie_credits_tool(self, args, raw_data):
        """Get cast and crew information for a movie."""
        movie_id = args.get("movie_id")
        language = args.get("language", "en-US")

        if not movie_id:
            return SwaigFunctionResult("Error: Movie ID is required.")

        result = get_movie_credits(self.tmdb_api_key, movie_id, language)

        if "error" in result:
            return SwaigFunctionResult(f"Error getting movie credits: {result['error']}")

        if "cast" not in result and "crew" not in result:
            return SwaigFunctionResult(f"No credits found for movie ID {movie_id}.")

        formatted = "Movie credits:\n"

        if "cast" in result:
            formatted += "cast:\n"
            for member in result["cast"][:10]:
                formatted += f"name: {member['name']} character: {member.get('character', 'N/A')}\n"

        if "crew" in result:
            formatted += "crew:\n"
            for member in result["crew"][:10]:
                formatted += f"name: {member['name']} department: {member.get('department', 'N/A')} job: {member.get('job', 'N/A')}\n"

        return SwaigFunctionResult(formatted)

    @AgentBase.tool(
        name="get_person_details",
        description="Retrieve detailed information about a person (actor, director)",
        parameters={
            "person_id": {
                "type": "integer",
                "description": "The TMDB ID of the person"
            },
            "language": {
                "type": "string",
                "description": "Language of the results",
                "default": "en-US"
            }
        }
    )
    def get_person_details_tool(self, args, raw_data):
        """Get detailed information about a person."""
        person_id = args.get("person_id")
        language = args.get("language", "en-US")

        if not person_id:
            return SwaigFunctionResult("Error: Person ID is required.")

        result = get_person_details(self.tmdb_api_key, person_id, language)

        if "error" in result or "id" not in result:
            return SwaigFunctionResult(f"No details found for person ID {person_id}.")

        # Get known_for from movie credits if available
        known_for_titles = []
        if "movie_credits" in result:
            cast = result["movie_credits"].get("cast", [])
            # Sort by popularity and get top 5
            sorted_cast = sorted(cast, key=lambda x: x.get("popularity", 0), reverse=True)[:5]
            known_for_titles = [m.get("title", "Unknown") for m in sorted_cast]

        formatted = (
            f"Person details:\n"
            f"name: {result.get('name', 'N/A')}\n"
            f"biography: {result.get('biography', 'N/A')}\n"
            f"birthday: {result.get('birthday', 'N/A')}\n"
            f"place_of_birth: {result.get('place_of_birth', 'N/A')}\n"
            f"known_for: {', '.join(known_for_titles) if known_for_titles else 'N/A'}"
        )

        return SwaigFunctionResult(formatted)


def main():
    """Run the MovieBot agent."""
    # Verify TMDB API key is set
    if not os.getenv("TMDB_API_KEY"):
        print("Error: TMDB_API_KEY environment variable is required.")
        print("Please set it with: export TMDB_API_KEY=your_api_key")
        return

    # Create and run the agent
    agent = MovieBot()

    # Print startup information
    print("Starting MovieBot Agent")
    print("----------------------------------------")
    print(f"URL: http://0.0.0.0:{os.getenv('PORT', 5000)}/swaig")
    print("----------------------------------------")
    print("Press Ctrl+C to stop the agent")

    agent.run()


if __name__ == "__main__":
    main()
