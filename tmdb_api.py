"""
TMDB API module for MovieBot.

This module provides functions to interact with The Movie Database (TMDB) API.
"""

import requests
from typing import Dict, Any, Optional

# TMDB API base URL
TMDB_API_BASE_URL = "https://api.themoviedb.org/3"


def tmdb_request(api_key: str, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Make a request to the TMDB API.

    Args:
        api_key: The TMDB API key
        endpoint: The API endpoint to call
        params: Additional parameters for the request

    Returns:
        JSON response as dictionary
    """
    url = f"{TMDB_API_BASE_URL}{endpoint}"

    # Prepare request parameters
    request_params = params.copy() if params else {}
    request_params["api_key"] = api_key

    # Remove None values
    request_params = {k: v for k, v in request_params.items() if v is not None}

    try:
        response = requests.get(url, params=request_params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"TMDB API request failed: {e}")
        return {"error": str(e)}


def search_movie(
    api_key: str,
    query: str,
    language: str = "en-US",
    page: int = 1,
    include_adult: bool = False,
    region: Optional[str] = None,
    year: Optional[int] = None,
    primary_release_year: Optional[int] = None
) -> Dict[str, Any]:
    """
    Search for movies by title.

    Args:
        api_key: TMDB API key
        query: Movie title to search for
        language: Language for results
        page: Page number for pagination
        include_adult: Whether to include adult content
        region: Region to prioritize search results
        year: Filter results by release year
        primary_release_year: Filter results by primary release year

    Returns:
        Dictionary containing search results
    """
    endpoint = "/search/movie"
    params = {
        "query": query,
        "language": language,
        "page": page,
        "include_adult": include_adult,
        "region": region,
        "year": year,
        "primary_release_year": primary_release_year
    }
    return tmdb_request(api_key, endpoint, params)


def get_movie_details(api_key: str, movie_id: int, language: str = "en-US") -> Dict[str, Any]:
    """
    Get detailed information about a specific movie.

    Args:
        api_key: TMDB API key
        movie_id: TMDB movie ID
        language: Language for results

    Returns:
        Dictionary containing movie details
    """
    endpoint = f"/movie/{movie_id}"
    params = {"language": language}
    return tmdb_request(api_key, endpoint, params)


def discover_movies(
    api_key: str,
    language: str = "en-US",
    region: Optional[str] = None,
    sort_by: str = "popularity.desc",
    include_adult: bool = False,
    include_video: bool = False,
    page: int = 1,
    primary_release_year: Optional[int] = None,
    primary_release_date_gte: Optional[str] = None,
    primary_release_date_lte: Optional[str] = None,
    with_genres: Optional[str] = None,
    with_cast: Optional[str] = None,
    with_crew: Optional[str] = None,
    with_keywords: Optional[str] = None,
    with_runtime_gte: Optional[int] = None,
    with_runtime_lte: Optional[int] = None
) -> Dict[str, Any]:
    """
    Discover movies based on different criteria.

    Args:
        api_key: TMDB API key
        language: Language for results
        region: Region to filter release dates
        sort_by: Sort method
        include_adult: Whether to include adult content
        include_video: Whether to include movies with videos
        page: Page number for pagination
        primary_release_year: Filter by release year
        primary_release_date_gte: Filter by release date (>=)
        primary_release_date_lte: Filter by release date (<=)
        with_genres: Comma-separated list of genre IDs
        with_cast: Comma-separated list of person IDs for cast
        with_crew: Comma-separated list of person IDs for crew
        with_keywords: Comma-separated list of keyword IDs
        with_runtime_gte: Minimum runtime in minutes
        with_runtime_lte: Maximum runtime in minutes

    Returns:
        Dictionary containing discovered movies
    """
    endpoint = "/discover/movie"
    params = {
        "language": language,
        "region": region,
        "sort_by": sort_by,
        "include_adult": include_adult,
        "include_video": include_video,
        "page": page,
        "primary_release_year": primary_release_year,
        "primary_release_date.gte": primary_release_date_gte,
        "primary_release_date.lte": primary_release_date_lte,
        "with_genres": with_genres,
        "with_cast": with_cast,
        "with_crew": with_crew,
        "with_keywords": with_keywords,
        "with_runtime.gte": with_runtime_gte,
        "with_runtime.lte": with_runtime_lte
    }
    return tmdb_request(api_key, endpoint, params)


def get_trending_movies(api_key: str, time_window: str = "week", language: str = "en-US") -> Dict[str, Any]:
    """
    Get a list of trending movies.

    Args:
        api_key: TMDB API key
        time_window: Time window for trending calculation (day or week)
        language: Language for results

    Returns:
        Dictionary containing trending movies
    """
    endpoint = f"/trending/movie/{time_window}"
    params = {"language": language}
    return tmdb_request(api_key, endpoint, params)


def get_movie_recommendations(api_key: str, movie_id: int, language: str = "en-US") -> Dict[str, Any]:
    """
    Get movie recommendations based on a specific movie.

    Args:
        api_key: TMDB API key
        movie_id: TMDB movie ID
        language: Language for results

    Returns:
        Dictionary containing recommended movies
    """
    endpoint = f"/movie/{movie_id}/recommendations"
    params = {"language": language}
    return tmdb_request(api_key, endpoint, params)


def get_movie_credits(api_key: str, movie_id: int, language: str = "en-US") -> Dict[str, Any]:
    """
    Get cast and crew information for a movie.

    Args:
        api_key: TMDB API key
        movie_id: TMDB movie ID
        language: Language for results

    Returns:
        Dictionary containing movie credits
    """
    endpoint = f"/movie/{movie_id}/credits"
    params = {"language": language}
    return tmdb_request(api_key, endpoint, params)


def get_person_details(
    api_key: str,
    person_id: int,
    language: str = "en-US",
    append_to_response: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get detailed information about a person.

    Args:
        api_key: TMDB API key
        person_id: TMDB person ID
        language: Language for results
        append_to_response: Additional data to append (e.g., "movie_credits")

    Returns:
        Dictionary containing person details
    """
    endpoint = f"/person/{person_id}"
    params = {
        "language": language,
        "append_to_response": append_to_response or "movie_credits"
    }
    return tmdb_request(api_key, endpoint, params)


def get_genre_list(api_key: str, language: str = "en-US") -> Dict[str, Any]:
    """
    Get the list of official genres.

    Args:
        api_key: TMDB API key
        language: Language for results

    Returns:
        Dictionary containing genre list
    """
    endpoint = "/genre/movie/list"
    params = {"language": language}
    return tmdb_request(api_key, endpoint, params)


def get_upcoming_movies(api_key: str, language: str = "en-US", region: Optional[str] = None) -> Dict[str, Any]:
    """
    Get a list of upcoming movies.

    Args:
        api_key: TMDB API key
        language: Language for results
        region: Region code (ISO 3166-1)

    Returns:
        Dictionary containing upcoming movies
    """
    endpoint = "/movie/upcoming"
    params = {
        "language": language,
        "region": region
    }
    return tmdb_request(api_key, endpoint, params)


def get_now_playing_movies(api_key: str, language: str = "en-US", region: Optional[str] = None) -> Dict[str, Any]:
    """
    Get a list of movies currently in theaters.

    Args:
        api_key: TMDB API key
        language: Language for results
        region: Region code (ISO 3166-1)

    Returns:
        Dictionary containing now playing movies
    """
    endpoint = "/movie/now_playing"
    params = {
        "language": language,
        "region": region
    }
    return tmdb_request(api_key, endpoint, params)


def get_similar_movies(api_key: str, movie_id: int, language: str = "en-US") -> Dict[str, Any]:
    """
    Get a list of similar movies.

    Args:
        api_key: TMDB API key
        movie_id: TMDB movie ID
        language: Language for results

    Returns:
        Dictionary containing similar movies
    """
    endpoint = f"/movie/{movie_id}/similar"
    params = {"language": language}
    return tmdb_request(api_key, endpoint, params)


def multi_search(
    api_key: str,
    query: str,
    language: str = "en-US",
    page: int = 1,
    include_adult: bool = False,
    region: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search for movies, TV shows, and people.

    Args:
        api_key: TMDB API key
        query: Search query
        language: Language for results
        page: Page number for pagination
        include_adult: Whether to include adult content
        region: Region to prioritize search results

    Returns:
        Dictionary containing search results
    """
    endpoint = "/search/multi"
    params = {
        "query": query,
        "language": language,
        "page": page,
        "include_adult": include_adult,
        "region": region
    }
    return tmdb_request(api_key, endpoint, params)
