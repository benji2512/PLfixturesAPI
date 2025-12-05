"""Get next game for a team."""

import logging
from typing import Optional
from datetime import datetime

from dateutil import parser as date_parser

from .fpl_api import get_client, FPLAPIError
from .models import MatchResult

logger = logging.getLogger(__name__)


def format_kickoff_time(kickoff_time: Optional[str]) -> Optional[str]:
    """
    Format kickoff time as a readable string, or return None if in the past.
    
    Args:
        kickoff_time: ISO format datetime string or None
        
    Returns:
        Formatted time string or None if time is in the past
    """
    if kickoff_time is None:
        return None
    
    try:
        # FPL API returns ISO format with 'Z' suffix
        dt = date_parser.parse(kickoff_time.replace('Z', '+00:00'))
        current_time = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        
        if dt > current_time:
            return f"{dt.strftime('%d-%m-%Y')} at {dt.strftime('%H:%M')}"
        return None
    except Exception as e:
        logger.warning(f"Could not parse kickoff time {kickoff_time}: {e}")
        return None


def get_next_game(team_name: str) -> Optional[MatchResult]:
    """
    Get the next upcoming game for a team.
    
    Args:
        team_name: Team name (case-insensitive, partial match supported)
        
    Returns:
        MatchResult for the next game or None if no upcoming games
        
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
    
    # Find the next upcoming fixture
    current_time = datetime.now()
    next_fixture = None
    next_fixture_time = None
    
    for fixture in fixtures:
        if fixture.kickoff_time is None:
            continue
        
        try:
            fixture_time = date_parser.parse(fixture.kickoff_time.replace('Z', '+00:00'))
            # Convert to naive datetime for comparison if needed
            if fixture_time.tzinfo:
                fixture_time_naive = fixture_time.replace(tzinfo=None)
                current_time_naive = current_time.replace(tzinfo=None) if current_time.tzinfo else current_time
            else:
                fixture_time_naive = fixture_time
                current_time_naive = current_time
            
            if fixture_time_naive > current_time_naive:
                if next_fixture_time is None or fixture_time_naive < next_fixture_time:
                    next_fixture = fixture
                    next_fixture_time = fixture_time_naive
        except Exception as e:
            logger.warning(f"Could not parse kickoff time {fixture.kickoff_time}: {e}")
            continue
    
    if next_fixture is None:
        return None
    
    # Create MatchResult
    home_team = all_teams.get(next_fixture.team_h)
    away_team = all_teams.get(next_fixture.team_a)
    
    if not home_team or not away_team:
        logger.warning(f"Could not find team info for fixture {next_fixture.id}")
        return None
    
    kickoff_time = None
    if next_fixture.kickoff_time:
        try:
            kickoff_time = date_parser.parse(next_fixture.kickoff_time.replace('Z', '+00:00'))
        except Exception as e:
            logger.warning(f"Could not parse kickoff time {next_fixture.kickoff_time}: {e}")
    
    return MatchResult(
        home_team=home_team.name,
        away_team=away_team.name,
        home_score=next_fixture.team_h_score,
        away_score=next_fixture.team_a_score,
        kickoff_time=kickoff_time,
        gameweek=next_fixture.event,
        finished=next_fixture.finished,
        venue="home" if next_fixture.team_h == team.id else "away"
    )


def print_next_game(team_name: str) -> None:
    """
    Print the next game for a team.
    
    Args:
        team_name: Team name
    """
    try:
        next_match = get_next_game(team_name)
        
        if next_match is None:
            print(f"\nNo upcoming games found for {team_name}")
            return
        
        print(f"\nNext Game for {team_name}:")
        print("=" * 70)
        print(f"{next_match.home_team} vs {next_match.away_team}")
        print(f"  {next_match.format_kickoff_time()}")
        if next_match.gameweek:
            print(f"  Gameweek {next_match.gameweek}")
        print("=" * 70)
    
    except FPLAPIError as e:
        logger.error(str(e))
        print(f"Error: {str(e)}")


def main(team: str) -> None:
    """
    Main function to get and display next game.
    
    Args:
        team: Team name
    """
    logging.basicConfig(level=logging.INFO)
    print_next_game(team)


if __name__ == "__main__":
    main("Manchester United")
