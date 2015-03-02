from strategy import strategy as strategy
from exchange import cb_exchange_sim
import sys

class awesome_strategy(strategy):

    def __init__(self, interval=(60*60), time_from_start=86400, buy_amt=0.001, pivot=0.5):
        self.interval=interval
        self.time_from_start=time_from_start
        self.buy_amt=buy_amt
        self.pivot=pivot
        self.profit_floor = 0.15
        self.exchange = None
        self.has_baseline = False
        self.time_elapsed = 0
        self.baseline = []
        self.weighted_avg = 0
        self.num_above = 0
        self.num_below = 0
        self.purchases = []
        self.times_recalculated = 0

    def trade(self, timeslice):
        self.time_elapsed += self.interval
        timestamp = timeslice[0]
        currprice = timeslice[4]
        self.baseline.append(timeslice)

        # If we've reached the first time_from_start, we have our first baseline
        if self.time_elapsed >= self.time_from_start and not self.has_baseline:
            # Calculate data and reset baseline
            self.weighted_avg, self.num_above, self.num_below = strategy.calculate_historic_data(self.baseline, currprice)
            self.baseline = []
            self.has_baseline = True

        if self.has_baseline:
            # If we have a baseline, we can do some trading
            if self.num_below + self.num_above != 0:
                self.percent_above = self.num_above/(self.num_above+self.num_below)
            else:
                self.percent_above = 0

            self.perc_currprice_from_avg = (currprice-self.weighted_avg)/self.weighted_avg
            if currprice < self.weighted_avg and self.percent_above >= self.pivot:
                # If the current price is below average and there is at least pivot% traded above average
                if self.exchange.usd_bal >= self.buy_amt*currprice:
                    self.exchange.place_order(currprice, self.buy_amt, 'buy', 'BTC-USD', historic_timeslice=timeslice)
                    self.purchases.append((currprice, self.buy_amt))

            # Go through all previous purchases, and sell if a profit can be made
            # purchases is a list of tuple a la (price, amount)
            if len(self.purchases) != 0:
                for purchase in self.purchases[:]:
                    perc_currprice_from_purch = (currprice-purchase[0])/purchase[0]
                    value_now = purchase[1]*currprice
                    value_then = purchase[1]*purchase[0]
                    profit = value_now - value_then
                    if profit > self.profit_floor: # TODO: account for fees as well
                        self.exchange.place_order(currprice, purchase[1], 'sell', 'BTC-USD', historic_timeslice=timeslice)
                        self.purchases.remove(purchase)

            if self.time_elapsed > self.time_from_start*(self.times_recalculated)+self.time_from_start:
                # Time to recalculate the data and reset our baseline
                # recalculate avg
                self.times_recalculated += 1
                if len(self.baseline) > 1:
                    #print("\nRecalculating data")
                    self.weighted_avg, self.num_above, self.num_below = strategy.calculate_historic_data(self.baseline, currprice)
                    self.baseline = []
        return
