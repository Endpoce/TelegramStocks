"""
This program was thought up because I want to stay up to date on stocks, without having to look them all up. The end product will take a list of tickers, and send the user
a report on that list. The report will eventually be very comprehensive, but for now we are looking for the basics. The bot should be able to send, stock and crypto price data.
Indicators will be added later. Adaptations are availible for other use cases.
"""


from matplotlib import ticker
import telebot
import os
import pandas as pd
import numpy as np
import yfinance as yf
import datetime
import schedule
import time

from dotenv import load_dotenv

load_dotenv()

botcode = os.getenv('botcode')

# Initialize bot
bot = telebot.TeleBot("5142532758:AAHuirsPXHSOPOr9WC7Y1sCaMgu9DV3ApNU")

Volumes = {}
Price_action = {}

## List of tickers to download
Buffet_Tracker_list = [ "AAPL", "ABBV", "AMZN", 'AXP', 'AXTA', 'BIIB', 'BMY', 'CHTR', 'CVX', 'DVA', "GM", 'JNJ', 'KHC', 'KO', 'LBTYA', 'MCO', 'MDLZ', 'MMC', 'MRK', 'MSFT', 'RH', 'SIRI', 'SNOW', 'SPY', 'STNE', 'STOR', 'SYF', 'TEVA', 'TMUS', 'UPS', 'USB', 'VOO', 'VRSN', 'VZ', 'WFC']
ARK_Tracker_list = [ "TSLA", "TDOC", "ROKU", 'COIN', 'ZM', 'EXAS', 'SQ', 'U', 'PATH', 'TWLO', "SPOT", 'BEAM', 'CRSP', 'NTLA', 'SHOP', 'DKNG', 'PD', 'FATE', 'HOOD', 'SGFY', 'TXG', 'NVTA', 'RBLX', 'PACB', 'VCYT', 'DNA', 'SSYS', 'TWST', 'SE', 'TSP', 'MTLS', 'TWOU', 'CERS', 'BLI', 'CGEN']
BillGates_Tracker_list = ["SAFM","SDGR", "CPNG", "WEBR", "WM","ECL", " MSGS"]
MichaelBurry_Tracker_list = ["GPN","STLA","NXST", "OVV", "FB", "CI"]
BlackRock_Tracker_list = ["FB","UNH","JNJ","BRK-B", "NVDA", "Appl", "AMZN", "MSFT"]

Crypto_Tracker_list = ['BTC-USD', 'ETH-USD', 'BTC-ETH','SOL']


## start message
@bot.message_handler(commands='hey')

def greeting(message):
    response = 'Hello!\nType /, then the command!\nWatchlists: \n\t-B\n\t-A\n\t-crypto\n\t-BG\n\t-MB\n\t-BR'

    bot.send_message(message.chat.id, response)

# Command message
@bot.message_handler(commands='B')

# Function to retrieve stock data and send message to telegram
def get_stocks(message):
    stocks = Buffet_Tracker_list

    for stock in stocks:
        stock_data = []
        response2 = ""

        ## download stock data, format it, get up until a week agos worth of data
        stock_info = yf.download(stock, period='1y', interval='1d')
        data = stock_info.reset_index()
        data = data[-7:]

        ## make 
        stock_data.append([stock])
        columns = ['stock']

        ## calculate average volume and price action
        Volumes[stock] = stock_info['Volume'].mean()
        Price_action[stock] = stock_info['Close'].diff().mean()

        ## calculate max volume and price action
        max_volume = max(Volumes, key=Volumes.get)
        max_action = max(Price_action, key=Price_action.get)
        
        ## build telegram message, adding a newline at end of each string
        response2 += "Highest Avg. Volume(1y):\n" +  max_volume+'\n'
        response2 += "Highest Price Action (1y):\n" +  max_action+ '\n'

    ## send message
    bot.send_message(message.chat.id, response2)

    ## print response to console and not telegram
    # print(response)

    # for stock in stocks - download data, format it, put in response var
    for stock in stocks:
        stock_data = []
        response = ""

        stock_info = yf.download(stock, period='1y', interval='1d')
        data = stock_info.reset_index()
        data = data[-7:]

        # print(data)

        response += f"----------{stock}----------\n"
        stock_data.append([stock])
        columns = ['stock']

        Volumes[stock] = stock_info['Volume'].mean()
        Price_action[stock] = stock_info['Close'].diff().mean()

        # for index, row in data (rows iterrated), round close price, format date, 
        for index, row in data.iterrows():
            stock_position = len(stock_data) - 1
            price = round(row['Close'], 2)
            format_date = row['Date'].strftime('%m/%d')
            response += f"{format_date}: {price}\n"
            stock_data[stock_position].append(price)
            columns.append(format_date)
        print()

        emasUsed=[30, 35, 60, 100]

        for x in emasUsed:
            ema=x
            stock_info["Ema_"+str(ema)]=round(stock_info.iloc[:,4].ewm(span=ema, adjust=False).mean(),2)

        df=stock_info.iloc[0:]

        for i in df.index:
            cmin=min(df["Ema_30"][i],df["Ema_35"][i])
            cmax=max(df["Ema_60"][i],df["Ema_100"][i])
            
        if(cmin>cmax):
            response += "\n"+str(stock)+" is in bullish position."

        elif(cmin<cmax):
            response += "\n"+str(stock)+" is in bearish position."

        

        bot.send_message(message.chat.id, response)



## Command message for cryptos
@bot.message_handler(commands='cryp')

# Function to retrieve stock data and send message to telegram
def get_Cryptos(message):
    stocks = Crypto_Tracker_list

    response2 = ""

    df = yf.download(stocks, group_by='Ticker', period='2d')
    df = df.stack(level=0).rename_axis(['Date', 'Ticker']).reset_index(level=1)
    
    df.dropna()
    df.to_csv('rawdata.csv')
    
    for stock in df:
        stock_data = []
        stock_data.append([stock])

        Volumes[stock] = df['Volume'].mean()
        Price_action[stock] = df['Close'].diff().mean()

    ## calculate max volume and price action
    max_volume = max(Volumes, key=Volumes.get)
    print(max_volume)
    max_action = max(Price_action, key=Price_action.get)

    ## build telegram message, adding a newline at end of each string
    response2 += "Highest Avg. Volume(1y):\n" +  max_volume+'\n'
    response2 += "Highest Price Action (1y):\n" +  max_action+ '\n'

    ## send message
    bot.send_message(message.chat.id, response2)

# Command message
@bot.message_handler(commands='A')

# Function to retrieve stock data and send message to telegram
def get_stocks(message):
    stocks = ARK_Tracker_list

    for stock in stocks:
        stock_data = []
        response2 = ""

        ## download stock data, format it, get up until a week agos worth of data
        stock_info = yf.download(stock, period='1y', interval='1d')
        data = stock_info.reset_index()
        data = data[-7:]

        ## make 
        stock_data.append([stock])
        columns = ['stock']

        ## calculate average volume and price action
        Volumes[stock] = stock_info['Volume'].mean()
        Price_action[stock] = stock_info['Close'].diff().mean()

        ## calculate max volume and price action
        max_volume = max(Volumes, key=Volumes.get)
        max_action = max(Price_action, key=Price_action.get)
        
        ## build telegram message, adding a newline at end of each string
        response2 += "Highest Avg. Volume(1y):\n" +  max_volume+'\n'
        response2 += "Highest Price Action (1y):\n" +  max_action+ '\n'

    ## send message
    bot.send_message(message.chat.id, response2)

    ## print response to console and not telegram
    # print(response)

    # for stock in stocks - download data, format it, put in response var
    for stock in stocks:
        stock_data = []
        response = ""

        stock_info = yf.download(stock, period='1y', interval='1d')
        data = stock_info.reset_index()
        data = data[-7:]

        # print(data)

        response += f"----------{stock}----------\n"
        stock_data.append([stock])
        columns = ['stock']

        Volumes[stock] = stock_info['Volume'].mean()
        Price_action[stock] = stock_info['Close'].diff().mean()

        # for index, row in data (rows iterrated), round close price, format date, 
        for index, row in data.iterrows():
            stock_position = len(stock_data) - 1
            price = round(row['Close'], 2)
            format_date = row['Date'].strftime('%m/%d')
            response += f"{format_date}: {price}\n"
            stock_data[stock_position].append(price)
            columns.append(format_date)
        print()

        emasUsed=[30, 35, 60, 100]

        for x in emasUsed:
            ema=x
            stock_info["Ema_"+str(ema)]=round(stock_info.iloc[:,4].ewm(span=ema, adjust=False).mean(),2)

        df=stock_info.iloc[0:]

        for i in df.index:
            cmin=min(df["Ema_30"][i],df["Ema_35"][i])
            cmax=max(df["Ema_60"][i],df["Ema_100"][i])
            
        if(cmin>cmax):
            response += "\n"+str(stock)+" is in bullish position."

        elif(cmin<cmax):
            response += "\n"+str(stock)+" is in bearish position."

        

        bot.send_message(message.chat.id, response)

# Command message
@bot.message_handler(commands='BG')

# Function to retrieve stock data and send message to telegram
def get_stocks(message):
    stocks = BillGates_Tracker_list

    for stock in stocks:
        stock_data = []
        response2 = ""

        ## download stock data, format it, get up until a week agos worth of data
        stock_info = yf.download(stock, period='1y', interval='1d')
        data = stock_info.reset_index()
        data = data[-7:]

        ## make 
        stock_data.append([stock])
        columns = ['stock']

        ## calculate average volume and price action
        Volumes[stock] = stock_info['Volume'].mean()
        Price_action[stock] = stock_info['Close'].diff().mean()

        ## calculate max volume and price action
        max_volume = max(Volumes, key=Volumes.get)
        max_action = max(Price_action, key=Price_action.get)
        
        ## build telegram message, adding a newline at end of each string
        response2 += "Highest Avg. Volume(1y):\n" +  max_volume+'\n'
        response2 += "Highest Price Action (1y):\n" +  max_action+ '\n'

    ## send message
    bot.send_message(message.chat.id, response2)

    ## print response to console and not telegram
    # print(response)

    # for stock in stocks - download data, format it, put in response var
    for stock in stocks:
        stock_data = []
        response = ""

        stock_info = yf.download(stock, period='1y', interval='1d')
        data = stock_info.reset_index()
        data = data[-7:]

        # print(data)

        response += f"----------{stock}----------\n"
        stock_data.append([stock])
        columns = ['stock']

        Volumes[stock] = stock_info['Volume'].mean()
        Price_action[stock] = stock_info['Close'].diff().mean()

        # for index, row in data (rows iterrated), round close price, format date, 
        for index, row in data.iterrows():
            stock_position = len(stock_data) - 1
            price = round(row['Close'], 2)
            format_date = row['Date'].strftime('%m/%d')
            response += f"{format_date}: {price}\n"
            stock_data[stock_position].append(price)
            columns.append(format_date)
        print()

        emasUsed=[30, 35, 60, 100]

        for x in emasUsed:
            ema=x
            stock_info["Ema_"+str(ema)]=round(stock_info.iloc[:,4].ewm(span=ema, adjust=False).mean(),2)

        df=stock_info.iloc[0:]

        for i in df.index:
            cmin=min(df["Ema_30"][i],df["Ema_35"][i])
            cmax=max(df["Ema_60"][i],df["Ema_100"][i])
            
        if(cmin>cmax):
            response += "\n"+str(stock)+" is in bullish position."

        elif(cmin<cmax):
            response += "\n"+str(stock)+" is in bearish position."

        

        bot.send_message(message.chat.id, response)

# Command message
@bot.message_handler(commands='MB')

# Function to retrieve stock data and send message to telegram
def get_stocks(message):
    stocks = MichaelBurry_Tracker_list

    for stock in stocks:
        stock_data = []
        response2 = ""

        ## download stock data, format it, get up until a week agos worth of data
        stock_info = yf.download(stock, period='1y', interval='1d')
        data = stock_info.reset_index()
        data = data[-7:]

        ## make 
        stock_data.append([stock])
        columns = ['stock']

        ## calculate average volume and price action
        Volumes[stock] = stock_info['Volume'].mean()
        Price_action[stock] = stock_info['Close'].diff().mean()

        ## calculate max volume and price action
        max_volume = max(Volumes, key=Volumes.get)
        max_action = max(Price_action, key=Price_action.get)
        
        ## build telegram message, adding a newline at end of each string
        response2 += "Highest Avg. Volume(1y):\n" +  max_volume+'\n'
        response2 += "Highest Price Action (1y):\n" +  max_action+ '\n'

    ## send message
    bot.send_message(message.chat.id, response2)

    ## print response to console and not telegram
    # print(response)

    # for stock in stocks - download data, format it, put in response var
    for stock in stocks:
        stock_data = []
        response = ""

        stock_info = yf.download(stock, period='1y', interval='1d')
        data = stock_info.reset_index()
        data = data[-7:]

        # print(data)

        response += f"----------{stock}----------\n"
        stock_data.append([stock])
        columns = ['stock']

        Volumes[stock] = stock_info['Volume'].mean()
        Price_action[stock] = stock_info['Close'].diff().mean()

        # for index, row in data (rows iterrated), round close price, format date, 
        for index, row in data.iterrows():
            stock_position = len(stock_data) - 1
            price = round(row['Close'], 2)
            format_date = row['Date'].strftime('%m/%d')
            response += f"{format_date}: {price}\n"
            stock_data[stock_position].append(price)
            columns.append(format_date)
        print()

        emasUsed=[30, 35, 60, 100]

        for x in emasUsed:
            ema=x
            stock_info["Ema_"+str(ema)]=round(stock_info.iloc[:,4].ewm(span=ema, adjust=False).mean(),2)

        df=stock_info.iloc[0:]

        for i in df.index:
            cmin=min(df["Ema_30"][i],df["Ema_35"][i])
            cmax=max(df["Ema_60"][i],df["Ema_100"][i])
            
        if(cmin>cmax):
            response += "\n"+str(stock)+" is in bullish position."

        elif(cmin<cmax):
            response += "\n"+str(stock)+" is in bearish position."

        

        bot.send_message(message.chat.id, response)

# Command message
@bot.message_handler(commands='BR')

# Function to retrieve stock data and send message to telegram
def get_stocks(message):
    stocks = BlackRock_Tracker_list

    for stock in stocks:
        stock_data = []
        response2 = ""

        ## download stock data, format it, get up until a week agos worth of data
        stock_info = yf.download(stock, period='1y', interval='1d')
        data = stock_info.reset_index()
        data = data[-7:]

        ## make 
        stock_data.append([stock])
        columns = ['stock']

        ## calculate average volume and price action
        Volumes[stock] = stock_info['Volume'].mean()
        Price_action[stock] = stock_info['Close'].diff().mean()

        ## calculate max volume and price action
        max_volume = max(Volumes, key=Volumes.get)
        max_action = max(Price_action, key=Price_action.get)
        
        ## build telegram message, adding a newline at end of each string
        response2 += "Highest Avg. Volume(1y):\n" +  max_volume+'\n'
        response2 += "Highest Price Action (1y):\n" +  max_action+ '\n'

    ## send message
    bot.send_message(message.chat.id, response2)

    ## print response to console and not telegram
    # print(response)

    # for stock in stocks - download data, format it, put in response var
    for stock in stocks:
        stock_data = []
        response = ""

        stock_info = yf.download(stock, period='1y', interval='1d')
        data = stock_info.reset_index()
        data = data[-7:]

        # print(data)

        response += f"----------{stock}----------\n"
        stock_data.append([stock])
        columns = ['stock']

        Volumes[stock] = stock_info['Volume'].mean()
        Price_action[stock] = stock_info['Close'].diff().mean()

        # for index, row in data (rows iterrated), round close price, format date, 
        for index, row in data.iterrows():
            stock_position = len(stock_data) - 1
            price = round(row['Close'], 2)
            format_date = row['Date'].strftime('%m/%d')
            response += f"{format_date}: {price}\n"
            stock_data[stock_position].append(price)
            columns.append(format_date)
        print()

        emasUsed=[30, 35, 60, 100]

        for x in emasUsed:
            ema=x
            stock_info["Ema_"+str(ema)]=round(stock_info.iloc[:,4].ewm(span=ema, adjust=False).mean(),2)

        df=stock_info.iloc[0:]

        for i in df.index:
            cmin=min(df["Ema_30"][i],df["Ema_35"][i])
            cmax=max(df["Ema_60"][i],df["Ema_100"][i])
            
        if(cmin>cmax):
            response += "\n"+str(stock)+" is in bullish position."

        elif(cmin<cmax):
            response += "\n"+str(stock)+" is in bearish position."

        

        bot.send_message(message.chat.id, response)

bot.polling()
