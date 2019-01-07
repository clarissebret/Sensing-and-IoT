import warnings
warnings.filterwarnings('ignore')
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')
from weather import Weather, resorts
import numpy as np
import datetime
import pandas as pd
from weather_analysis import dic_float
from statsmodels.tsa.arima_model import ARIMA

def convert_datetime(string):
    date = datetime.datetime.strptime(string, "%Y-%m-%d %H:%M")
    return date


def best_day(forecast_date):

    print("INITIALISING...")

    time_activity = {
        'day1' : {'start':'2018-12-17 13:06', 'end':'2018-12-17 16:21', 'resort':'Brevent-Flegere'},
        'day2' : {'start':'2018-12-18 10:49', 'end':'2018-12-18 16:29', 'resort':'Courmayeur'},
        'day3' : {'start':'2018-12-19 12:02', 'end': '2018-12-19 17:17', 'resort':'Brevent-Flegere'},
        'day4' : {'start':'2018-12-20 11:47', 'end': '2018-12-20 16:49', 'resort':'St Gervais Les Bains'},
        'day5': {'start':'2018-12-21 10:39', 'end': '2018-12-21 12:51', 'resort':'Grands Montets'},
        'day6': {'start': '2018-12-28 10:39', 'end': '2018-12-28 12:51', 'resort':'Brevent-Flegere'},
        'day7': {'start': '2018-12-30 10:39', 'end': '2018-12-30 12:51', 'resort':'Contamines-Montjoie'}
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

    train = df[:int(float(5/7) * (len(df)))]
    valid = df[int(float(5/7) * (len(df))):]

    train.index = pd.DatetimeIndex(train.index.values, freq='1H')

    # Fit model on train set
    model = ARIMA(endog=train['activity'], order=(1,0,0), exog = train.iloc[:, 0:6])
    model_fit = model.fit()

    # Forecast on valid set
    # prediction = model_fit.forecast(steps=len(valid), exog=valid.iloc[:,0:6])

    # # Fit model on entire set
    # model = ARIMA(endog=df['activity'], order=(5,0,0), exog=df.iloc[:, 0:6])
    # model_fit = model.fit()

    resort_predictions = []
    time_predictions = []

    # Store exogenous variables from today's weather in exog dataframe
    for resort, q in resorts.items():
        current_weather = w.weather_query([forecast_date],q)
        index = dic_float(current_weather[0])[2]
        exog = pd.DataFrame(index=index[9:18], columns=header[0:6])

        for j in range(0,len(header[0:5])):
            values = dic_float(current_weather[j])[1]
            for i in range(0,9):
                exog.iloc[i][j] = values[i+9]

        exog['status'] = 1

        # Forecast for 24 hours
        prediction = model_fit.forecast(steps=9, exog=exog)

        # Total activity for the day
        prediction_second = 0
        for p in prediction[0]:
            prediction_second += p

        resort_predictions.append(resort)
        time_predictions.append(prediction_second)

    best_prediction_s = max(time_predictions)
    index = time_predictions.index(best_prediction_s)
    best_resort = resort_predictions[index]
    best_prediction = str(datetime.timedelta(seconds=best_prediction_s))

    print('%s will be perfect for you today! (time activity estimation: %s)' % (best_resort, best_prediction))
    return best_resort