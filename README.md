# bitraider
A Library of tools for algorithmic Bitcoin trading in Python. Bitraider includes a Coinbase
Exchange API wrapper, a CLI dashboard for backtesting or running a trader, and an abstract
strategy class that enables you to implement different trading techniques.

###Quickstart:

1. `$pip install bitraider`

2. Create a new directory in which your trader will reside
    ```
    $mkdir example_trader
    $cd example_trader
    ```

3. Create a class that inherits from bitraider.strategy. Implement all necessary functions.
NOTE: See `example_strategy.py` for a more thurough example.

    ```
    $vim mystrategy.py
    ```

    ```
    from bitraider import strategy as strategy

        class my_strategy(strategy):

            def __init__(self):
                self.interval = 60
                # Look at every 60 seconds, required attribute
                self.any_attribute = 999
                self.current_average = 0
                self.recalculate_every = 8600
                self.time_elapsed = 0
                # Recalculate average every day

            def trade(self, timeslice):
                # This will get run in a loop for each timeslice
                # Increment time elapsed
                # If time_elapsed % recalculate_every == 0:
                #   recalculate average
                pass
    ```

4. `$bitraider`

Package Organization
====================
The bitraider package contains the following subpackages

1. strategy: a module containing what a strategy class should look like

2. exchange: a module containing cb_exchange, a CoinbaseExchange API Wrapper

3. trader_template: a terminal-style dashboard for backtesting or running trading strategies.

TODO:
======
1. Implement logging with python logging
2. Implement emailer
