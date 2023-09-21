import yfinance as yf
from datalib import collate, sym_dct_mult, tdata_std, action, mod_eval_selu, print_status
import numpy as np
import time
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from datetime import datetime
import pickle
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

with open('machines/Prime_mkI_w.pickle','rb') as f:
    Prime_mkI = pickle.load(f)
    f.close()
    
with open('mkI_orders.pickle','rb') as f:
    mkI_orders = pickle.load(f)
    f.close()

with open('machines/Prime_mkII_w.pickle','rb') as f:
    Prime_mkII = pickle.load(f)
    f.close()
    
with open('mkII_orders.pickle','rb') as f:
    mkII_orders = pickle.load(f)
    f.close()
    
with open('chase_live/status.pickle','rb') as f:
    status = pickle.load(f)
    f.close()

key1 = 'PKRPZNH8F1DUMK4OZDAD'
secret1 = 'lwFPa4IeCsfFF5NCcRchPtr9c6mIncgaB9jofQWJ'
client1 = TradingClient(key1, secret1, paper=True)
acc1 = client1.get_account()
eqt1 = float(acc1.equity)

key2 = 'PK1I1556K4QGY0P2AMJ3'
secret2 = 'uqerqgvNj8Qrqnws9CeI3M4R9JVKjfAXu7QIc6bl'
client2 = TradingClient(key2, secret2, paper=True)
acc2 = client2.get_account()
eqt2 = float(acc2.equity)

play_list = ['AAPL','MSFT','GOOG','AMZN','NVDA','TSLA','META','LLY',
             'V','XOM','UNH','WMT','JPM','MA','JNJ','PG','AVGO','ORCL','HD',
             'CVX','MRK','ABBV','ADBE','KO','COST','PEP','CSCO','BAC','CRM',
             'MCD','TMO','NFLX','PFE','CMCSA','DHR','ABT','AMD','TMUS','INTC',
             'INTU','WFC','TXN','NKE','DIS','COP','CAT','PM','MS','VZ','AMGN',
             'UPS','NEE','IBM','LOW','UNP','BA','BMY','SPGI','AMAT','HON',
             'NOW','GE','RTX','QCOM','AXP','DE','PLD','SYK','SBUX',
             'SCHW','GS','LMT','ELV','ISRG','TJX','BLK','T','ADP','UBER',
             'MMC','MDLZ','GILD','ABNB','REGN','LRCX','VRTX','ADI','ZTS',
             'SLB','CVS','AMT','CI','BX','PGR','BSX','MO','C','BDX']


go = True
ctr = 0
mod1_out, mod2_out = np.array([0]),np.array([0])
while True:
    clock = client1.get_clock()
    if clock.is_open:
        minute = datetime.now().minute
        second = datetime.now().second
        c1 = minute % 5 == 0 or minute % 5 == 5
        c2 = second > 3
        if c1 and c2:
            if go:
                x_raw = yf.download(play_list, period='4d', interval='5m')
                
                symbols_dct = sym_dct_mult(x_raw.drop(x_raw.index[-1]))
                
                df_list = [symbols_dct[symbol]['hist'] for symbol in symbols_dct]
                
                df_col = collate(df_list)
                
                tdata_dct = tdata_std(df_col, 78, 12, 50)
                ############################# MODEL ACTION ####################################
                mod1_out = mod_eval_selu(tdata_dct['x'][-1], Prime_mkI)
                mod2_out = mod_eval_selu(tdata_dct['x'][-1], Prime_mkII)
                ###############################################################################
                orders_1 = action(client=client1,
                                  mod_out=mod1_out,
                                  play_list=play_list,
                                  symbols_dct=symbols_dct,
                                  equity=eqt1)
                
                orders_2 = action(client=client2,
                                  mod_out=mod2_out,
                                  play_list=play_list,
                                  symbols_dct=symbols_dct,
                                  equity=eqt2)
                
                for orderr in orders_1:
                    order = client1.submit_order(order_data=orderr)
                
                for orderr in orders_2:
                    order = client2.submit_order(order_data=orderr)
                    
                go = False
        else:
            go = True
            
    order1_list = client1.get_orders(GetOrdersRequest(status='all'))
    for order in order1_list:
        if order.status == 'filled':
            mkI_orders[str(order.id)] = {'Symbol': order.symbol,
                                         'Qty': float(order.qty),
                                         'Side': str(order.side)[10:],
                                         'Price': float(order.filled_avg_price),
                                         'Status': order.status.value,
                                         'Submit': order.submitted_at.strftime('%Y-%m-%d %H:%M:%S'),
                                         'Fill': order.filled_at.strftime('%Y-%m-%d %H:%M:%S')}
    
    order2_list = client2.get_orders(GetOrdersRequest(status='all'))
    for order in order2_list:
        if order.status == 'filled':
            mkII_orders[str(order.id)] = {'Symbol': order.symbol,
                                          'Qty': float(order.qty),
                                          'Side': str(order.side)[10:],
                                          'Price': float(order.filled_avg_price),
                                          'Status': order.status.value,
                                          'Submit': order.submitted_at.strftime('%Y-%m-%d %H:%M:%S'),
                                          'Fill': order.filled_at.strftime('%Y-%m-%d %H:%M:%S')}
            
    pos1_dct = {}
    pos1_list = client1.get_all_positions()
    for pos in pos1_list:
        pos1_dct[pos.symbol] = {'Qty': float(pos.qty),
                                'Value': float(pos.market_value),
                                'Gain': round(float(pos.unrealized_plpc)*100,2)}
        
    pos2_dct = {}
    pos2_list = client2.get_all_positions()
    for pos in pos2_list:
        pos2_dct[pos.symbol] = {'Qty': float(pos.qty),
                                'Value': float(pos.market_value),
                                'Gain': round(float(pos.unrealized_plpc)*100,2)}
            
    ########################## TO KAFKA #######################################
    status = {'Time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
              'Market_open': clock.is_open,
              'Gains_mkI': round(eqt1/1000 - 100,2),
              'Pos_mkI': pos1_dct,
              'Orders_mkI': mkI_orders,
              'Gains_mkII': round(eqt2/1000 - 100,2),
              'Pos_mkII': pos2_dct,
              'Orders_mkII': mkII_orders}
    if ctr % 12 == 0:
        acc1 = client1.get_account()
        acc2 = client2.get_account()
        eqt1 = float(acc1.equity)
        eqt2 = float(acc2.equity)
        print_status(status, mod1_out, mod2_out)
    
    with open('mkI_orders.pickle','wb') as f:
        pickle.dump(mkI_orders, f)
        f.close()
        
    with open('mkII_orders.pickle','wb') as f:
        pickle.dump(mkII_orders, f)
        f.close()
        
    with open('chase_live/status.pickle','wb') as f:
        pickle.dump(status, f)
        f.close()
        
    time.sleep(5)
    ctr += 1
