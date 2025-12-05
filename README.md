# Premier League Fixtures API  

This API provides up-to-date Premier League fixture details, gameweek information, and standings. It uses the free Fantasy Premier League API as the data source.

## Features

- **Full team schedules**: Get all fixtures for any Premier League team
- **Next game lookup**: Find the next upcoming game for a team
- **Gameweek information**: Get fixtures for specific gameweeks
- **League standings**: Calculate and display current league standings
- **Modern Python**: Built with Python 3.13, type hints, and best practices

## Technology Stack

- **Python 3.13**: Latest Python version
- **Fantasy Premier League API**: Free, no API key required
- **Pydantic**: Data validation and models
- **Requests**: HTTP client for API calls
- **Python-dateutil**: Advanced date/time handling

## Installation

1. Ensure you have Python 3.13 installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Project Structure

```
PLfixturesAPI/
├── utils/
│   ├── fpl_api.py          # FPL API client
│   ├── models.py            # Data models (Pydantic)
│   ├── fullSchedule.py      # Get full team schedule
│   ├── nextGame.py          # Get next game for a team
│   ├── gameweek.py          # Gameweek utilities
│   └── standings.py         # League standings
├── requirements.txt         # Python dependencies
├── pyrightconfig.json      # Type checking configuration
└── README.md               # This file
```

## Usage Examples

### Get Full Schedule for a Team

```python
from utils.fullSchedule import print_team_schedule

print_team_schedule("Arsenal")
```

### Get Next Game for a Team

```python
from utils.nextGame import print_next_game

print_next_game("Manchester United")
```

### Get Gameweek Fixtures

```python
from utils.gameweek import print_gameweek_fixtures

print_gameweek_fixtures(5)  # Get fixtures for gameweek 5
```

### Get Current Gameweek

```python
from utils.gameweek import get_current_gameweek_number

current_gw = get_current_gameweek_number()
print(f"Current gameweek: {current_gw}")
```

### Get League Standings

```python
from utils.standings import print_standings

print_standings()
```

### Programmatic Usage

```python
from utils.fpl_api import get_client
from utils.models import MatchResult

client = get_client()

# Get all teams
teams = client.get_teams()
for team in teams:
    print(f"{team.id}: {team.name}")

# Get fixtures for a specific gameweek
fixtures = client.get_fixtures(gameweek=1)

# Get fixtures for a team
team_fixtures = client.get_fixtures_for_team_by_name("Liverpool")
```

## API Endpoints Used

The project uses the following free Fantasy Premier League API endpoints:

- `https://fantasy.premierleague.com/api/bootstrap-static/` - Teams, gameweeks, season info
- `https://fantasy.premierleague.com/api/fixtures/` - All fixtures
- `https://fantasy.premierleague.com/api/fixtures/?event={gameweek}` - Specific gameweek fixtures

## Data Models

The project uses Pydantic models for type safety and validation:

- `Team`: Team information
- `Fixture`: Match fixture data
- `Gameweek`: Gameweek information
- `MatchResult`: Formatted match result for display

## Future Enhancements

- [ ] Populate MongoDB with per-team fixture information
  - Automating it obviously
  - [ ] Clean up returned data into a per-team basis in MongoDB styling
  - [ ] Write script to push gathered information to MongoDB
- [ ] Setup CI workflow for data comparison
  - [ ] Choose a provider
- [ ] Add OpenFaaS deployment configuration
- [ ] Add caching layer for improved performance
- [ ] Add unit tests

## Notes

- The FPL API is free and doesn't require authentication
- API responses are cached for 5 minutes by default to reduce API calls
- Team names are matched case-insensitively and support partial matches
- All date/time handling is timezone-aware
