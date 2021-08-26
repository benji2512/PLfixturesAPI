from pymongo import MongoClient
def handle(date):
    client = MongoClient("mongodb+srv://benthedev:{PASSWORD}@cluster0.50ibf.mongodb.net/PLFixtures?retryWrites=true&w=majority")
    db = client.PLFixtures

    cursor = db.Gameweeks.find({"date":date})
    games = []
    for gw in cursor:
        games.append(gw)
    return games
