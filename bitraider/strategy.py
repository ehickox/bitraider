import sys
import pytz
import time
import numpy
from datetime import date, datetime, timedelta
#from matplotlib import pyplot as plt
from exchange import cb_exchange as cb_exchange
from exchange import CoinbaseExchangeAuth
from abc import ABCMeta, abstractmethod

class strategy(object):
    """`strategy` defines an abstract base strategy class. Minimum required to create a strategy is a file with a class which inherits from strategy containing a backtest_strategy function. As a bonus, strategy includes utility functions like calculate_historic_data.

    """
    __metaclass__ = ABCMeta

    def __init__(name="default name", interval=5):
        """Constructor for an abstract strategy. You can modify it as needed.

        \n`interval`: a.k.a timeslice the amount of time in seconds for each 'tick' default is 5
        \n`name`: a string name for the strategy
        """
        self.name = name
        self.interval = interval
        self.times_recalculated = 0

    @abstractmethod
    def trade(self, timeslice):
        """Perform operations on a timeslice.

        \n`timeslice`: a section of trade data with time length equal to the strategy's interval, formatted as follows:
        \n[time, low, high, open, close, volume]
        """
        return

    def backtest_strategy(self, historic_data, verbose=True):
        """Returns performance of a strategy vs market performance.
        """
        # Reverse the data since Coinbase returns it in reverse chronological
        # now historic_data strarts with the oldest entry
        historic_data = list(reversed(historic_data))
        earliest_time = float(historic_data[0][0])
        latest_time = float(historic_data[-1][0])
        start_price = float(historic_data[0][4])
        end_price = float(historic_data[-1][4])
        market_performance = ((end_price-start_price)/start_price)*100

        if verbose:
            print("Running simulation on historic data. This may take some time....")

        for timeslice in historic_data:
            # Display what percent through the data we are
            if verbose:
                idx = historic_data.index(timeslice)
                percent = (float(idx)/float(len(historic_data)))*100 + 1
                sys.stdout.write("\r%d%%" % percent)
                sys.stdout.flush()

            self.trade(timeslice)

        # Calculate performance
        end_amt_no_trades = (float(self.exchange.start_usd)/float(end_price)) + float(self.exchange.start_btc)
        end_amt = (float(self.exchange.usd_bal)/float(end_price)) + float(self.exchange.btc_bal)
        start_amt = (float(self.exchange.start_usd)/float(start_price)) + float(self.exchange.start_btc)
        strategy_performance = ((end_amt-start_amt)/start_amt)*100
        strategy_performance_vs_market = strategy_performance - market_performance
        if verbose:
            print("\n")
            print("Times recalculated: "+str(self.times_recalculated))
            print("Times bought: "+str(self.exchange.times_bought))
            print("Times sold: "+str(self.exchange.times_sold))
            print("The Market's performance: "+str(market_performance)+" %")
            print("Strategy's performance: "+str(strategy_performance)+" %")
            print("Account's ending value if no trades were made: "+str(end_amt_no_trades)+" BTC")
            print("Account's ending value with this strategy: "+str(end_amt)+" BTC")
            if strategy_performance > market_performance:
                print("Congratulations! This strategy has beat the market by: "+str(strategy_performance_vs_market)+" %")
            elif strategy_performance < market_performance:
                print("This strategy has preformed: "+str(strategy_performance_vs_market)+" % worse than market.")

        return strategy_performance_vs_market, strategy_performance, market_performance

    @staticmethod
    def calculate_historic_data(data, pivot):
        """Returns average price weighted according to volume, and the number of bitcoins traded
            above and below a price point, called a pivot.\n

        \n`pivot`: the price used for returning volume above and below
        \n`data`: a list of lists formated as follows [time, low, high, open, close]
        \n[
            \n\t["2014-11-07 22:19:28.578544+00", "0.32", "4.2", "0.35", "4.2", "12.3"],
                \n\t\t...
        \n]
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
