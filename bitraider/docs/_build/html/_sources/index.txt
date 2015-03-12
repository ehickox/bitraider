.. . documentation master file, created by
   sphinx-quickstart on Thu Feb 19 12:43:42 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to bitraider's documentation!
=====================================
A Library of tools for algorithmic Bitcoin trading in Python. Bitraider includes a Coinbase 
Exchange API wrapper, a CLI dashboard for backtesting or running a trader, and an abstract
strategy class that enables you to implement different trading techniques.

Quickstart:
-----------

1::
    
    $pip install bitraider

2. Create a new directory in which your trader will reside:
::

    $mkdir example_trader

::

    $cd example_trader

3. Create a class that inherits from bitraider.strategy. Implement all necessary functions. See `example_strategy.py` for a more thorough example.
::

    $vim mystrategy.py

::

    from bitraider import strategy as strategy

    class my_strategy(strategy):

        def __init__(self):
            self.interval = 60
            # Look at every 60 seconds, required
            self.time_from_start = 8600
            # Time needed to have a baseline
            self.any_attribute = 0.5
            self.current_average = 0
            self.time_elapsed = 0

        def trade(self, timeslice):
            # This will run in a loop for each timeslice
            # Increment time elapsed
            self.time_elapsed += self.interval
            if self.time_elapsed % self.time_from_start == 0:
                # recalculate average
            pass

4. Run
::

    $bitraider

Package Organization
====================
The bitraider package contains the following subpackages

1. strategy: a module containing what a strategy class should look like

2. exchange: a module containing cb_exchange, a CoinbaseExchange API Wrapper

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

