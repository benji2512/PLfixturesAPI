"""Data models for Premier League fixtures API."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Team(BaseModel):
    """Team model from FPL API."""
    
    id: int
    name: str
    short_name: str
    code: int


class Fixture(BaseModel):
    """Fixture/match model from FPL API."""
    
    id: int
    code: int
    team_h: int = Field(..., description="Home team ID")
    team_a: int = Field(..., description="Away team ID")
    team_h_score: Optional[int] = None
    team_a_score: Optional[int] = None
    event: Optional[int] = Field(None, description="Gameweek number")
    finished: bool = False
    minutes: int = 0
    provisional_start_time: bool = False
    kickoff_time: Optional[str] = None
    event_name: Optional[str] = None
    is_home: bool = True
    difficulty: int = 0


class Gameweek(BaseModel):
    """Gameweek model from FPL API."""
    
    id: int
    name: str
    deadline_time: Optional[str] = None
    average_entry_score: Optional[int] = None
    finished: bool = False
    data_checked: bool = False
    highest_scoring_entry: Optional[int] = None
    deadline_time_epoch: Optional[int] = None
    deadline_time_game_offset: int = 0
    highest_score: Optional[int] = None
    is_previous: bool = False
    is_current: bool = False
    is_next: bool = False


class MatchResult(BaseModel):
    """Formatted match result for display."""
    
    home_team: str
    away_team: str
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    kickoff_time: Optional[datetime] = None
    gameweek: Optional[int] = None
    finished: bool = False
    venue: str = "home"
    
    def format_kickoff_time(self) -> str:
        """Format kickoff time as a readable string."""
        if self.kickoff_time is None:
            return "Game was cancelled and is to be rescheduled"
        return f"{self.kickoff_time.strftime('%d-%m-%Y')} at {self.kickoff_time.strftime('%H:%M')}"
    
    def format_score(self) -> str:
        """Format match score as a readable string."""
        if self.home_score is None or self.away_score is None:
            return "Game has not happened yet"
        return f"Final score was {self.home_score} - {self.away_score}"
    
    def __str__(self) -> str:
        """String representation of the match."""
        score_str = self.format_score()
        time_str = self.format_kickoff_time()
        return f"{self.home_team} vs {self.away_team} - {time_str}\n{score_str}"

