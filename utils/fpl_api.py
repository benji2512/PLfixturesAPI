"""Fantasy Premier League API client."""

import logging
import time
from typing import Optional, Dict, List, Any
from datetime import datetime

import requests
from dateutil import parser as date_parser

from .models import Team, Fixture, Gameweek

logger = logging.getLogger(__name__)

# FPL API base URL
FPL_BASE_URL = "https://fantasy.premierleague.com/api"

# Cache for API responses (simple in-memory cache)
_cache: Dict[str, tuple[Any, float]] = {}
_cache_ttl = 300  # 5 minutes cache TTL


class FPLAPIError(Exception):
    """Custom exception for FPL API errors."""
    pass


class FPLAPIClient:
    """Client for interacting with the Fantasy Premier League API."""
    
    def __init__(self, base_url: str = FPL_BASE_URL, cache_ttl: int = 300):
        """
        Initialize the FPL API client.
        
        Args:
            base_url: Base URL for the FPL API
            cache_ttl: Cache time-to-live in seconds
        """
        self.base_url = base_url
        self.cache_ttl = cache_ttl
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PLFixturesAPI/1.0'
        })
    
    def _get_cached(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key in _cache:
            value, timestamp = _cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return value
            else:
                del _cache[key]
        return None
    
    def _set_cache(self, key: str, value: Any) -> None:
        """Set value in cache."""
        _cache[key] = (value, time.time())
    
    def _make_request(self, endpoint: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Make a request to the FPL API with error handling and caching.
        
        Args:
            endpoint: API endpoint (relative to base URL)
            use_cache: Whether to use cached response if available
            
        Returns:
            JSON response as dictionary
            
        Raises:
            FPLAPIError: If the request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        cache_key = url
        
        # Check cache first
        if use_cache:
            cached_response = self._get_cached(cache_key)
            if cached_response is not None:
                logger.debug(f"Cache hit for {url}")
                return cached_response
        
        try:
            logger.debug(f"Making request to {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Cache the response
            if use_cache:
                self._set_cache(cache_key, data)
            
            return data
        
        except requests.exceptions.Timeout:
            raise FPLAPIError(f"Request to {url} timed out")
        except requests.exceptions.HTTPError as e:
            raise FPLAPIError(f"HTTP error {e.response.status_code} for {url}: {e}")
        except requests.exceptions.RequestException as e:
            raise FPLAPIError(f"Request failed for {url}: {e}")
        except ValueError as e:
            raise FPLAPIError(f"Invalid JSON response from {url}: {e}")
    
    def get_bootstrap_static(self) -> Dict[str, Any]:
        """
        Get bootstrap static data (teams, gameweeks, etc.).
        
        Returns:
            Dictionary containing teams, events (gameweeks), and other static data
        """
        return self._make_request("bootstrap-static/")
    
    def get_teams(self) -> List[Team]:
        """
        Get all Premier League teams.
        
        Returns:
            List of Team models
        """
        bootstrap = self.get_bootstrap_static()
        teams_data = bootstrap.get("teams", [])
        return [Team.model_validate(team) for team in teams_data]
    
    def get_team_by_id(self, team_id: int) -> Optional[Team]:
        """
        Get a team by its ID.
        
        Args:
            team_id: Team ID
            
        Returns:
            Team model or None if not found
        """
        teams = self.get_teams()
        for team in teams:
            if team.id == team_id:
                return team
        return None
    
    def _word_matches(self, word1: str, word2: str) -> bool:
        """
        Check if two words match (handles abbreviations and prefixes).
        
        Examples:
        - "man" matches "manchester" (prefix)
        - "manchester" matches "man" (contains)
        - "utd" matches "united" (abbreviation)
        - "united" matches "utd" (contains)
        - "nott'm" matches "nottingham" (abbreviation with apostrophe)
        - "nottm" matches "nottingham" (abbreviation)
        """
        if word1 == word2:
            return True
        
        # Remove apostrophes and compare
        word1_clean = word1.replace("'", "").replace("'", "")
        word2_clean = word2.replace("'", "").replace("'", "")
        if word1_clean == word2_clean:
            return True
        
        # Check substring match
        if word1 in word2 or word2 in word1:
            return True
        
        # Check cleaned substring match (handles apostrophes)
        if word1_clean in word2_clean or word2_clean in word1_clean:
            return True
        
        # Check prefix match
        if word1.startswith(word2) or word2.startswith(word1):
            return True
        
        # Check cleaned prefix match
        if word1_clean.startswith(word2_clean) or word2_clean.startswith(word1_clean):
            return True
        
        # Handle common abbreviation patterns
        # "nott'm" or "nottm" should match "nottingham"
        # "man" should match "manchester"
        # "utd" should match "united"
        # "city" should match "city"
        
        # Check if one word is a significant prefix of the other (at least 3 chars)
        min_len = min(len(word1_clean), len(word2_clean))
        if min_len >= 3:
            if word1_clean.startswith(word2_clean[:3]) or word2_clean.startswith(word1_clean[:3]):
                return True
        
        return False
    
    def _words_match(self, words1: set[str], words2: set[str]) -> bool:
        """
        Check if words from two sets match each other.
        
        Returns True if every word in words1 has a matching word in words2,
        or if every word in words2 has a matching word in words1.
        """
        # Check if all words1 match words in words2
        all_match_1_to_2 = all(
            any(self._word_matches(w1, w2) for w2 in words2)
            for w1 in words1
        )
        
        # Check if all words2 match words in words1
        all_match_2_to_1 = all(
            any(self._word_matches(w2, w1) for w1 in words1)
            for w2 in words2
        )
        
        return all_match_1_to_2 or all_match_2_to_1
    
    def get_team_by_name(self, team_name: str) -> Optional[Team]:
        """
        Get a team by its name (case-insensitive, supports partial and word matching).
        
        Handles both full names and abbreviations bidirectionally:
        - "Manchester United" matches both "Manchester United" and "Man Utd"
        - "Man Utd" matches both "Manchester United" and "Man Utd"
        
        Args:
            team_name: Team name to search for (e.g., "Manchester United", "Man Utd", "Man United")
            
        Returns:
            Team model or None if not found
        """
        teams = self.get_teams()
        team_name_lower = team_name.lower().strip()
        team_name_words = set(team_name_lower.split())
        
        # First, try exact match (case-insensitive) on both full and short names
        for team in teams:
            if team.name.lower() == team_name_lower or team.short_name.lower() == team_name_lower:
                return team
        
        # Second, try substring match in both directions
        # Check if search term is substring of team name (full or short)
        for team in teams:
            if team_name_lower in team.name.lower() or team_name_lower in team.short_name.lower():
                return team
        
        # Check if team name (full or short) is substring of search term
        for team in teams:
            if team.name.lower() in team_name_lower or team.short_name.lower() in team_name_lower:
                return team
        
        # Third, try word-based matching with abbreviation handling
        for team in teams:
            team_name_full = team.name.lower()
            team_short = team.short_name.lower()
            team_full_words = set(team_name_full.split())
            team_short_words = set(team_short.split())
            
            # Check if search words match team full name words
            if self._words_match(team_name_words, team_full_words):
                return team
            
            # Check if search words match team short name words
            if self._words_match(team_name_words, team_short_words):
                return team
            
            # Also check if combining full and short name words helps
            # (e.g., "Man" from short name + "City" from full name)
            all_team_words = team_full_words | team_short_words
            if self._words_match(team_name_words, all_team_words):
                return team
        
        return None
    
    def get_gameweeks(self) -> List[Gameweek]:
        """
        Get all gameweeks for the current season.
        
        Returns:
            List of Gameweek models
        """
        bootstrap = self.get_bootstrap_static()
        events_data = bootstrap.get("events", [])
        return [Gameweek.model_validate(event) for event in events_data]
    
    def get_current_gameweek(self) -> Optional[Gameweek]:
        """
        Get the current gameweek.
        
        Returns:
            Current Gameweek model or None if no current gameweek
        """
        gameweeks = self.get_gameweeks()
        for gw in gameweeks:
            if gw.is_current:
                return gw
        return None
    
    def get_fixtures(self, gameweek: Optional[int] = None) -> List[Fixture]:
        """
        Get all fixtures or fixtures for a specific gameweek.
        
        Args:
            gameweek: Optional gameweek number. If None, returns all fixtures.
            
        Returns:
            List of Fixture models
        """
        endpoint = "fixtures/"
        if gameweek is not None:
            endpoint = f"fixtures/?event={gameweek}"
        
        fixtures_data = self._make_request(endpoint)
        # fixtures_data is a list of dictionaries from the API
        if not isinstance(fixtures_data, list):
            raise FPLAPIError(f"Expected list of fixtures, got {type(fixtures_data)}")
        return [Fixture.model_validate(fixture) for fixture in fixtures_data]
    
    def get_fixtures_for_team(self, team_id: int) -> List[Fixture]:
        """
        Get all fixtures for a specific team.
        
        Args:
            team_id: Team ID
            
        Returns:
            List of Fixture models for the team
        """
        all_fixtures = self.get_fixtures()
        return [
            fixture for fixture in all_fixtures
            if fixture.team_h == team_id or fixture.team_a == team_id
        ]
    
    def get_fixtures_for_team_by_name(self, team_name: str) -> List[Fixture]:
        """
        Get all fixtures for a team by name.
        
        Args:
            team_name: Team name
            
        Returns:
            List of Fixture models for the team
            
        Raises:
            FPLAPIError: If team is not found
        """
        team = self.get_team_by_name(team_name)
        if team is None:
            # Get list of available teams for better error message
            teams = self.get_teams()
            team_names = [t.name for t in teams]
            raise FPLAPIError(
                f"Team '{team_name}' not found. Available teams: {', '.join(sorted(team_names))}"
            )
        return self.get_fixtures_for_team(team.id)


# Global client instance
_client: Optional[FPLAPIClient] = None


def get_client() -> FPLAPIClient:
    """Get or create the global FPL API client instance."""
    global _client
    if _client is None:
        _client = FPLAPIClient()
    return _client


def list_all_teams() -> List[Team]:
    """
    Get a list of all available teams.
    
    Returns:
        List of all Team models
    """
    client = get_client()
    return client.get_teams()

