import numpy as np
import pandas as pd
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from numpy_ml.neural_nets.activations import SELU
selu = SELU()

# Collate list of histories into a singular array
def collate(df_list):
    out = []
    for i in range(len(df_list[0].index)):
        idx = df_list[0].index[i]
        tmp = []
        for df in df_list:
            if idx in df.index:
                val = [df['Close'][idx],
                       df['High'][idx],
                       df['Low'][idx],
                       df['Volume'][idx]]
            else:
                val = [df['Close'][df.index[i-1]],
                       df['High'][df.index[i-1]],
                       df['Low'][df.index[i-1]],
                       df['Volume'][df.index[i-1]]]
            tmp.append(val)
        out.append(tmp)
    return np.array(out, dtype=np.float32)

def tdata_std(df_col, h_prev, h_next, scale):
    x_raw = np.zeros((h_prev,
                      df_col.shape[0]-h_prev-h_next,
                      df_col.shape[1],
                      3),dtype=np.float32)
    y_raw = np.zeros((df_col.shape[0]-h_prev-h_next,
                      3,
                      df_col.shape[1]),dtype=np.float32)
    
    for t in range(h_prev,df_col.shape[0]-h_next):
        x_raw[:,t-h_prev] = df_col[t-h_prev:t,:,1:4]
        y_raw[t-h_prev,0] = df_col[t:t+h_next,:,1].max(axis=0)
        y_raw[t-h_prev,1] = df_col[t:t+h_next,:,2].min(axis=0)
        y_raw[t-h_prev,2] = df_col[t,:,0]
        
    # Standardize x and process y
    a = x_raw - x_raw.mean(axis=0)
    b = x_raw.std(axis=0)
    x = np.divide(a,b,out=np.zeros_like(a),where=b!=0)
    y = np.tanh(((y_raw[:,0]/y_raw[:,2])-(y_raw[:,2]/y_raw[:,1]))*scale)
    
    # Pickle the data
    return {'x': x.swapaxes(0,1), 'y': y}

def sym_dct_mult(x_raw):
    play_list = []
    kys = list(x_raw.keys())
    for ky in kys:
        if ky[0] == 'Close': play_list.append(ky[1])
        
    symbols_dct = {}
    for symbol in play_list:
        symbols_dct[symbol] = {}
        cols = {'Open': x_raw['Open'][symbol],
                'High': x_raw['High'][symbol],
                'Low': x_raw['Low'][symbol],
                'Close': x_raw['Close'][symbol],
                'Volume': x_raw['Volume'][symbol]}
        df = pd.concat(cols, axis=1)
        df.index = df.index.tz_localize(None)
        df['Symbol'] = symbol
        df['Time'] = df.index
        df = df.ffill()
        symbols_dct[symbol]['hist'] = df
    return symbols_dct

def action(client,
           mod_out,
           play_list,
           symbols_dct,
           close_thr=0.2,
           open_thr=0.5,
           max_pos=20,
           equity=100000):
    pos_size = equity/max_pos
    mod_out = mod_out.squeeze()
    orders = []
    
    move_dct = {}
    for i in range(len(play_list)):
        if mod_out[i] >= 0:
            side = 'long'
        else:
            side = 'short'
        move_dct[play_list[i]] = {'side': side,
                                  'score': np.abs(mod_out[i])}
    move_df = pd.DataFrame(move_dct).transpose().sort_values('score',ascending=False)
    
    positions = client.get_all_positions()
    for pos in positions:
        c1 = move_df['side'][pos.symbol] != pos.side
        c2 = move_df['score'][pos.symbol] < close_thr
        if c1 or c2:
            client.close_position(pos.symbol)
            positions.remove(pos)
            
        
    allowed_pos = max_pos - len(positions)
    for i in range(allowed_pos):
        symbol = move_df.index[i]
        if move_df['score'][symbol] > open_thr and move_df['side'][symbol] == 'long':
            price = symbols_dct[symbol]['hist'].iloc[-1]['Close']
            qty = pos_size // price
            
            if side == 'long':
                order_side = OrderSide.BUY
            else:
                order_side = OrderSide.SELL
                
            orders.append(MarketOrderRequest(symbol=symbol,
                                             qty=qty,
                                             side=order_side,
                                             time_in_force=TimeInForce.DAY))
    return orders
            
def mod_eval_selu(x, mod_w):
    out = selu.fn(np.matmul(x.flatten(), mod_w[0])) + mod_w[1]
    for i in range(2,len(mod_w)-2,2):
        out = selu.fn(np.matmul(out, mod_w[i])) + mod_w[i+1]
    out = np.tanh(np.matmul(out, mod_w[-2])) + mod_w[-1]
    return np.array([out])

def print_status(status, mod1_out, mod2_out):
    print(
    f"""
    ######################################################################
    Time: {status['Time']}
    Market Open: {status['Market_open']}
    Mod1: Max = {round(mod1_out.max(),2)}, Min = {round(mod1_out.min(),2)}
    Mod2: Max = {round(mod2_out.max(),2)}, Min = {round(mod2_out.min(),2)}
    -----------------------------Prime mkI--------------------------------
    Gains: {status['Gains_mkI']} %
    Positions:
    """)
    for pos in status['Pos_mkI']:
        print(f"        {pos}: {status['Pos_mkI'][pos]['Gain']} %")
    print(
    f"""
    -----------------------------Prime mkII-------------------------------
    Gains: {status['Gains_mkII']} %
    Positions:
    """)
    for pos in status['Pos_mkII']:
        print(f"        {pos}: {status['Pos_mkII'][pos]['Gain']} %")
    print(
    """
    ----------------------------------------------------------------------
    """)
    