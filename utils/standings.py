"""Standings utilities for Premier League."""

import logging
from typing import List, Dict, Optional

from .fpl_api import get_client, FPLAPIError
from .models import Team, Fixture

logger = logging.getLogger(__name__)


def calculate_standings() -> List[Dict[str, any]]:
    """
    Calculate league standings from fixture results.
    
    Note: FPL API doesn't provide direct standings, so we calculate from fixtures.
    This is a simplified calculation based on available fixture data.
    
    Returns:
        List of team standings dictionaries with points, wins, draws, losses, etc.
    """
    client = get_client()
    teams = {team.id: team for team in client.get_teams()}
    fixtures = client.get_fixtures()
    
    # Initialize standings for each team
    standings: Dict[int, Dict[str, any]] = {}
    for team_id, team in teams.items():
        standings[team_id] = {
            'team_id': team_id,
            'team_name': team.name,
            'played': 0,
            'won': 0,
            'drawn': 0,
            'lost': 0,
            'goals_for': 0,
            'goals_against': 0,
            'goal_difference': 0,
            'points': 0
        }
    
    # Process finished fixtures
    for fixture in fixtures:
        if not fixture.finished or fixture.team_h_score is None or fixture.team_a_score is None:
            continue
        
        home_id = fixture.team_h
        away_id = fixture.team_a
        home_score = fixture.team_h_score
        away_score = fixture.team_a_score
        
        # Update home team
        standings[home_id]['played'] += 1
        standings[home_id]['goals_for'] += home_score
        standings[home_id]['goals_against'] += away_score
        
        # Update away team
        standings[away_id]['played'] += 1
        standings[away_id]['goals_for'] += away_score
        standings[away_id]['goals_against'] += home_score
        
        # Determine result
        if home_score > away_score:
            standings[home_id]['won'] += 1
            standings[home_id]['points'] += 3
            standings[away_id]['lost'] += 1
        elif away_score > home_score:
            standings[away_id]['won'] += 1
            standings[away_id]['points'] += 3
            standings[home_id]['lost'] += 1
        else:
            standings[home_id]['drawn'] += 1
            standings[home_id]['points'] += 1
            standings[away_id]['drawn'] += 1
            standings[away_id]['points'] += 1
    
    # Calculate goal difference
    for team_id in standings:
        standings[team_id]['goal_difference'] = (
            standings[team_id]['goals_for'] - standings[team_id]['goals_against']
        )
    
    # Convert to list and sort by points (desc), then goal difference (desc), then goals for (desc)
    standings_list = list(standings.values())
    standings_list.sort(
        key=lambda x: (x['points'], x['goal_difference'], x['goals_for']),
        reverse=True
    )
    
    # Add position
    for i, team in enumerate(standings_list, 1):
        team['position'] = i
    
    return standings_list


def print_standings() -> None:
    """Print formatted league standings."""
    standings = calculate_standings()
    
    print("\nPremier League Standings:\n")
    print(f"{'Pos':<5} {'Team':<25} {'P':<4} {'W':<4} {'D':<4} {'L':<4} {'GF':<4} {'GA':<4} {'GD':<5} {'Pts':<5}")
    print("=" * 75)
    
    for team in standings:
        print(
            f"{team['position']:<5} "
            f"{team['team_name']:<25} "
            f"{team['played']:<4} "
            f"{team['won']:<4} "
            f"{team['drawn']:<4} "
            f"{team['lost']:<4} "
            f"{team['goals_for']:<4} "
            f"{team['goals_against']:<4} "
            f"{team['goal_difference']:>4} "
            f"{team['points']:<5}"
        )


def get_team_position(team_name: str) -> Optional[int]:
    """
    Get the current league position of a team.
    
    Args:
        team_name: Team name
        
    Returns:
        Team position (1-20) or None if team not found
    """
    standings = calculate_standings()
    for team in standings:
        if team_name.lower() in team['team_name'].lower():
            return team['position']
    return None


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    print_standings()

