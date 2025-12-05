"""Get full schedule of fixtures for a team."""

import logging
from typing import Optional
from datetime import datetime

from dateutil import parser as date_parser

from .fpl_api import get_client, FPLAPIError
from .models import MatchResult

logger = logging.getLogger(__name__)


def format_kickoff_time(kickoff_time: Optional[str]) -> str:
    """
    Format kickoff time as a readable string.
    
    Args:
        kickoff_time: ISO format datetime string or None
        
    Returns:
        Formatted time string
    """
    if kickoff_time is None:
        return "Game was cancelled and is to be rescheduled"
    
    try:
        # FPL API returns ISO format with 'Z' suffix
        dt = date_parser.parse(kickoff_time.replace('Z', '+00:00'))
        return f"{dt.strftime('%d-%m-%Y')} at {dt.strftime('%H:%M')}"
    except Exception as e:
        logger.warning(f"Could not parse kickoff time {kickoff_time}: {e}")
        return "Time TBD"


def format_score(home_score: Optional[int], away_score: Optional[int]) -> str:
    """
    Format match score as a readable string.
    
    Args:
        home_score: Home team score or None
        away_score: Away team score or None
        
    Returns:
        Formatted score string
    """
    if home_score is None or away_score is None:
        return "Game has not happened yet"
    return f"Final score was {home_score} - {away_score}"


def get_team_schedule(team_name: str) -> list[MatchResult]:
    """
    Get full schedule of fixtures for a team.
    
    Args:
        team_name: Team name (case-insensitive, partial match supported)
        
    Returns:
        List of MatchResult objects for all fixtures involving the team
        
    Raises:
        FPLAPIError: If team is not found
    """
    client = get_client()
    
    # Get team by name
    team = client.get_team_by_name(team_name)
    if team is None:
        raise FPLAPIError(f"Team '{team_name}' not found")
    
    # Get all fixtures for the team
    fixtures = client.get_fixtures_for_team(team.id)
    
    # Get all teams for name lookup
    all_teams = {t.id: t for t in client.get_teams()}
    
    # Convert to MatchResult objects
    results = []
    for fixture in fixtures:
        home_team = all_teams.get(fixture.team_h)
        away_team = all_teams.get(fixture.team_a)
        
        if not home_team or not away_team:
            logger.warning(f"Could not find team info for fixture {fixture.id}")
            continue
        
        kickoff_time = None
        if fixture.kickoff_time:
            try:
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
            venue="home" if fixture.team_h == team.id else "away"
        )
        results.append(result)
    
    return results


def print_team_schedule(team_name: str) -> None:
    """
    Print full schedule for a team.
    
    Args:
        team_name: Team name
    """
    try:
        schedule = get_team_schedule(team_name)
        print(f"\nFull Schedule for {team_name}:\n")
        print("=" * 70)
        
        for match in schedule:
            print(f"{match.home_team} vs {match.away_team}")
            print(f"  {match.format_kickoff_time()}")
            print(f"  {match.format_score()}")
            if match.gameweek:
                print(f"  Gameweek {match.gameweek}")
            print("-" * 70)
    
    except FPLAPIError as e:
        logger.error(str(e))
        print(f"Error: {str(e)}")


def main(team: str) -> None:
    """
    Main function to get and display team schedule.
    
    Args:
        team: Team name
    """
    logging.basicConfig(level=logging.INFO)
    print_team_schedule(team)


if __name__ == "__main__":
    main("Arsenal")
