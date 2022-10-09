# for test purposes only
# read dydx docs https://docs.dydx.exchange/
# do not use with already existing open positions - it will take profit/loss on run


from dydx3 import Client
from dydx3.constants import *
import time
from dydx3.constants import ORDER_SIDE_BUY
from dydx3.constants import ORDER_SIDE_SELL
from dydx3.constants import ORDER_STATUS_OPEN
from dydx3.constants import ORDER_TYPE_LIMIT
from dydx3.constants import ORDER_TYPE_TAKE_PROFIT
from statistics import mean
from statistics import median


ETHEREUM_ADDRESS = 'your_address'                                       # your credentials 
private_client = Client(
    host = 'https://api.dydx.exchange',         
    api_key_credentials = {'key': 'your_key',                           
    'secret': 'your_secret',
    'passphrase': 'your_passphrase'},
    stark_private_key = 'your_privat_key',
    default_ethereum_address = ETHEREUM_ADDRESS,
)

#for ETH/USD market
def candle_data(resolution,max_range):
    account_response = private_client.private.get_account()
    position_id = account_response.data['account']['positionId']
    print(position_id)
    candles = private_client.public.get_candles(market=MARKET_ETH_USD,resolution=resolution,)
    arr_delta = []
    for i in range(0,max_range):
        low = float(candles.data['candles'][i]['low'])
        high = float(candles.data['candles'][i]['high'])
        delta = abs(low-high)
        arr_delta.append(round(delta,2))
    return arr_delta

# candle data - spreads data

def candle_stats(resolution,max_range):
    avg_delta = candle_data(resolution,max_range)
    #print(avg_delta)
    mean_delta = mean(avg_delta)
    high_delta = max(avg_delta)
    low_delta = min(avg_delta)
    median_delta = median(avg_delta)
    print('\n')
    print(resolution)
    print("MEAN: ",round(mean_delta,2))
    print("MEDIAN: ",round(median_delta,2))
    print("MAX: ",round(high_delta,2))
    print("MIN: ",round(low_delta,2))

big_stat = candle_stats("15MINS",16)
medium_stat = candle_stats("5MINS",48)
small_stat = candle_stats("1MIN",100)

account_response = private_client.private.get_account()
position_id = account_response.data['account']['positionId']
print(position_id)


side = input("Select side: S - short, L - long : ")
pos_price = input("Enter price: ")

# orders part

if side == "s":                                                         # FOR SHORT
    order_side = ORDER_SIDE_SELL                                        # places SELL order aka short
    take_profit_side = ORDER_SIDE_BUY                                   # thus take profit = BUY aka long
    price_profit = float(pos_price) - 4                                 # takes profit when price 4 usd lower 
    price_trigger = float(pos_price) - 0.1                              # triggers take profit order fast when price 0.1 usd lower
    price_stop = float(pos_price) + 1.8                                 # stop loss if price 1.8 usd higher
    price_trigger_stop = float(pos_price) + 1.2                         # triggers stop loss order when price is 1.2 usd higher

else:                                                                   # FOR LONG
    order_side = ORDER_SIDE_BUY                                         # everything opposite to SHORT
    take_profit_side = ORDER_SIDE_SELL                                  
    price_profit = float(pos_price) + 4
    price_trigger = float(pos_price) + 0.1
    price_stop = float(pos_price) - 1.8
    price_trigger_stop = float(pos_price) - 1.2

#order size 1 ETH
try:
    order_params = {
        'position_id': position_id,
        'market': MARKET_ETH_USD,
        'side': order_side,
        'order_type': ORDER_TYPE_LIMIT,
        'post_only': False,
        'size': '1',
        'price': str(pos_price),
        'limit_fee': '0.0015',
        'expiration_epoch_seconds': time.time() + 300                   # kills order in 5 mins if not filled
        }
    order_bid = private_client.private.create_order(**order_params)
    order_id = order_bid.data['order']['id']
    print(order_id)

except Exception as e:
    print(e)


print('===ORDERs STATUS===')
print('\n')

#open positions part

while True:
    account_response = private_client.private.get_account()
    open_positions = account_response.data['account']['openPositions']
    if len(open_positions)>=1:

        order_params = {
            'position_id': position_id,
            'market': MARKET_ETH_USD,
            'side': take_profit_side,
            'order_type': ORDER_TYPE_TAKE_PROFIT,
            'post_only': False,
            'size': '1',                                                # position size 1 ETH
            'trigger_price': str(round(price_trigger,1)),
            'price': str(price_profit),
            'limit_fee': '0.0015',
            'expiration_epoch_seconds': time.time() + 86400             
            }
        order_bid_tp = private_client.private.create_order(**order_params)
        order_id_tp = order_bid_tp.data['order']['id']
        print(order_id_tp)

        order_params_stop = {
            'position_id': position_id,
            'market': MARKET_ETH_USD,
            'side': take_profit_side,
            'order_type': ORDER_TYPE_STOP,
            'post_only': False,
            'size': '1',                                                # position size 1 ETH
            'trigger_price': str(round(price_trigger_stop,1)),
            'price': str(price_stop),
            'limit_fee': '0.0015',
            'expiration_epoch_seconds': time.time() + 86400
            }
        order_bid_stop = private_client.private.create_order(**order_params_stop)
        order_id_stop = order_bid_stop.data['order']['id']
        print(order_id_stop)

        break
    else:
        print("NOT FILLED") 
        time.sleep(5)                                                   # updates every 5 seconds
