.. . documentation master file, created by
   sphinx-quickstart on Thu Feb 19 12:43:42 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to bitraider's documentation!
=====================================
A Library of tools for algorithmic Bitcoin trading in Python. Bitraider includes a Coinbase 
Exchange API wrapper, a CLI dashboard for backtesting or running a trader, and an abstract
strategy object that enables you to implement different trading techniques.

Quickstart:
-----------

1::
    
    pip install bitraider

2. Create a new directory in which your trader will reside:
::

    $mkdir example_trader

::

    $cd example_trader

3. Create an `auth.txt` containing your Coinbase API key, secret, and passphrase on lines 1, 2, and 3 respectively.
::

    $vim auth.txt

In auth.txt:
::

    MY-API-KEY-HERE
    MY-API-SECRET-HERE
    MY-API-PASSPHRASE-HERE


4. Create a class in a Python file that inherits from strategy. Implement all necessary functions. For Example:
::

    from bitraider import strategy as strategy

    class my_strategy(strategy):

        def backtest_strategy(self, historical_data, start_btc, start_usd):
            for timeslice in historical_data:
                pass


5. Run
::

    $bitraider

Package Organization
====================
The bitraider package contains the following subpackages

1. strategy: a module containing what a strategy class should look like

2. cbexchange: a module containing cb_exchange, a CoinbaseExchange API Wrapper

3. trader_template: a terminal-style dashboard for backtesting or running trading strategies.

Contributing
------------
.. _is on GitHub: https://github.com/ehickox2012/bitraider 

`bitraider` `is on GitHub`_ . Pull requests and bug reports are welcome.

Contents:

.. toctree::
   :maxdepth: 4

   bitraider


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

