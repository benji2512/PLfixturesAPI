import requests
from pymongo import MongoClient
from pprint import pprint

def main():
    client = MongoClient("mongodb+srv://benthedev:B3n4i%402516@cluster0.50ibf.mongodb.net/PLFixtures?retryWrites=true&w=majority")
    db = client.PLFixtures

    cursor = db.Gameweeks.find({"match":"Manchester United vs Chelsea"})

    for gw in cursor:
        pprint(gw)

if __name__ == "__main__":
    main()