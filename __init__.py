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

Create an object that inherits from strategy. Implement all necessary functions. For Example:

    #!python
    from bitraider import strategy as strategy

    class my_strategy(strategy):

        def backtest_strategy():
            for timeslice in data:
                pass

run:

    $python trader_template.py

Package Organization
====================
The bitraider package contains the following subpackages

1. strategy: a module containing what a strategy class should look like

2. cbexchange: a module containing cb_exchange, a CoinbaseExchange API Wrapper

3. trader_template: a terminal-style dashboard for backtesting or running trading strategies.
"""

__version__ = '0.0.3' 
"""The version of bitraider""" 
     
__author__ = 'Eli Hickox <liquidchickenman.blogspot.com>' 
"""The author of bitraider""" 

