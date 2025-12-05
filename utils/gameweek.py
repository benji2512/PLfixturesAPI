"""Gameweek utilities for Premier League fixtures."""

import logging
from typing import Optional, List
from datetime import datetime

from dateutil import parser as date_parser

from .fpl_api import get_client, FPLAPIError
from .models import Fixture, Gameweek, MatchResult, Team

logger = logging.getLogger(__name__)


def get_current_gameweek_number() -> Optional[int]:
    """
    Get the current gameweek number.
    
    Returns:
        Current gameweek number or None if no current gameweek
    """
    client = get_client()
    current_gw = client.get_current_gameweek()
    if current_gw:
        return current_gw.id
    return None


def get_gameweek_fixtures(gameweek: int) -> List[Fixture]:
    """
    Get all fixtures for a specific gameweek.
    
    Args:
        gameweek: Gameweek number
        
    Returns:
        List of fixtures for the gameweek
    """
    client = get_client()
    return client.get_fixtures(gameweek=gameweek)


def get_all_gameweeks() -> List[Gameweek]:
    """
    Get all gameweeks for the current season.
    
    Returns:
        List of all gameweeks
    """
    client = get_client()
    return client.get_gameweeks()


def get_fixtures_for_gameweek(gameweek: int) -> List[MatchResult]:
    """
    Get formatted fixtures for a specific gameweek.
    
    Args:
        gameweek: Gameweek number
        
    Returns:
        List of formatted match results
    """
    client = get_client()
    fixtures = client.get_fixtures(gameweek=gameweek)
    teams = {team.id: team for team in client.get_teams()}
    
    results = []
    for fixture in fixtures:
        home_team = teams.get(fixture.team_h)
        away_team = teams.get(fixture.team_a)
        
        if not home_team or not away_team:
            logger.warning(f"Could not find team info for fixture {fixture.id}")
            continue
        
        kickoff_time = None
        if fixture.kickoff_time:
            try:
                # FPL API returns ISO format with 'Z' suffix
                kickoff_time = date_parser.parse(fixture.kickoff_time.replace('Z', '+00:00'))
            except Exception as e:
                logger.warning(f"Could not parse kickoff time {fixture.kickoff_time}: {e}")
        
        result = MatchResult(
            home_team=home_team.name,
            away_team=away_team.name,
            home_score=fixture.team_h_score,
            away_score=fixture.team_a_score,
            kickoff_time=kickoff_time,
            gameweek=fixture.event,
            finished=fixture.finished,
            venue="home"
        )
        results.append(result)
    
    return results


def print_gameweek_fixtures(gameweek: int) -> None:
    """
    Print fixtures for a specific gameweek.
    
    Args:
        gameweek: Gameweek number
    """
    fixtures = get_fixtures_for_gameweek(gameweek)
    print(f"\nGameweek {gameweek} Fixtures:\n")
    print("=" * 60)
    for fixture in fixtures:
        print(fixture)
        print("-" * 60)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    current_gw = get_current_gameweek_number()
    if current_gw:
        print(f"Current gameweek: {current_gw}")
        print_gameweek_fixtures(current_gw)
    else:
        print("No current gameweek found")

