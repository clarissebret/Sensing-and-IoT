import warnings
warnings.filterwarnings('ignore')
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')
from weather import Weather, resorts
import numpy as np
import datetime
import pandas as pd
from weather_analysis import dic_float
from pymongo import MongoClient
import urllib.parse
import requests
from pprint import pprint


def convert_datetime(string):
    date = datetime.datetime.strptime(string, "%Y-%m-%d %H:%M")
    return date


def user_df():

    time_activity = {

        'day1': {'start': '2018-12-17 13:06', 'end': '2018-12-17 16:21', 'resort': 'Brevent-Flegere'},
        'day2': {'start': '2018-12-18 10:49', 'end': '2018-12-18 16:29', 'resort': 'Courmayeur'},
        'day3': {'start': '2018-12-19 12:02', 'end': '2018-12-19 17:17', 'resort': 'Brevent-Flegere'},
        'day4': {'start': '2018-12-20 11:47', 'end': '2018-12-20 16:49', 'resort': 'St Gervais Les Bains'},
        'day5': {'start': '2018-12-21 10:39', 'end': '2018-12-21 12:51', 'resort': 'Grands Montets'},
        'day6': {'start': '2018-12-28 10:39', 'end': '2018-12-28 12:51', 'resort': 'Brevent-Flegere'},
        'day7': {'start': '2018-12-30 10:39', 'end': '2018-12-30 12:51', 'resort': 'Contamines-Montjoie'}
    }

    w = Weather()

    index = dic_float(w.get_location('Balme', "temp")["temp"])[2]
    header = ["temp", "visi", "precip", "wind", "snow", "status", "activity"]
    df = pd.DataFrame(index=index, columns=header,dtype=np.float64)

    # Adding ski activity to table
    for k, v in time_activity.items():

        start = convert_datetime(v['start'])
        end = convert_datetime(v['end'])
        resort = v['resort']

        for i in range(0, len(index)):

            ix = convert_datetime(index[i]) # Date of index
            opening = convert_datetime(('%s 9:00' % ix.date())) # Ski lift opening time
            closing = convert_datetime(('%s 18:00' % ix.date())) # Ski lift closing time

            # Match activity date with the right index date
            if start.date() == ix.date():

                query = w.get_location(resort, "temp", "precip", "snow", "visi", "wind")
                index = dic_float(query["temp"])[2]

                for j in query:

                    val = dic_float(query[j])[1]
                    df.iloc[i][j] = val[i]

                # Is index datetime within opening hours?
                if opening.time() <= ix.time() < closing.time():

                    # Ski lifts are opened
                    df.iloc[i][5] = 1

                    # Start of activity
                    if (start - ix).seconds < datetime.timedelta(hours=1).seconds:
                        df.iloc[i][6] = (start - ix).seconds # Start of activity

                    # End of activity
                    elif (end - ix).seconds < datetime.timedelta(hours=1).seconds:
                        df.iloc[i][6] = (end - ix).seconds

                    # Full 3 hours of activity
                    elif start < ix < end:
                        df.iloc[i][6] = datetime.timedelta(hours=1).seconds # Full 3 hours activity

                    # No ski activity
                    else:
                        df.iloc[i][6] = 0.0

                # Ski lifts are closed
                else:
                    df.iloc[i][6] = 0.0
                    df.iloc[i][5] = 0

    df = df[np.isfinite(df['activity'])]
    print(df)
    data = df.to_dict()

    return data


class User:

    """
    A class to add, retrieve and delete user data from/to MongoDB Atlas.
    """

    def __init__(self):

        self.client = MongoClient("mongodb+srv://clarissebret:sensing-and-iot@cluster0-xrhtq.mongodb.net/")
        self.db = self.client.ski
        self.user = self.db.user

    @staticmethod
    def weather_query(date, q):

        """
        A static method retrieving weather data from World Weather Online local weather API.
        :param date: a date, either 'today', 'tomorrow' or in string format %Y-%m-%d
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

        params = {'key': key, 'q': q, "date": date, "tp": tp, "format": "json","includelocation":"yes"}
        query = urllib.parse.urlencode(params)
        url_query = urllib.parse.unquote(query)
        url = 'http://api.worldweatheronline.com/premium/v1/weather.ashx?' + url_query
        response = requests.get(url)
        data = response.json()
        weather = data["data"]["weather"][0]

        for i in range(0, len(weather["hourly"])):
            t = weather['date'] + " " + "%s" % i
            ts = datetime.datetime.strptime(t, "%Y-%m-%d %H").strftime("%Y-%m-%d %H:%M")
            temp[ts] = weather["hourly"][i]["tempC"]
            visi[ts] = weather["hourly"][i]["cloudcover"]
            precip[ts] = weather["hourly"][i]["precipMM"]
            wind[ts] = weather["hourly"][i]["windspeedKmph"]
            snow[ts] = weather["totalSnow_cm"]

        return temp, visi, precip, wind, snow

    def get_user(self, name):

        query = list(self.user.find(
            {"_id": name},
            {"_id": 0}
        ))

        if len(query) == 0:
            print("%s is not in the database. Use add_location to insert it." % name)
        else:
            return query[0]

    def add_user(self, name, data):

        data["_id"] = name
        query = list(self.user.find({"_id": name}))

        if len(query) == 0:
            self.user.insert_one(data)
            print("%s was added to this collection!" % name)
        else:
            print("%s was already added to this collection. Use update_user instead." % name)

    def update_user(self, name, object, data):

        self.user.update_one({"_id": name}, {"$set": { object: data }})

    def delete_user(self, name):

        query = list(self.user.find({"_id": name}))

        if len(query) == 0:
            print("%s is not in this collection." % name)

        else:
            self.user.delete_one({"_id":name})


if __name__ == '__main__':

    user = User()
    data = user_df()
    name = "James" # user name in string format
    user.add_user(name, data)

