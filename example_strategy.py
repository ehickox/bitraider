from strategy import strategy as strategy

class awesome_strategy(strategy):

    def __init__(self, interval=5, time_from_start=86400, buy_amt=0.001, pivot=0.5):
        self.interval=interval
        self.time_from_start=time_from_start
        self.buy_amt=buy_amt
        self.pivot=pivot


    def backtest_strategy(self, historic_data, start_btc, start_usd, start_time, end_time):
        """Returns performance of a strategy vs market performance.
        
        start_btc -- the starting amount of BTC for the hypothetical account
        start_usd -- the starting amount of USD for the hypothetical account
        start_time -- ISO8601 formated time representing the earliest time to look at
        end_time -- ISO8601 formated time representing the latest time to look at
        """
        print("Backtesting strategy... this may take some time.")
        # Reverse the data since Coinbase returns it in reverse chronological
        # now historic_data strarts with the oldest entry
        historic_data = list(reversed(historic_data))
        earliest_time = float(historic_data[0][0])
        latest_time = float(historic_data[-1][0])
        start_price = float(historic_data[0][4])
        end_price = float(historic_data[-1][4])
        market_performance = ((end_price-start_price)/start_price)*100
        usd_bal = start_usd
        btc_bal = start_btc
        baseline_idx = 0
        data_to_test = []
        prev_idx = 0
        purchases = []
        weighted_avg, num_above, num_below = 0, 0, 0
        # Calculate initial data
        time_elapsed = 0
        print("Initializing...")
        for timeslice in historic_data:
            idx = historic_data.index(timeslice)
            timeslice = [float(i) for i in timeslice]
            timestamp = float(timeslice[0])
            currprice = float(timeslice[4])
            time_elapsed = timestamp-earliest_time
            if time_elapsed >= self.time_from_start:
                baseline = historic_data[:idx]
                baseline_idx = idx
                prev_idx = idx
                weighted_avg, num_above, num_below = strategy.calculate_historic_data(baseline, currprice)
                data_to_test = historic_data[prev_idx:]
                break

        time_elapsed = 0
        times_recalculated = 0
        times_bought = 0
        times_sold = 0
        # After initial data is calculated, run the simulation with the given strategy
        print("Initialization complete. Running backtest...")
        for timeslice in data_to_test:
            idx = data_to_test.index(timeslice)
            percent = (float(idx)/float(len(data_to_test)))*100 + 1
            sys.stdout.write("\r%d%%" % percent)
            sys.stdout.flush()  
            timeslice = [float(i) for i in timeslice]
            timestamp = float(timeslice[0])
            currprice = float(timeslice[4])
            if num_below+num_above != 0:
                percent_above = num_above/(num_above+num_below)
            else:
                percent_above = 0

            perc_currprice_from_avg = (currprice-weighted_avg)/weighted_avg
            if currprice < weighted_avg and percent_above >= self.pivot:
                # If the current price is below average and there is at least pivot% traded above average 
                if usd_bal >= self.buy_amt*currprice:
                    usd_bal -= self.buy_amt*currprice
                    btc_bal += self.buy_amt
                    purchases.append((currprice, self.buy_amt))
                    times_bought += 1
            
            # Go through all previous purchases, and sell if a profit can be made 
            # purchases is a list of tuple a la (price, amount)
            if len(purchases) != 0:
                for purchase in purchases[:]:
                    perc_currprice_from_purch = (currprice-purchase[0])/purchase[0]
                    value_now = purchase[1]*currprice
                    value_then = purchase[1]*purchase[0]
                    profit = value_now - value_then
                    if profit > 0: # TODO: account for fees as well
                        usd_bal += currprice*purchase[1]
                        btc_bal -= purchase[1]
                        purchases.remove(purchase)
                        times_sold += 1

            time_elapsed = timestamp-earliest_time
            if time_elapsed > self.time_from_start*(times_recalculated)+self.time_from_start:
                # recalculate avg
                times_recalculated += 1
                baseline = data_to_test[prev_idx:idx]
                prev_idx = idx
                if len(baseline) > 1:
                    #print("\nRecalculating data")
                    weighted_avg, num_above, num_below = strategy.calculate_historic_data(baseline, currprice)

        # Calculate performance
        start_amt = (float(start_usd)/float(end_price)) + float(start_btc)
        end_amt = (float(usd_bal)/float(end_price)) + float(btc_bal)
        strategy_performance = ((end_amt-start_amt)/start_amt)*100
        print("\n")
        print("Times recalculated: "+str(times_recalculated))
        print("Times bought: "+str(times_bought))
        print("Times sold: "+str(times_sold))
        print("Purchases left: "+str(len(purchases)*self.buy_amt)+" BTC")
        print("The Market's performance: "+str(market_performance)+" %")
        print("Strategy's performance: "+str(strategy_performance)+" %")
        print("Account's ending value if no trades were made: "+str(start_amt)+" BTC")
        print("Account's ending value with this strategy: "+str(end_amt)+" BTC")
        strategy_performance_vs_market = strategy_performance - market_performance
        if strategy_performance > market_performance:
            print("Congratulations! This strategy has beat the market by: "+str(strategy_performance_vs_market)+" %")
        elif strategy_performance < market_performance:
            print("This strategy has preformed: "+str(strategy_performance_vs_market)+" % worse than market.")

        return strategy_performance_vs_market, strategy_performance, market_performance
