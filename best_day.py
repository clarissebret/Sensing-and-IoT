# WORK OF CLARISSE BRET

import warnings
warnings.filterwarnings('ignore')
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')
from weather import Weather, resorts
import datetime
import pandas as pd
from weather_analysis import dic_float
from statsmodels.tsa.arima_model import ARIMA
from user_profile import User
from pprint import pprint


def convert_datetime(string):
    date = datetime.datetime.strptime(string, "%Y-%m-%d %H:%M")
    return date


def best_day(name, forecast_date):

    user = User()

    data = user.get_user(name)
    df = pd.DataFrame.from_dict(data, orient='columns')
    # df = (df - df.mean()) / df.std()
    # summary = df.describe()
    # summary.to_csv('summary.csv', sep=',')

    train = df[:int(float(5/7) * (len(df)))]
    valid = df[int(float(5/7) * (len(df))):]

    train.index = pd.DatetimeIndex(train.index.values, freq='1H')

    # Fit model on train set
    model = ARIMA(endog=train['activity'], order=(1,0,0), exog = train.iloc[:, 0:6])
    model_fit = model.fit(disp=0)
    print(model_fit.summary())

    #Forecast on valid set
    # prediction = model_fit.forecast(steps=len(valid), exog=valid.iloc[:,0:6])
    # print(prediction)

    # Fit model on entire set
    # model = ARIMA(endog=df['activity'], order=(1,0,0), exog=df.iloc[:, 0:6])
    # model_fit = model.fit(disp=0)

    resort_predictions = []
    time_predictions = []

    # Store exogenous variables from today's weather in exog dataframe
    for resort, q in resorts.items():
        current_weather = user.weather_query('today',q)
        index = dic_float(current_weather[0])[2]
        exog = pd.DataFrame(index=index[9:18], columns=list(df)[0:6])

        for j in range(0,len(list(df)[0:5])):
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
