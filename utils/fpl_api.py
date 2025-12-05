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
    
    def get_team_by_name(self, team_name: str) -> Optional[Team]:
        """
        Get a team by its name (case-insensitive partial match).
        
        Args:
            team_name: Team name to search for
            
        Returns:
            Team model or None if not found
        """
        teams = self.get_teams()
        team_name_lower = team_name.lower()
        for team in teams:
            if team_name_lower in team.name.lower() or team_name_lower in team.short_name.lower():
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
            raise FPLAPIError(f"Team '{team_name}' not found")
        return self.get_fixtures_for_team(team.id)


# Global client instance
_client: Optional[FPLAPIClient] = None


def get_client() -> FPLAPIClient:
    """Get or create the global FPL API client instance."""
    global _client
    if _client is None:
        _client = FPLAPIClient()
    return _client

