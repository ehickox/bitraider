from bitraider.cbexchange import cb_exchange
from bitraider.trader_template import runner
from bitraider.strategy import strategy

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

3. Create an `auth.txt` containing your Coinbase API key, secret, and passphrase on lines 1, 2, and 3 respectively.
`$vim auth.txt`

In auth.txt:
```
MY-API-KEY-HERE
MY-API-SECRET-HERE
MY-API-PASSPHRASE-HERE
```

4. Create an object that inherits from strategy. Implement all necessary functions. For Example:

    #!python
    from bitraider import strategy as strategy

    class my_strategy(strategy):

        def backtest_strategy(self, historical_data, start_btc, start_usd):
            for timeslice in historical_data:
                pass

5. Run: `$bitraider`

Package Organization
====================
The bitraider package contains the following subpackages

1. strategy: a module containing what a strategy class should look like

2. cbexchange: a module containing cb_exchange, a CoinbaseExchange API Wrapper

3. trader_template: a terminal-style dashboard for backtesting or running trading strategies.

Contributing
------------
`bitraider` [is on GitHub](https://github.com/ehickox2012/bitraider). Pull requests and bug reports are welcome.
"""

__version__ = '0.0.3' 
"""The version of bitraider""" 
     
__author__ = 'Eli Hickox <liquidchickenman.blogspot.com>' 
"""The author of bitraider""" 

