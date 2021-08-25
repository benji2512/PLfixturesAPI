import requests, os
from dotenv import load_dotenv
from pymongo import MongoClient
from pprint import pprint

def main():
    load_dotenv()
    mongodburi = os.getenv("MONGODBURI")
    client = MongoClient(mongodburi)
    db = client.PLFixtures

    cursor = db.Gameweeks.find({"match":"Manchester United vs Chelsea"})

    for gw in cursor:
        pprint(gw)

if __name__ == "__main__":
    main()