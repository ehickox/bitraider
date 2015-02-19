import sys
import pytz
import xml.utils.iso8601
import time
import numpy
from datetime import date, datetime, timedelta
from matplotlib import pyplot as plt
from cbexchange import cb_exchange as cb_exchange
from cbexchange import CoinbaseExchangeAuth
from strategy import strategy

class runner():
    """Runner is a customizable CLI dashboard for retrieval of market data, backtesting strategies,and running strategies on live data.
    """
    
    def __init__(self, commands=None, strategy=None):
        """Create a new runner with provided CLI commands. Default commands are:
        \n1. exit: quit autotrader
        \n2. help: display all commands
        \n3. price: display the most recent bitcoin price
        \n4. run: start trading on live data
        \n5. backtest: run a backtest on historic data
        \n6. load: load a new strategy
        """

        # Default Commands
        self.commands = {}
        if commands is not None:
            self.commands += commands
        
        self.commands["exit"] = "Quit Autotrader"
        self.commands["help"] = "Display all commands"
        self.commands["price"] = "Display current bitcoin price"
        self.commands["run"] = "Start trader"
        self.commands["load"] = "Load a new strategy"
        self.commands["backtest"] = "Backtest a strategy with historic data"

        self.auth_file = None
        """Create `auth.txt` to connect to CoinbaseExchange. auth.txt should only contain 3 lines containing your CoinbaseExchange API key, secret, and passphrase on lines 1, 2, and 3 respectively.
        """
        self.exchange = cb_exchange(None, None, None)
        self.accounts = None
        print("Welcome to bitraider v0.0.3, an algorithmic Bitcoin trader")
        print("Attempting to read Coinbase Exchange API key, secret and password, from auth.txt...")
        try:
            self.auth_file = open('auth.txt', 'r')
            self.auth_key = self.auth_file.readline().rstrip()
            self.auth_secret = self.auth_file.readline().rstrip()
            self.auth_password = self.auth_file.readline().rstrip()
            self.exchange = cb_exchange(self.auth_key, self.auth_secret, self.auth_password)
            self.accounts = self.exchange.list_accounts()
            if len(self.accounts) != 0:
                print("Successfully authenticated!")

        except Exception, err:
            print("Error! Only unauthorized endpoints are available.")
            print("error: "+str(err))

        if self.accounts is not None:
            print(str(len(self.accounts))+" accounts were found.")
            for i in range(0, len(self.accounts)):
                print("Account ID: "+str(self.accounts[i]['id'])+" Available Funds: "+str(self.accounts[i]['available'])+" "+str(self.accounts[i]['currency'])+"")

        # Set up strategy
        self.strategies = []
        """The currently loaded strategies"""
        if strategy is not None:
            self.strategies.append(strategy)

    def run(self):
        # Time Configuration
        curr_time = time.time() # Seconds since Jan 1st, 1970
        curr_timezone = pytz.timezone("US/Central")

        input = ""
        print "Type \'help\' to see a list of all possible commands."
        while True:
            input = raw_input("> ")
            if input == "help":
                self.print_all_commands()
            if input == "price":
                self.print_curr_price()
            if input == "run":
                self.set_ticker_on()
            if input == "exit":
                sys.exit()
            if input == "load":
                print("Type the filename (without .py) containing the class which inherits from bitraider.strategy:")
                input = raw_input("> ")
                filename = str(input)
                print("Type the name of the class within "+str(input)+" representing the strategy to load:")
                input = raw_input("> ")
                loaded_strategy = str(input)
                self.load_strategy(filename, loaded_strategy)
            if input == "backtest":
                usd = 1000
                btc = 1
                days_back_in_time = 7
                print("Enter the number of days back in time to backtest on: ")
                input = raw_input("> ")
                if input == "":
                    print("Performing backtest on default of 7 days.")
                else:
                    days_back_in_time = float(input)
                    print("Performing backtest on last "+str(days_back_in_time)+" days.")

                curr_time = datetime.now(tz=curr_timezone)
                start_time = curr_time - timedelta(seconds=86400*days_back_in_time)
                start_time = start_time.isoformat(' ')
                end_time = curr_time.isoformat(' ')
                print("Enter the initial USD amount:")
                input = raw_input("> ")
                if input == "":
                    print("Using default starting USD amount of $1,000")
                else:
                    usd = float(input)
                    print("Using starting USD amount of $"+str(usd))
                
                print("Enter the initial BTC amount:")
                input = raw_input("> ")
                if input == "":
                    print("Using default starting BTC amount of 1")
                else:
                    btc = float(input)
                    print("Using starting BTC amount of "+str(btc))

                historic_data = self.exchange.get_historic_rates(start_time=start_time, end_time=end_time, granularity=self.strategies[0].interval)

                self.strategies[0].backtest_strategy(historic_data=historic_data, start_usd=usd, start_btc=btc,
                        start_time=start_time, end_time=end_time)
    


    def print_curr_price(self):
        """Print the most recent price."""
        print(self.exchange.get_last_trade('BTC-USD')['price'])

    def print_all_commands(self):
        """Print all commands with their descriptions."""
        print('\n'.join(['%s:  %s' % (key, value) for (key, value) in self.commands.items()]))

    def load_strategy(self, module, cls):
        """Load a user-defined strategy from a file.

        \n`module`: the filename in the current directory containing the strategy class which
        inherits from bitraider.strategy (does not include .py)
        \n`cls`: the classname within the file to load
        """
        import_string = module+"."+cls
        _temp = __import__(module)
        loaded_strategy_ = getattr(_temp, cls)
        instance_of_loaded_strategy = loaded_strategy_()
        self.strategies.append(instance_of_loaded_strategy)
        print("Loaded strategy: "+str(cls)+" from file: "+str(module)+".py")
    
def run():
    my_runner = runner()
    my_runner.run()

if __name__=="__main__":
   run() 
