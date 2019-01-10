from datetime import datetime
import requests
import urllib.parse
from pymongo import MongoClient

resorts = {
    'Brevent-Flegere': '45.934,6.839',
    'Balme': '46.042,6.952',
    'Grands Montets': '45.957,6.952',
    'Houches': '45.885,6.752',
    'Courmayeur': '45.790,6.933',
    'Verbiers': '46.091,7.254',
    'St Gervais Les Bains': '45.849,6.614',
    'Contamines-Montjoie': '45.961,6.887'
}

dates = ['2018-12-17', '2018-12-18', '2018-12-19', '2018-12-20', '2018-12-21', '2018-12-22', '2018-12-23',
         '2018-12-24', '2018-12-25', '2018-12-26', '2018-12-27', '2018-12-28', '2018-12-29', '2018-12-30']


class Weather:

    """
    A class to add, retrieve and delete past weather data from/to MongoDB Atlas.
    """

    def __init__(self):

        self.client = MongoClient("mongodb+srv://clarissebret:sensing-and-iot@cluster0-xrhtq.mongodb.net/")
        self.db = self.client.ski
        self.weather = self.db.weather

    @staticmethod
    def weather_query(date, q):

        """
        A static method retrieving weather data from World Weather Online local historical weather API.
        :param date: a list of dates in string format %Y-%m-%d
        :param q: geographical coordinates in decimal string format XXX.XXX, XXX.XXX
        :return: 5 time series: temperature (ºC), precipitations (mm), wind (km/h), snow falls (cm)
        """

        key = '932520134b344e028f4113339191001'
        tp = 1

        temp = {}
        visi = {}
        precip = {}
        wind = {}
        snow = {}

        for j in range(0, len(date)):

            params = {'key': key, 'q': q, "date": date[j], "tp": tp, "format": "json","includelocation":"yes"}
            query = urllib.parse.urlencode(params)
            url_query = urllib.parse.unquote(query)
            url = 'http://api.worldweatheronline.com/premium/v1/past-weather.ashx?' + url_query
            response = requests.get(url)
            data = response.json()
            weather = data["data"]["weather"][0]

            for i in range(0, len(weather["hourly"])):
                t = weather['date'] + " " + str(int(int(weather["hourly"][i]["time"]) * 0.01))
                ts = datetime.strptime(t, "%Y-%m-%d %H").strftime("%Y-%m-%d %H:%M")
                temp[ts] = weather["hourly"][i]["tempC"]
                visi[ts] = weather["hourly"][i]["cloudcover"]
                precip[ts] = weather["hourly"][i]["precipMM"]
                wind[ts] = weather["hourly"][i]["windspeedKmph"]
                snow[ts] = weather["totalSnow_cm"]

        return temp, visi, precip, wind, snow

    def get_location(self, place, name = "", q = "", temp = "", visi = "", precip = "", wind = "", snow = ""):

        query = list(self.weather.find(
            {"name": place},
            {"_id": 0, name: 1, q: 1, temp: 1, visi: 1, precip: 1, wind: 1, snow: 1}
        ))

        if len(query) == 0:
            print("%s is not in the database. Use add_location to insert it." % place)

        else:

            return query[0]

    def add_location(self, date, place, q):

        query = list(self.weather.find({"name": place}))

        if len(query) == 0:

            location = {}
            weather = self.weather_query(date, q)
            location["name"] = place
            location["q"] = q
            location["temp"] = weather[0]
            location["visi"] = weather[1]
            location["precip"] = weather[2]
            location["wind"] = weather[3]
            location["snow"] = weather[4]
            self.weather.insert_one(location)

        else:

            print("%s was already added to this collection: use update_location instead." % place)

    def delete_location(self, place):

        query = list(self.weather.find({"name": place}))

        if len(query) == 0:
            print("%s is not in the database. Use add_location to insert it." % place)

        else:
            self.weather.delete_one({"name":place})


if __name__ == '__main__':

    w = Weather()

    # Perform any action
    # for k,v in resorts.items():
    #    pprint(w.get_location(k, "name","temp","precip", "snow","visi","wind"))