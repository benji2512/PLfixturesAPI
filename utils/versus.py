import requests

def main(team1, team2):
    teams = {1:"Arsenal", 2:"Aston Villa", 3:"Brentford", 4:"Brighton and Hove Albion", 5:"Burnley", 6:"Chelsea", 7:"Crystal Palace", 8:"Everton", 9:"Leicester City", 10:"Leeds United", 11:"Liverpool", 12:"Manchester City", 13:"Manchester United", 14:"Newcastle United", 15:"Norwich City", 16:"Southampton", 17:"Tottenham Hotspur", 18:"Watford", 19:"West Ham United", 20:"Wolverhampton Wanderers"}
    res = requests.get("https://fantasy.premierleague.com/api/fixtures/")
    result = res.json()
    i = 1
    while i < len(result):
        team_a = result[i]["team_a"]
        team_h = result[i]["team_h"]
        if team_a == team1 and team_h == team2 or team_a == team2 and team_h == team1:
            print("Gameweek " + str(result[i]["event"]))
            print(result[i]["kickoff_time"])
            if team_a in teams.keys():
                away = team_a
            else:
                away = "Not in dict"
            if team_h in teams.keys():
                home = team_h
            else:
                home = "Not in dict"
            game = "{0} vs {1}".format(teams[home], teams[away])
            print(game)
        i+=1

if __name__ == "__main__":
    team1 = 13
    team2 = 11
    main(team1, team2)
