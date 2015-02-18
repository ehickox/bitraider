import sys
import pytz
import xml.utils.iso8601
import time
import numpy
from datetime import date, datetime, timedelta
from matplotlib import pyplot as plt
from cbexchange import cb_exchange as cb_exchange
from cbexchange import CoinbaseExchangeAuth

class strategy():
    
    def __init__(name="default name", interval=5):
        """Constructor for an abstract strategy. Minimum required to create a strategy is
        a file with a class which inherits from strategy containing a backtest_strategy function.
        As a bonus, strategy includes utility functions like calculate_historic_data.

        interval -- the amount of time in seconds for each 'tick' default is 5
        name -- a string name for the strategy
        """
        self.name = name
        self.interval = interval

    @staticmethod
    def calculate_historic_data(data, pivot):
        """Returns average price weighted according to volume, and the number of bitcoins traded
            above and below a price point, called a pivot.
        
        pivot -- the price used for returning volume above and below
        data -- a list of lists formated as follows [time, low, high, open, close]
        [
            ["2014-11-07 22:19:28.578544+00", "0.32", "4.2", "0.35", "4.2", "12.3"],
                ...
        ] 

        """
        price_list = []
        weights = []
        if data is None:
            pass
        min_price = float(data[0][1])
        max_price = float(data[0][2])
        discrete_prices = {}
        for timeslice in data:
            timeslice = [float(i) for i in timeslice]
            if max_price < timeslice[2]:
                max_prie = timeslice[2]
            if min_price > timeslice[1]:
                min_price = timeslice[1]
            
            closing_price = timeslice[4]
            volume = timeslice[5]
            if closing_price not in discrete_prices.keys():
                discrete_prices[str(closing_price)] = volume
            else:
                discrete[str(closing_price)] += volume

            idx = data.index(timeslice)
            price_list.append(closing_price)
            weights.append(volume)

        fltprices = [float(i) for i in discrete_prices.keys()]
        fltvolumes = [float(i) for i in discrete_prices.values()]
        np_discrete_prices = numpy.array(fltprices)
        np_volume_per_price = numpy.array(fltvolumes) 
        weighted_avg = numpy.average(np_discrete_prices, weights=np_volume_per_price)
        num_above = 0
        num_below = 0
        num_at = 0
        for key in discrete_prices.keys():
            value = discrete_prices[key]
            if float(key) > pivot:
                num_above+=value
            elif float(key) < pivot:
                num_below+=value
            elif float(key) == pivot:
                num_at+=value

        total_volume = 0.0
        for volume in fltvolumes:
            total_volume+=volume
        fltprops = []
        for volume in fltvolumes:
            fltprops.append((volume/total_volume))
        #print("num_below: "+str(num_below))
        #print("num_above: "+str(num_above))
        #print("num_at: "+str(num_at))
        #print("weighted_average: "+str(weighted_avg))

        #plt.title("Price distribution")
        #plt.xlabel("Price (USD)")
        #plt.ylabel("Volume")
        #plt.bar(fltprices, fltprops)
        #plt.show()
        return weighted_avg, num_above, num_below
