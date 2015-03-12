import json, hmac, hashlib, time, requests, base64
from requests.auth import AuthBase
from abc import ABCMeta, abstractmethod

class exchange(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def place_order(self):
        pass

class cb_exchange_sim(exchange):
    """Class used for backtesting"""

    def __init__(self, start_btc, start_usd):
        self.start_usd = start_usd
        self.start_btc = start_btc
        self.btc_bal = start_btc
        self.usd_bal = start_usd
        self.fee_percent = 0.25
        self.times_bought = 0
        self.times_sold = 0
        self.api_url = 'https://api.exchange.coinbase.com/'

    def get_historic_rates(self, start_time, end_time, granularity, product_id='BTC-USD'):
        """Get a historic rates for a product. Rates are returned in grouped
        buckets based on requested granularity"""
        params= {
            'start': start_time,
            'end': end_time,
            'granularity': granularity
        }
        r = requests.get(self.api_url + 'products/' + product_id + '/candles', params=params)
        rDict = r.json()
        return rDict

    def get_last_trade(self, product_id):
        """Get snapshot information about the last trade (tick)"""
        r = requests.get(self.api_url + 'products/' + product_id + '/ticker')
        rDict = r.json()
        return rDict

    def place_order(self, price, size, side, product_id, historic_timeslice=None):
        """Place an order

        For buy orders, we will hold price x size x (1 + fee-percent) USD. For sell orders,
        we will hold the number of Bitcoin you wish to sell. Actual fees are assessed at time of trade.
        If you cancel a partially filled or unfilled order, any remaining funds will be released from hold.
        """
        order = {
            'size': size,
            'price': price,
            'side': side,
            'product_id': product_id,
        }
        size = float(size)
        currprice = 0
        if historic_timeslice is not None:
            currprice = float(historic_timeslice[4])
        else:
            currprice = float(self.get_last_trade(product_id).get("price"))

        if side == "buy":
            if self.usd_bal >= (size*price):
                if currprice <= price:
                    self.usd_bal -= (size*currprice)
                    self.btc_bal += size
                    self.times_bought += 1
                    #print("Buy of: "+str(size)+" BTC made at price: "+str(currprice))
                else:
                    # TODO: put buy in holds
                    pass
            else:
                print("Insufficient funds")

        elif side == "sell":
            if self.btc_bal >= size:
                if currprice >= price:
                    self.usd_bal += (size*currprice)
                    self.btc_bal -= size
                    self.times_sold += 1
                    #print("Sell of: "+str(size)+" BTC made at price: "+str(currprice))
                else:
                    # TODO: put sell in holds
                    pass
            else:
                print("Insufficient funds")
        return

# Create custom authentication for Exchange
class CoinbaseExchangeAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or '')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        signature_b64 = signature.digest().encode('base64').rstrip('\n')

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            })
        return request

class cb_exchange(exchange):
    """CoinbaseExchange API Wrapper"""

    def __init__(self, key=None, secret=None, password=None):
        self.key=key
        self.secret=secret
        self.password=password
        self.auth = None
        if password is not None:
            self.auth = CoinbaseExchangeAuth(key, secret, password)
        self.api_url = 'https://api.exchange.coinbase.com/'

    def list_accounts(self):
        """Get a list of trading accounts"""
        r = requests.get(self.api_url + 'accounts', auth=self.auth)
        rDict = r.json()
        return rDict

    def get_account(self, account_id):
        """Get information for a single account"""
        r = requests.get(self.api_url + 'accounts/' + account_id, auth=self.auth)
        rDict = r.json()
        return rDict

    def get_account_history(self, account_id):
        """List account activity. Items are paginated and sorted latest first."""
        r = requests.get(self.api_url + 'accounts/' + account_id + '/ledger', auth=self.auth)
        rDict = r.json()
        return rDict

    def get_holds(self, account_id):
        """Holds are placed on an account for any active orders. As an order
        is filled, the hold amount is updated. If ad order is canceled, any
        remaining hold is removed."""
        r = requests.get(self.api_url + 'accounts/' + account_id + '/holds', auth=self.auth)
        rDict = r.json()
        return rDict

    def place_order(self, price, size, side, product_id):
        """Place an order"""
        order = {
            'size': size,
            'price': price,
            'side': side,
            'product_id': product_id,
        }
        r = requests.post(self.api_url + 'orders', params=order, auth=self.auth)
        rDict = r.json()
        return rDict

    def cancel_order(self, order_id):
        """Cancel an order"""
        r = requests.delete(self.api_url + 'orders/' + order_id, auth=self.auth)
        rDict = r.json()
        return rDict

    def list_open_orders(self):
        """List currently open orders"""
        r = requests.get(self.api_url + 'orders', auth=self.auth)
        rDict = r.json()
        return rDict

    def get_order(self, order_id):
        """Get a single order"""
        r = requests.get(self.api_url + 'orders/' + order_id, auth=self.auth)
        rDict = json.loa(r.json())
        return rDict

    def list_fills(self):
        """Get a list of recent fills"""
        r = requests.get(self.api_url + 'fills', auth=self.auth)
        rDict = r.json()
        return rDict

    def transfer(self):
        """Move funds to/from Coinbase Exchange and Coinbase account"""
        r = requests.post(self.api_url + 'transfers', auth=self.auth)
        rDict = r.json()
        return rDict

    # Unauthenticated endpoints below

    def get_products(self):
        """Get a list of available currency pairs for trading"""
        r = requests.get(self.api_url + 'products')
        rDict = r.json()
        return rDict

    def get_order_book(self, product_id, level=1):
        """Get a list of open orders for a product. Amount of detail
        shown can be customized with the level parameter."""
        params= {
            'level': level,
        }
        r = requests.get(self.api_url + 'products/' + product_id + '/book', params=params)
        rDict = r.json()
        return rDict

    def get_last_trade(self, product_id):
        """Get snapshot information about the last trade (tick)"""
        r = requests.get(self.api_url + 'products/' + product_id + '/ticker')
        rDict = r.json()
        return rDict

    def get_trades(self, product_id):
        """Get a paginated list of latest trades for a product"""
        r = requests.get(self.api_url + 'products/' + product_id + '/trades')
        rDict = r.json()
        return rDict

    def get_historic_rates(self, start_time, end_time, granularity, product_id='BTC-USD'):
        """Get a historic rates for a product. Rates are returned in grouped
        buckets based on requested granularity"""
        params= {
            'start': start_time,
            'end': end_time,
            'granularity': granularity
        }
        r = requests.get(self.api_url + 'products/' + product_id + '/candles', params=params)
        rDict = r.json()
        return rDict

    def get_24_hour_stats(self, product_id):
        """Get 24 hour stats for the product"""
        r = requests.get(self.api_url + 'products/' + product_id + '/stats')
        rDict = r.json()
        return rDict

    def get_currencies(self):
        """Get a list of known currencies"""
        r = requests.get(self.api_url + 'currencies')
        rDict = r.json()
        return rDict

    def get_time(self):
        """Get the API server time"""
        r = requests.get(self.api_url + 'time')
        rDict = r.json()
        return rDict

