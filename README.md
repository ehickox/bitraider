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

4. Create a class that inherits from bitraider.strategy. Implement all necessary functions.
NOTE: See `example_strategy.py` for a more thurough example.

    ```
    vim mystrategy.py
    ```

    ```
    from bitraider import strategy as strategy

        class my_strategy(strategy):

            def __init__(self):
                self.usd_bal = 1000
                self.other_attributes = 999

            def trade(self, timeslice):
                # This will get run in a loop for each timeslice
                pass
    ```

5. `$bitraider`

Package Organization
====================
The bitraider package contains the following subpackages
1. strategy: a module containing what a strategy class should look like
2. cbexchange: a module containing cb_exchange, a CoinbaseExchange API Wrapper
3. trader_template: a terminal-style dashboard for backtesting or running trading strategies.

TODO:
======
1. Implement logging with python logging
2. Implement emailer
