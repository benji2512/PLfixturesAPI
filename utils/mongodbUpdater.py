import requests, os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

# id: num,
# gameweek: 1,
# date: date,
# matches: [ match1: team_h v team_a ]

def main():
    load_dotenv()
    mongodburi = os.getenv("MONGODBURI")
    client = MongoClient(mongodburi)
    db = client.PLFixtures
    db.Gameweeks.drop()
    teams = {1:"Arsenal", 2:"Aston Villa", 3:"Brentford", 4:"Brighton and Hove Albion", 5:"Burnley", 6:"Chelsea", 7:"Crystal Palace", 8:"Everton", 9:"Leicester City", 10:"Leeds United", 11:"Liverpool", 12:"Manchester City", 13:"Manchester United", 14:"Newcastle United", 15:"Norwich City", 16:"Southampton", 17:"Tottenham Hotspur", 18:"Watford", 19:"West Ham United", 20:"Wolverhampton Wanderers"}
    res = requests.get("https://fantasy.premierleague.com/api/fixtures/")
    result = res.json()
    i = 0
    while i < len(result):
        gameweek = result[i]["event"] # gameweek
        team_a = result[i]["team_a"]
        team_h = result[i]["team_h"]
        if team_a in teams.keys():
            away = team_a # away team
        else:
            away = "Not in dict"
        if team_h in teams.keys(): # home team
            home = team_h
        else:
            home = "Not in dict"
        game = "{0} vs {1}".format(teams[home], teams[away])
        date = result[i]["kickoff_time"] # date
        dt = datetime.fromisoformat(date[:-1])
        dateString = "{:02d}/{:02d}/{}".format(dt.day, dt.month, dt.year)
        kickoffTimeString = "{:02d}:{:02d}BST".format(int(dt.hour), int(dt.minute))
        db.Gameweeks.insert_one(
            {"gameweek": gameweek,
             "date": dateString,
             "kickoffTime": kickoffTimeString,
             "match": game 
            }
        )
        i+=1

if __name__ == "__main__":
    main()
