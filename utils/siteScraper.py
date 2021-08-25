import requests, datetime

def main(gameweek):
    teams = {1:"Arsenal", 2:"Aston Villa", 3:"Brentford", 4:"Brighton and Hove Albion", 5:"Burnley", 6:"Chelsea", 7:"Crystal Palace", 8:"Everton", 9:"Leicester City", 10:"Leeds United", 11:"Liverpool", 12:"Manchester City", 13:"Manchester United", 14:"Newcastle United", 15:"Norwich City", 16:"Southampton", 17:"Tottenham Hotspur", 18:"Watford", 19:"West Ham United", 20:"Wolverhampton Wanderers"}
    res = requests.get("https://fantasy.premierleague.com/api/fixtures/")
    result = res.json()
    i = 0
    while i < len(result):
        if result[i]["event"] == gameweek:
            team_a = result[i]["team_a"]
            team_h = result[i]["team_h"]
            kickoffDateTime = result[i]["kickoff_time"]
            kickoffDateTime = datetime.datetime.fromisoformat(kickoffDateTime[:-1])
            kickoffDate = "{0}-{1}-{2}".format(kickoffDateTime.day, kickoffDateTime.month, kickoffDateTime.year)
            kickoffTime2 = kickoffDateTime.time()
            if team_a in teams.keys():
                away = team_a
            else:
                away = "Not in dict"
            if team_h in teams.keys():
                home = team_h
            else:
                home = "Not in dict"
            game = "{0} vs {1} on {2} at {3}".format(teams[home], teams[away], kickoffDate, kickoffTime2)
            print(game)
        i+=1
if __name__ == "__main__":
    gw = 1
    while gw < 39:
        gameweek = gw
        print("Gameweek " + str(gw))
        main(gameweek)
        print("----------")
        gw += 1

