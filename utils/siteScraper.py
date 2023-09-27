
import re,requests, datetime
from bs4 import BeautifulSoup
from urllib.request import urlopen
#from pymongo import MongoClient
#from pymongo.server_api import ServerApi

def scrapeContent():
    url = "https://www.skysports.com/premier-league-fixtures" # use https://www.skysports.com/manchester-united-fixtures for just United games
    page = urlopen(url)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    return soup

def gameBreakdown(html):
    # dict object : {"date": list of fixtures}
    # progression to team based db
    # mongouri = "mongodb+srv://plfixturesdb.l3h7281.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
    # client = MongoClient(mongouri,
    #                  tls=True,
    #                  tlsCertificateKeyFile='../X509-cert-5032269924842152828.pem',
    #                  server_api=ServerApi('1'))
    # fixturesdb = client["fixturesdb"]
    # allfixtures = fixturesdb["allfixtures"]
    # mongodict = {}
    # {x: x**2 for x in (2, 4, 6)} <- example of dictionary comprehension3
    gameDates = html.find_all('h4', class_='fixres__header2') # Gets array of fixture dates from h4 tags
    gamelistList = []
    for date in gameDates:
        readableDate = date.get_text()
        for detail in date.find_next_sibling("div", "fixres__item"):
            # print(detail)
            nonReadableDetails = detail.get_text(strip=True)
            # print(nonReadableDetails)
            readableDetails = re.split(r"(00|\d\d:\w\w)", nonReadableDetails, maxsplit=2) # This regex seems to work atm. Will see how it holds up
            # print(readableDetails)
            if len(readableDetails) < 4:
                continue
            else:
                readableFixtures = gameListToString(readableDetails, readableDate)
                print(readableFixtures)
            # if len(readableDetails)>1:
                # print(readableDate, readableFixtures)
        # print({readableDate: detail.get_text(strip=True).split("00") for detail in date.find_next_siblings("div", "fixres__item")})
        # print(mongodict)

def gameListToString(gameList, date):
    # example list ['Burnley', '00', '', '20:00', 'Manchester City']
    # remove element 1 and 2
    gameList.remove('00')
    gameList.remove('')
    string1 = "{}\n{} v {} @ {}".format(date, gameList[0],gameList[2],gameList[1])
    return string1

def outputGameTeams(games_metadata):
    print(games_metadata)

if __name__ == "__main__":
    skySportsPageHTML=scrapeContent()
    games_metadata=gameBreakdown(skySportsPageHTML)
    # outputGameDetails(games_metadata)
