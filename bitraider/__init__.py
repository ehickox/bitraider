from bitraider.trader_template import runner
from bitraider.strategy import strategy
from bitraider.exchange import cb_exchange_sim

# bitraider
#
# Copyright (C) 2015 Eli Hickox
# Author: Eli Hickox <ehicko2@illinois.edu>
# URL: <http://github.com/ehickox2012/bitraider/>
#

"""
A Library of tools for algorithmic Bitcoin trading in Python. Bitraider includes a Coinbase
Exchange API wrapper, a CLI dashboard for backtesting or running a trader, and an abstract
strategy object that enables you to implement different trading techniques.

###Quickstart:

1. `$pip install bitraider`

2. Create a new directory in which your trader will reside
`$mkdir example_trader`
`$cd example_trader`

3. Create an object that inherits from strategy. Implement all necessary functions. See example_strategy.py for a more thurough example. For Example:

    #!python
    from bitraider import strategy as strategy

        class my_strategy(strategy):

            def __init__(self):
                self.interval = 60
                # Look at every 60 seconds, required attribute
                self.any_attribute = 999
                self.current_average = 0
                self.time_from_start = 8600
                # The time required to have a baseline
                self.time_elapsed = 0


            def trade(self, timeslice):
                # This will get run in a loop for each timeslice
                # Increment time elapsed
                # If time_elapsed % recalculate_every == 0:
                #   recalculate average
                pass

4. Run: `$bitraider`

Package Organization
====================
The bitraider package contains the following subpackages

1. strategy: a module containing what a strategy class should look like

2. exchange: a module containing cb_exchange, a CoinbaseExchange API Wrapper

3. trader_template: a terminal-style dashboard for backtesting or running trading strategies.

Contributing
------------
`bitraider` [is on GitHub](https://github.com/ehickox2012/bitraider). Pull requests and bug reports are welcome.
"""

__version__ = '0.0.4'
"""The version of bitraider"""

__author__ = 'Eli Hickox <liquidchickenman.blogspot.com>'
"""The author of bitraider"""
