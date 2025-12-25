"""Main CLI entry point for fplapi command."""

import argparse
import sys
from typing import Optional

from . import fullSchedule, nextGame, gameweek, standings


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="fplapi",
        description="Premier League Fixtures API - Get fixtures, gameweeks, and standings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # nextGame command
    nextgame_parser = subparsers.add_parser(
        "nextGame",
        aliases=["next", "next-game"],
        help="Get the next upcoming game for a team",
        description="Get the next upcoming game for a Premier League team",
    )
    nextgame_parser.add_argument(
        "team",
        type=str,
        nargs="?",
        help="Team name (case-insensitive, partial match supported)"
    )
    nextgame_parser.add_argument(
        "-l", "--list-teams",
        action="store_true",
        help="List all available teams"
    )
    nextgame_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    # fullSchedule command
    schedule_parser = subparsers.add_parser(
        "fullSchedule",
        aliases=["schedule", "full-schedule"],
        help="Get full schedule of fixtures for a team",
        description="Get full schedule of fixtures for a Premier League team",
    )
    schedule_parser.add_argument(
        "team",
        type=str,
        nargs="?",
        help="Team name (case-insensitive, partial match supported)"
    )
    schedule_parser.add_argument(
        "-l", "--list-teams",
        action="store_true",
        help="List all available teams"
    )
    schedule_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    # gameweek command
    gameweek_parser = subparsers.add_parser(
        "gameweek",
        aliases=["gw"],
        help="Get gameweek information and fixtures",
        description="Get Premier League gameweek information and fixtures",
    )
    gameweek_parser.add_argument(
        "-g", "--gameweek",
        type=int,
        metavar="GW",
        help="Show fixtures for specific gameweek number"
    )
    gameweek_parser.add_argument(
        "-c", "--current",
        action="store_true",
        help="Show current gameweek number only"
    )
    gameweek_parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="List all gameweeks in the season"
    )
    gameweek_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    # standings command
    standings_parser = subparsers.add_parser(
        "standings",
        aliases=["table", "league-table"],
        help="Get Premier League standings",
        description="Get Premier League standings",
    )
    standings_parser.add_argument(
        "-t", "--team",
        type=str,
        metavar="TEAM",
        help="Get position for a specific team"
    )
    standings_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # If no command provided, show help
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Import logging here to avoid issues if not needed
    import logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')
    
    # Route to appropriate command
    if args.command in ["nextGame", "next", "next-game"]:
        if args.list_teams:
            from .fpl_api import list_all_teams
            teams = list_all_teams()
            print("\nAvailable Premier League Teams:\n")
            for team in sorted(teams, key=lambda t: t.name):
                print(f"  {team.name} (short: {team.short_name})")
        elif not args.team:
            nextgame_parser.error("Team name is required (or use --list-teams to see available teams)")
        else:
            nextGame.print_next_game(args.team)
    
    elif args.command in ["fullSchedule", "schedule", "full-schedule"]:
        if args.list_teams:
            from .fpl_api import list_all_teams
            teams = list_all_teams()
            print("\nAvailable Premier League Teams:\n")
            for team in sorted(teams, key=lambda t: t.name):
                print(f"  {team.name} (short: {team.short_name})")
        elif not args.team:
            schedule_parser.error("Team name is required (or use --list-teams to see available teams)")
        else:
            fullSchedule.print_team_schedule(args.team)
    
    elif args.command in ["gameweek", "gw"]:
        if args.current:
            current_gw = gameweek.get_current_gameweek_number()
            if current_gw:
                print(f"Current gameweek: {current_gw}")
            else:
                print("No current gameweek found")
        elif args.list:
            gameweeks = gameweek.get_all_gameweeks()
            print("\nAll Gameweeks in Season:\n")
            print(f"{'GW':<5} {'Name':<20} {'Finished':<10} {'Current':<10} {'Next':<10}")
            print("=" * 60)
            for gw in gameweeks:
                print(
                    f"{gw.id:<5} "
                    f"{gw.name:<20} "
                    f"{str(gw.finished):<10} "
                    f"{str(gw.is_current):<10} "
                    f"{str(gw.is_next):<10}"
                )
        elif args.gameweek:
            gameweek.print_gameweek_fixtures(args.gameweek)
        else:
            # Default: show current gameweek fixtures
            current_gw = gameweek.get_current_gameweek_number()
            if current_gw:
                print(f"Current gameweek: {current_gw}")
                gameweek.print_gameweek_fixtures(current_gw)
            else:
                print("No current gameweek found")
    
    elif args.command in ["standings", "table", "league-table"]:
        if args.team:
            position = standings.get_team_position(args.team)
            if position:
                print(f"\n{args.team} is currently in position {position}")
            else:
                print(f"\nTeam '{args.team}' not found")
        else:
            standings.print_standings()


if __name__ == "__main__":
    main()

