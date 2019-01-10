# WORK OF CLARISSE BRET

import warnings
warnings.filterwarnings('ignore')
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')
from weather import Weather
import numpy as np
import seaborn as sns
import mpld3

def dic_float(dic):

    lists_str = sorted(dic.items()) # sorted by key, return a list of tuples
    lists = list([i, float(lists_str[i][1]), lists_str[i][0]] for i in range(0,len(lists_str)))
    indexes, values, dates = zip(*lists) # unpack a list of pairs into two tuples

    return indexes, values, dates


def plot():

    colours = ['#FA9F42','#957186','#32908F','#26C485','#5EC5E5','#192BC2', '#FA9F42', '#957186']

    w = Weather()
    locations = ["Houches", "Grands Montets", "Balme", "Brevent-Flegere", "Courmayeur", "Verbiers", 'Contamines-Montjoie', 'St Gervais Les Bains']


    ### SNOW AND RAIN PRECIPITATIONS OVER TIME ###

    fig1 = plt.figure(figsize=(15,14))

    sns.set(style='darkgrid', font='sans-serif', font_scale=0.75)
    sns.despine(left=True)

    for x in range(0,len(locations)-1):

        query = w.get_location(locations[x], "precip", "snow")
        precip = dic_float(query["precip"])
        snow = dic_float(query["snow"])
        index = precip[0]
        ts = precip[2]

        snow_precip = []

        for i in range(0, len(snow[0])):
            y = snow[1][i]*precip[1][i]
            snow_precip.append(y)

        n_precip = (precip[1] - np.mean(precip[1]))/np.std(precip[1])
        n_snow_precip = (snow_precip - np.mean(snow_precip))/np.std(snow_precip)

        ax = fig1.add_subplot(3, 3, x+1)

        ax.bar(index, n_precip[1], color=colours[1])
        ax.bar(index, n_snow_precip, color=colours[3])

        ax.set_xticks(index[::24])
        ax.set_xticklabels(ts[::24], fontsize=6, rotation=30)
        ax.set_ylabel('Precipitations (mm)')
        ax.set_title('%s' % locations[x])
        ax.legend(['Rain', 'Snow'], fontsize=7)


    ### VISIBILITY AND WIND OVER TIME ###

    fig2, ax = plt.subplots(nrows=2,ncols=1,figsize=(15, 14))

    for y in range(0,len(locations)):

        response = w.get_location(locations[y], "visi", "wind")

        visi_dic = response["visi"]
        visi = dic_float(visi_dic)

        wind_dic = response["wind"]
        wind = dic_float(wind_dic)

        index = visi[0]
        ts = visi[2]

        ax[0].plot(index, visi[1])
        ax[0].set_prop_cycle(color=colours[y])
        ax[0].set_xticks(index[::8])
        ax[0].set_xticklabels(ts[::8], fontsize=6)
        ax[0].legend(locations)
        ax[0].set_title('Cloud coverage over time')
        ax[0].set_ylabel('Cloud coverage (%)')

        ax[1].plot(index, wind[1])
        ax[1].set_prop_cycle(color=colours[y])
        ax[1].set_xticks(index[::8])
        ax[1].set_xticklabels(ts[::8], fontsize=6)
        ax[1].legend(locations)
        ax[1].set_title('Wind over time')
        ax[1].set_ylabel('Wind (km/h)')

    html_fig2 = mpld3.fig_to_html(fig2)
    plt.show()

    return html_fig2

plot()
