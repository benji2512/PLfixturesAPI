import requests, datetime

def kickoff_time_calc(kickoff_time):
    if kickoff_time == None:
        return "Game was cancelled and is to be rescheduled"
    else:
        kickoffDateTime = kickoff_time
        kickoffDateTime = datetime.datetime.fromisoformat(kickoffDateTime[:-1])
        kickoffDate = "{0}-{1}-{2}".format(kickoffDateTime.day, kickoffDateTime.month, kickoffDateTime.year)
        kickoffTime2 = kickoffDateTime.time()
        return "{0} at {1}".format(kickoffDate, kickoffTime2)

def nextMatch_calc(kickoff_time):
    currentDate = datetime.datetime.now()
    kickoffDateTime = datetime.datetime.fromisoformat(kickoff_time[:-1])
    if kickoffDateTime > currentDate:
        kickoffDate = "{0}-{1}-{2}".format(kickoffDateTime.day, kickoffDateTime.month, kickoffDateTime.year)
        kickoffTime2 = kickoffDateTime.time()
        return "{0} at {1}".format(kickoffDate, kickoffTime2)
    else:
        return 1

def main(team):
    teams = {1:"Arsenal", 2:"Aston Villa", 3:"Brentford", 4:"Brighton and Hove Albion", 5:"Burnley", 6:"Chelsea", 7:"Crystal Palace", 8:"Everton", 9:"Leeds United", 10:"Leicester City", 11:"Liverpool", 12:"Manchester City", 13:"Manchester United", 14:"Newcastle United", 15:"Norwich City", 16:"Southampton", 17:"Tottenham Hotspur", 18:"Watford", 19:"West Ham United", 20:"Wolverhampton Wanderers"}
    res = requests.get("https://fantasy.premierleague.com/api/fixtures/")
    result = res.json()

    try:
        for (k,v) in teams.items():
            if v == team:
                team_id = k
    except:
        print("No team in dictionary")

    i = 0
    j = 0
    while i < len(result):
        if result[i]["team_a"] == team_id or result[i]["team_h"] == team_id:
            team_a = result[i]["team_a"]
            team_h = result[i]["team_h"]
            if team_a in teams.keys():
                away = team_a
            if team_h in teams.keys():
                home = team_h
            next_match = nextMatch_calc(result[i]["kickoff_time"])
            if next_match == 1:
                pass
            else:
                game = "{0} vs {1} - {2}".format(teams[home], teams[away], next_match)
                print(game)
                break
            j+=1
        i+=1

if __name__ == "__main__":
    team = "Manchester United"
    main(team)