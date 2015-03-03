import sys
import pytz
import time
import calendar
import ConfigParser
import cmd
import itertools
import smtplib
import random
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from datetime import date, datetime, timedelta
from strategy import strategy
from exchange import cb_exchange_sim, cb_exchange

class runner(cmd.Cmd):

    def __init__(self):

        print("    __    _ __             _     __         ")
        print("   / /_  (_) /__________ _(_)___/ /__  _____")
        print("  / __ \/ / __/ ___/ __ `/ / __  / _ \/ ___/")
        print(" / /_/ / / /_/ /  / /_/ / / /_/ /  __/ /    ")
        print("/_.___/_/\__/_/   \__,_/_/\__,_/\___/_/     ")
        print("")
        print("Welcome to bitraider v0.0.4, an algorithmic Bitcoin trader!")

        cmd.Cmd.__init__(self)
        self.prompt = '> '
        self.intro = "Type a command to get started or type \'help\'"


        # Init config
        self.config_path = "settings.ini"
        self.config = ConfigParser.ConfigParser()
        try:
            self.config.read(self.config_path)
        except Exception, err:
            print(str(err))

        # Set up strategy
        self.strategies = {}
        """The currently loaded strategies with key:classname,
        value:instance of strategy"""

        # Try to load a default strategy, if one exists
        try:
            default_strategy_module = self.config.get("default_strategy", "module")
            default_strategy_class = self.config.get("default_strategy", "class")
            self.load_strategy(default_strategy_module, default_strategy_class)
        except Exception, err:
            #print(str(err))
            print("No default strategy configured. Run "
                    "\'config default\' to set one")
            try:
                self.config.add_section("default_strategy")
            except:
                pass

        self.exchange = cb_exchange_sim(1000, 1)
        self.accounts = None

        # Get auth credentials from settings.ini, if they exist, authorize
        try:
            self.auth_key = self.config.get("auth", "key")
            self.auth_secret = self.config.get("auth", "secret")
            self.auth_password = self.config.get("auth", "password")
            self.authenticate()
        except Exception, err:
            #print(str(err))
            print("No authentication configured. Run "
                    "\'config auth\' to set it")
            try:
                self.config.add_section("auth")
            except:
                pass

        if self.accounts is not None:
            print(str(len(self.accounts))+" account(s) were found.")
            for i in range(0, len(self.accounts)):
                try:
                    print("Account ID: "+str(self.accounts[i]['id'])+" Available Funds: "+str(self.accounts[i]['available'])+" "+str(self.accounts[i]['currency'])+"")
                except Exception, err:
                    print("Something went wrong while trying to authenticate \nwith the provided credentials. Try running \'config auth\' again.")

        # Default number of folds:
        self.num_folds = 1
        # Try to load optimization and cross-validation settings
        try:
            self.num_folds = int(self.config.get("optimize", "folds"))
        except Exception, err:
            #print(str(err))
            print("No optimization settings found. Run "
                    "\'config optimize\' to set them")
            try:
                self.config.add_section("optimize")
            except:
                pass

        # Try to load emailer settings
        self.email = False
        try:
            self.email_server = smtplib.SMTP('smtp.gmail.com:587')
            self.email_user = self.config.get("email", "username")
            self.email_pass = self.config.get("email", "password")
            self.email_dest = self.config.get("email", "destination")
            self.email_server.ehlo()
            self.email_server.starttls()
            self.email_server.login(self.email_user, self.email_pass)
            self.email_server.quit()
            self.email = True
        except Exception, err:
            #print(str(err))
            print("No emailer settings found. Run "
                    "\'config email\' to set them")
            try:
                self.config.add_section("email")
            except:
                pass

    def do_exit(self, line):
        """Quit bitraider"""
        sys.exit()

    def do_price(self, line):
        """Prints the most recent bitcoin price"""
        self.print_curr_price()

    def do_run(self, line):
        """Start a real live trading session"""
        self.set_ticker_on()

    def do_list(self, line):
        """Display all currently loaded strategies"""
        self.list_strategies()

    def do_config(self, option):
        """usage: \'config \' [option]"""

        if option == "":
            print("error: no cofiguration option specified")
        else:
            if option == "auth":
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

            elif option == "default":
                print("Type the filename (without .py) containing the class which inherits from bitraider.strategy:")
                option = raw_input("> ")
                filename = str(option)
                self.config.set("default_strategy", "module", filename)
                print("Type the name of the class within "+str(option)+" representing the strategy to load:")
                option = raw_input("> ")
                loaded_strategy = str(option)
                if self.strategies is not None:
                    if loaded_strategy in self.strategies.keys():
                        print("Error: "+loaded_strategy+" is already loaded")
                        option = raw_input("> ")
                        loaded_strategy = str(option)

                self.config.set("default_strategy", "class", loaded_strategy)
                with open(self.config_path, "wb") as config_file:
                    self.config.write(config_file)
                self.load_strategy(filename, loaded_strategy)

            elif option == "optimize":
                print("Type the number of folds to be used for cross-validation:")
                option = raw_input("> ")
                self.num_folds = int(option)
                self.config.set("optimize", "folds", self.num_folds)
                with open(self.config_path, "wb") as config_file:
                    self.config.write(config_file)

            elif option == "email":
                print("Type your gmail email: ")
                option = raw_input("> ")
                self.email_user = str(option)
                self.config.set("email", "username", self.email_user)
                print("Type your gmail password: ")
                option = raw_input("> ")
                self.email_pass = str(option)
                self.email_server = smtplib.SMTP('smtp.gmail.com:587')
                self.config.set("email", "password", self.email_pass)
                try:
                    self.email_server.ehlo()
                    self.email_server.starttls()
                    self.email_server.login(self.email_user, self.email_pass)
                    self.email_server.quit()
                except Exception, err:
                    print(str(err))
                    print("Something went wrong while logging in using the provided "
                            "credentials. Try again.")
                    return
                print("Type the destination email: ")
                option = raw_input("> ")
                self.email_dest = str(option)
                self.config.set("email", "destination", self.email_dest)
                self.email = True
                print("bitraider will now email helpful updates regarding data it is processing")
                with open(self.config_path, "wb") as config_file:
                    self.config.write(config_file)


    def do_load(self, option):
        """Load a strategy"""
        print("Type the filename (without .py) containing the class which inherits from bitraider.strategy:")
        input = raw_input("> ")
        filename = str(input)
        print("Type the name of the class within "+str(input)+" representing the strategy to load:")
        input = raw_input("> ")
        loaded_strategy = str(input)
        self.load_strategy(filename, loaded_strategy)

    def do_backtest(self, option):
        """Performs a single fold backtest"""

        strategy_to_backtest = ""
        print("Enter the class name of the strategy to backtest, or press enter to\n"
                "backtest on the default strategy.")
        input = raw_input("> ")
        if input == "":
            print("Performing backest on default strategy: "+str(self.config.get("default_strategy" ,"class")))
            strategy_to_backtest = str(self.config.get("default_strategy", "class"))
        else:
            strategy_to_backtest = str(input)

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

        curr_time = datetime.now(tz=self.curr_timezone)
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

        if strategy_to_backtest is not "":
            self.strategies[strategy_to_backtest].exchange = cb_exchange_sim(start_usd=usd, start_btc=btc)
            historic_data = self.strategies[strategy_to_backtest].exchange.get_historic_rates(start_time=start_time, end_time=end_time, granularity=self.strategies[strategy_to_backtest].interval)
            if type(historic_data) is not list:
                print("API error: "+str(historic_data.get("message", "")))
                print("Unable to backtest")
                pass
            else:
                print("Backtesting from "+str(start_time)+" to "+str(end_time))
                print("with "+str(len(historic_data))+" timeslices of length "+str(self.strategies[strategy_to_backtest].interval)+" seconds each")
                self.strategies[strategy_to_backtest].backtest_strategy(historic_data)

    def do_optimize(self, line):
        """Finds the best possible constant values for a strategy"""

        print("WARNING: Optimization can take a LONG time i.e. days or more")
        print("Computational complexity is O(n^a) n = granularity, a = num values "
                "to optimize.")
        usd = 1000
        btc = 1
        days_back_in_time = 7
        print("Enter the class name of the strategy to be optimized:")
        input = raw_input("> ")
        if input not in self.strategies.keys():
            print("Error: not found. Exiting to main menu")
            return
        strategy_to_optimize = input
        strategy = strategy_to_optimize

        print("Enter the timeframe to optimize for i.e. the time to simulate over:")
        print("Current cross-validation settings are set for: "+str(self.num_folds)+" fold(s)")
        days_back_in_time = 7
        input = raw_input("> ")
        if input == "":
            print("Performing optimization for default of 7 days.")
        else:
            days_back_in_time = float(input)
            print("Performing optimization based on  "+str(days_back_in_time)+" days.")

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

        self.strategies[strategy].exchange = cb_exchange_sim(start_usd=usd, start_btc=btc)
        historic_data = []
        curr_time = datetime.now(tz=self.curr_timezone)

        print("Pulling historical data from exchange...")

        for fold in range(self.num_folds):
            start_time_sec = curr_time - timedelta(seconds=86400*days_back_in_time)
            start_time = start_time_sec.isoformat(' ')
            end_time = curr_time.isoformat(' ')
            curr_time = start_time_sec
            fold_data = self.strategies[strategy].exchange.get_historic_rates(start_time=start_time, end_time=end_time, granularity=self.strategies[strategy].interval)
            # Sleep between 1 and 3 seconds to lighten load on exchange API
            time.sleep(random.randint(1, 3))
            if type(fold_data) is not list:
                print("API error: "+str(fold_data.get("message", "")))
                print("Unable to optimize. Try changing strategy's interval")
                pass
            else:
                print("Optimizing fold #"+str(fold)+" based on time frame from \n"+str(start_time)+" to "+str(end_time))
                print("with "+str(len(fold_data))+" timeslices of length "+str(self.strategies[strategy].interval)+" seconds each\n")
                historic_data.append(fold_data)

        strategy_attributes = dir(self.strategies[strategy])
        bounds_by_attribute = {}
        print("Note: strategy interval cannot be optimized due to API restraints")

        for attribute in strategy_attributes:
            if "__" not in str(attribute) and "_abc" not in str(attribute) and str(attribute) != "interval":
                # Optimizing for interval would poll API too frequently
                print("Enter the lower bound for attribute: "+str(attribute)+", or press enter to skip:")
                input = raw_input("> ")
                if input == "":
                    pass
                else:
                    lower_bound = float(input)
                    print("Enter the upper bound for attribute: "+str(attribute)+":")
                    input = raw_input("> ")
                    upper_bound = float(input)
                    print("Enter the granularity of this attribute i.e. how many different values to try:")
                    input = raw_input("> ")
                    granularity = float(input)
                    if upper_bound is not None and lower_bound is not None:
                        bounds_by_attribute[str(attribute)] = {"lower":lower_bound, "upper":upper_bound, "granularity":granularity}
                        #self.strategies[strategy][attribute] = float(lower_bound)

        possible_vals_by_attr = {}
        attribute_vals_by_id = {}
        config_id = 0
        # Initialize attribute_vals_by id
        for attribute in bounds_by_attribute.keys():
            upper_bound = bounds_by_attribute[attribute]["upper"]
            lower_bound = bounds_by_attribute[attribute]["lower"]
            num_shades_of_attr = int(bounds_by_attribute[attribute].get("granularity"))
            increment = (float(upper_bound) - float(lower_bound))/num_shades_of_attr
            if attribute not in possible_vals_by_attr.keys():
                possible_vals_by_attr[attribute] = []
                for shade in range(num_shades_of_attr):
                    attr_val = float(lower_bound) + (shade*increment)
                    possible_vals_by_attr[attribute].append(attr_val)

        all_possible_configs = list(self.combinations(possible_vals_by_attr))
        config_id = 0
        for config in all_possible_configs:
            attribute_vals_by_id[str(config_id)] = config
            config_id += 1

        performance_by_id_by_fold = {}
        mkt_perf_by_fold_id = {}
        performance_vs_mkt = 0
        strategy_performance = 0
        mkt_performance = 0
        for fold in historic_data:
            # Change the attribute values for this strategy, updating when the performance is highest
            fold_id = str(historic_data.index(fold))
            print("\nOptimizing on fold #"+fold_id)
            if self.email == True:
                # Email when starting a new fold
                subject = "bitraider has begun a new fold."
                body = "bitraider has started processing fold #"+fold_id
                self.send_email(self.email_user, self.email_dest, subject, body)
            performance_by_id_by_fold[fold_id] = {}
            idx = 0
            for configuration in attribute_vals_by_id.keys():
                #print("Backtesting with strategy configuration #"+configuration+": "+str(attribute_vals_by_id[configuration]))

                percent = (float(idx)/float(len(attribute_vals_by_id)))*100 + 1
                sys.stdout.write("\r%d%%" % percent)
                sys.stdout.flush()
                idx += 1
                self.load_strategy(self.module, strategy, verbose=False)
                self.strategies[strategy].exchange = cb_exchange_sim(start_usd=usd, start_btc=btc)
                for attribute in attribute_vals_by_id[configuration]:
                    setattr(self.strategies[strategy], attribute, attribute_vals_by_id[configuration][attribute])
                # Once all the attributes are set, perform backtest for this config
                performance_vs_mkt, strategy_performance, mkt_performance = self.strategies[strategy].backtest_strategy(fold, verbose=False)
                performance_by_id_by_fold[fold_id][str(configuration)] = strategy_performance
                mkt_perf_by_fold_id[fold_id] = mkt_performance

        print("\n")

        # Find the best config in each fold, then average the attribute values
        fold_bests = {}
        for fold_id in performance_by_id_by_fold.keys():
            best_config = "0"
            for config in performance_by_id_by_fold[fold_id]:
                if performance_by_id_by_fold[fold_id][config] > performance_by_id_by_fold[fold_id][best_config]:
                    best_config = config
                    fold_bests[fold_id] = best_config

        totals = {}
        for fold_id in fold_bests.keys():
            for attr in attribute_vals_by_id[fold_bests[fold_id]].keys():
                value = attribute_vals_by_id[fold_bests[fold_id]][attr]
                if attr not in totals.keys():
                    totals[attr] = value
                else:
                    totals[attr] += value

        averages = totals
        for key in totals.keys():
            value = totals[key]
            averages[key] = value/self.num_folds

        # Email when done
        if self.email == True:
            subject = "bitraider has finished optimizing "+strategy
            body = "Here are the best configs with their performances from each fold: \n"
            for fold_id in fold_bests.keys():
                body += "Fold #"+str(fold_id)
                body += "Config: "+str(attribute_vals_by_id[fold_bests[fold_id]])+"\n"
                body += "Strategy performance: "+str(performance_by_id_by_fold[fold_id][fold_bests[fold_id]])+"\n"
                body += "Market performance: "+str(mkt_perf_by_fold_id[fold_id])+"\n"
            body += "The optimized configuration is: "+str(averages)+"\n"
            self.send_email(self.email_user, self.email_dest, subject, body)

        print("Here are the best configs with their performances from each fold: ")
        for fold_id in fold_bests.keys():
            print("Config: "+str(attribute_vals_by_id[fold_bests[fold_id]]))
            print("Strategy performance: "+str(performance_by_id_by_fold[fold_id][fold_bests[fold_id]]))
            print("Market performance: "+str(mkt_perf_by_fold_id[fold_id]))
        print("The best performing strategy configuration is: "+str(averages))
        #print("With a performance vs market of: "+str(performance_by_id[best_config]))

    # End python cmd funtions

    def send_email(self, fromaddr, toaddr, subject="bitraider", body=""):
        """Helper function to send an email"""
        body += "\nThis is an automated email sent by bitraider"
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        text = msg.as_string()
        try:
            self.email_server = smtplib.SMTP('smtp.gmail.com:587')
            self.email_server.ehlo()
            self.email_server.starttls()
            self.email_server.login(self.email_user, self.email_pass)
            self.email_server.sendmail(fromaddr, toaddr, text)
            self.email_server.quit()
        except Exception, err:
            print("error: email failed")
            print(str(err))

    def combinations(self, dicts):
        """Helper function to find all possible combinations of strategy parameters"""
        return (dict(itertools.izip(dicts, x)) for x in itertools.product(*dicts.itervalues()))

    def authenticate(self):
        """Attempts to authenticate using the credentials on the runner object"""
        try:
            self.exchange = cb_exchange(self.auth_key, self.auth_secret, self.auth_password)
            self.accounts = self.exchange.list_accounts()

        except Exception, err:
            print("Error! Only unauthorized endpoints are available.")
            print("error: "+str(err))
            print("If you would like bitraider to walk you through authentication, enter the commands: \'config\' > \'auth\'")


    def set_ticker_on(self):
        """Initiate a real, live trading session"""
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
        """Initiates the CLI prompt"""
        # Time Configuration
        self.curr_time = time.time() # Seconds since Jan 1st, 1970
        self.curr_timezone = pytz.timezone("US/Central")
        self.cmdloop()

    def print_curr_price(self):
        """Print the most recent price."""
        print(self.exchange.get_last_trade('BTC-USD')['price'])

    def list_strategies(self):
        for key in self.strategies.keys():
            print(key)

    def load_strategy(self, module, cls, verbose=True):
        """Load a user-defined strategy from a file.

        \n`module`: the filename in the current directory containing the strategy class which
        inherits from bitraider.strategy (does not include .py)
        \n`cls`: the classname within the file to load
        """
        import_string = module+"."+cls
        self.module = module # TODO: support more than one module
        classname = str(cls)
        _temp = __import__(module)
        loaded_strategy_ = getattr(_temp, cls)
        instance_of_loaded_strategy = loaded_strategy_()
        self.strategies[classname] = instance_of_loaded_strategy
        if verbose:
            print("Loaded strategy: "+str(cls)+" from file: "+str(module)+".py")

def run():
    my_runner = runner()
    my_runner.run()

if __name__=="__main__":
    my_runner = runner()
    my_runner.run()
