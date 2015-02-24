import sys
import pytz
import time
import calendar
import ConfigParser
from datetime import date, datetime, timedelta
from strategy import strategy
from exchange import cb_exchange_sim, cb_exchange

class runner():
    """Runner is a customizable CLI dashboard for retrieval of market data, backtesting strategies, and running strategies on live data."""

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
        self.commands["list"] = "List all currently loaded strategies" # TODO: implement
        self.commands["backtest"] = "Backtest a strategy with historic data"
        self.commands["config"] = "Run through the bitraider configuration flow"

        # Init config
        self.config_path = "settings.ini"
        self.config = ConfigParser.ConfigParser()
        try:
            self.config.read(self.config_path)
        except Exception, err:
            print(str(err))

        print("Welcome to bitraider v0.0.3, an algorithmic Bitcoin trader")

        # Set up strategy
        self.strategies = []
        """The currently loaded strategies"""
        if strategy is not None:
            self.strategies.append(strategy)

        try:
            print("Attempting to load default strategy...")
            default_strategy_module = self.config.get("default_strategy", "module")
            default_strategy_class = self.config.get("default_strategy", "class")
            self.load_strategy(default_strategy_module, default_strategy_class)
        except Exception, err:
            print(str(err))
            print("No default strategy configured. Run "
                    "\'config\' > \'default strategy\' to set one")

        self.exchange = cb_exchange_sim(1000, 1)
        self.accounts = None

        # Get auth credentials from settings.ini, if they exist, authorize
        print("Attempting to read Coinbase Exchange API key, secret and password, from settings.ini...")
        try:
            self.auth_key = self.config.get("auth", "key")
            self.auth_secret = self.config.get("auth", "secret")
            self.auth_password = self.config.get("auth", "password")
            self.authenticate()
        except Exception, err:
            print(str(err))


        if self.accounts is not None:
            print(str(len(self.accounts))+" accounts were found.")
            for i in range(0, len(self.accounts)):
                try:
                    print("Account ID: "+str(self.accounts[i]['id'])+" Available Funds: "+str(self.accounts[i]['available'])+" "+str(self.accounts[i]['currency'])+"")
                except Exception, err:
                    print("Something went wrong while trying to authenticate with the provided credentials. Try running config>auth again.")


    def authenticate(self):
        try:
            self.exchange = cb_exchange(self.auth_key, self.auth_secret, self.auth_password)
            self.accounts = self.exchange.list_accounts()

        except Exception, err:
            print("Error! Only unauthorized endpoints are available.")
            print("error: "+str(err))
            print("If you would like bitraider to walk you through authentication, enter the commands: \'config\' > \'auth\'")

    def set_ticker_on(self):
        strategy = self.strategies[0]
        start_time = time.time()
        lower_bound = start_time
        upper_bound = start_time + strategy.interval
        elapsed_time = 0.0
        last_intervals_trades = []
        while True:
            curr_time = time.time()
            elapsed_time = curr_time - start_time
            if elapsed_time % strategy.interval == 0:
                # if we've reached a new interval, calculate data for the last interval and pass
                # it onto the strategy
                latest_trades = self.exchange.get_trades('BTC-USD')
                interval_data = []
                last_intervals_low = 999999999
                last_intervals_high = 0.0
                last_intervals_close = 0.0
                last_intervals_close = 0.0
                last_intervals_volume = 0.0
                for trade in latest_trades:
                    # starting with the most recent trade, get trades for the last interval
                    datestring = str(trade.get("time"))[:-3]
                    trade_time = float(calendar.timegm(datetime.strptime(datestring, "%Y-%m-%d %H:%M:%S.%f").timetuple()))
                    if trade_time >= lower_bound and trade_time <= upper_bound:
                        last_intervals_trades.append(trade)
                        if float(trade.get('price')) > last_intervals_high:
                            last_intervals_high = float(trade.get('price'))
                        if float(trade.get('price')) < last_intervals_low:
                            last_intervals_low = float(trade.get('price'))
                        last_intervals_volume += float(trade.get('size'))
                if len(last_intervals_trades) > 0:
                    last_intervals_close = float(last_intervals_trades[0].get('price'))
                    last_intervals_open = float(last_intervals_trades[-1].get('price'))
                    interval_start_time = curr_time - strategy.interval
                    interval_data.extend([interval_start_time, last_intervals_low, last_intervals_high,
                    last_intervals_open, last_intervals_close, last_intervals_volume])
                print("last_intervals_trades: "+str(last_intervals_trades))
                print("elapsed: "+str(elapsed_time))
                last_intervals_trades = []
                lower_bound += strategy.interval
                upper_bound += strategy.interval

                # Here's where the magic happens:
                #strategy.trade(interval_data)

    def run(self):
        # Time Configuration
        curr_time = time.time() # Seconds since Jan 1st, 1970
        curr_timezone = pytz.timezone("US/Central")

        input = ""
        print "Type \'help\' to see a list of all possible commands."
        while True:
            input = raw_input("> ")
            if input not in self.commands.keys():
                print("Error: unrecognized command. Type \'help\' to"
                        " see a list of all commands."
            if input == "help":
                self.print_all_commands()
            if input == "price":
                self.print_curr_price()
            if input == "run":
                self.set_ticker_on()
            if input == "exit":
                sys.exit()
            if input == "config":
                print("Enter in the property you would like to configure:")
                input = raw_input("> ")
                if input == "auth":
                    if self.accounts is not None:
                        print("Are you sure? Reconfiguring auth will wipe your current auth settings. [y/n]")
                        input = raw_input("> ")
                        if input == "y":
                            print("Paste in your CoinbaseExchange API key:")
                            input = raw_input("> ")
                            self.auth_key = input
                            print("Paste in your CoinbaseExchange API secret:")
                            input = raw_input("> ")
                            self.auth_secret = input
                            print("Paste in your CoinbaseExchange API passphrase:")
                            input = raw_input("> ")
                            if input is not "":
                                self.auth_password = input
                                self.config.set("auth", "key", self.auth_key)
                                self.config.set("auth", "secret", self.auth_secret)
                                self.config.set("auth", "password", self.auth_password)
                                with open(self.config_path, "wb") as config_file:
                                    self.config.write(config_file)
                                self.authenticate()
                        elif input == "n":
                            print("Exiting to main menu")
                            pass
                    else:
                        print("Paste in your CoinbaseExchange API key:")
                        input = raw_input("> ")
                        self.auth_key = input
                        print("Paste in your CoinbaseExchange API secret:")
                        input = raw_input("> ")
                        self.auth_secret = input
                        print("Paste in your CoinbaseExchange API passphrase:")
                        input = raw_input("> ")
                        self.auth_password = input
                        self.config.set("auth", "key", self.auth_key)
                        self.config.set("auth", "secret", self.auth_secret)
                        self.config.set("auth", "password", self.auth_password)
                        with open(self.config_path, "wb") as config_file:
                            self.config.write(config_file)
                        self.authenticate()
                elif input == "default strategy":
                    print("Type the filename (without .py) containing the class which inherits from bitraider.strategy:")
                    input = raw_input("> ")
                    filename = str(input)
                    self.config.set("default_strategy", "module", filename)
                    print("Type the name of the class within "+str(input)+" representing the strategy to load:")
                    input = raw_input("> ")
                    loaded_strategy = str(input)
                    self.config.set("default_strategy", "class", loaded_strategy)
                    with open(self.config_path, "wb") as config_file:
                        self.config.write(config_file)
                    self.load_strategy(filename, loaded_strategy)

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

                self.strategies[0].exchange = cb_exchange_sim(start_usd=usd, start_btc=btc)
                historic_data = self.strategies[0].exchange.get_historic_rates(start_time=start_time, end_time=end_time, granularity=self.strategies[0].interval)
                if type(historic_data) is not list:
                    print("API error: "+str(historic_data.get("message", "")))
                    print("Unable to backtest")
                    pass
                else:
                    print("Backtesting from "+str(start_time)+" to "+str(end_time))
                    print("with "+str(len(historic_data))+" timeslices of length "+str(self.strategies[0].interval)+" seconds each")
                    self.strategies[0].backtest_strategy(historic_data)

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
