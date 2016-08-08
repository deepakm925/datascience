# -*- coding: utf-8 -*-
"""
Created on Sat Aug  6 22:17:36 2016

@author: donaldfung
"""

""" Retrieve and process raw data and create csv and sqlite database"""

from yahoo_finance import Share
import quandl
import settings
import plots
import computations
import prepare
import pandas as pd
import sqlite3

def get_data():
    # check if csv exists
    closing_prices = settings.closing_prices_data + settings.csv
    try:
        data = pd.read_csv(closing_prices, index_col = "Unnamed: 0")
        print "successfully loaded closing prices!"
        return data
    except:
        print "no csv file"
        
    # Define data range
    start_date = settings.start_date
    end_date = settings.end_date
    dates = pd.date_range(start_date, end_date)
    # create empty dataframe with dates as index
    closing_prices = pd.DataFrame(index = dates)
    # dataframe of company name, ticker and industry
    companies = pd.read_csv(settings.companies_abridged)
    tickers = companies["Symbol"]
    name = companies["Name"]
    companies = dict(zip(name, tickers))
    # active data source
    datasource = settings.active_datasource
    
    for name, ticker in companies.items():
        print "getting stock data"
        try:
            data = get_data_from_datasource(datasource, ticker, start_date, end_date)
            closing_prices = adjusted_close(closing_prices, data, ticker, provider = datasource)
        except:
            print "Error getting data for ", name, ticker
    # fill in empty values
    closing_prices = prepare.fill_missing_values(closing_prices)
    # save dataframe
    save_dataframe(closing_prices)
    print "csv successfully saved!"
    # save database
    #create_database(closing_prices)
    #print "databased successfully saved!"  
    return closing_prices
    
def get_data_from_datasource(provider, ticker, start_date, end_date):
    if provider == "Yahoo":
        yahoo = Share(ticker)
        historical_data = yahoo.get_historical(start_date, end_date)
        return historical_data
    elif provider == "Quandl":
        endpoint = settings.stock_price_code + ticker
        quandl.ApiConfig.api_key = settings.api_key
        data = quandl.get(endpoint, start_date = start_date, end_date = end_date)
        return data
        
def save_dataframe(df = None):
    closing_prices = settings.closing_prices_data + settings.csv
    df.to_csv(closing_prices, sep=',', encoding='utf-8')

def create_database(df = None):
    closing_prices = settings.closing_prices_data + settings.sql
    conn = sqlite3.connect(closing_prices)
    df.to_sql(closing_prices, conn)
    
def adjusted_close(df1, df2, ticker, provider):
    if provider == "Yahoo":
        # extract adjusted closing price 
        columns = ["Date", "Adj_Close"]
        df_temp = pd.DataFrame(df2, columns=columns)
        df_temp = df_temp.rename(columns = {"Adj_Close": ticker})
        # set index to be the date column
        df_temp = df_temp.set_index("Date")
        # join dataframes
        df1 = df1.join(df_temp, how = 'inner')
        # drop rows with NaN values
        #df1 = df1.dropna()
        df1 = prepare.fill_missing_values(df1)
    elif provider == "Quandl":
        columns = ["Adj. Close"]
        df_temp = pd.DataFrame(df2, columns=columns)
        df_temp = df_temp.rename(columns = {"Adj. Close": ticker})
        df1 = df1.join(df_temp, how = 'outer')
    return df1
    
data = get_data()
#print data
#print data.median()
#plots.plot_rolling_mean(dataframe = data, ticker = "AAL", window = 20)
#plots.plot_stock_price_data(data)
#returns = computations.compute_daily_returns(data)
#data = computations.normalize_data(data)
#cum_returns = computations.compute_cumulative_returns(data, time = -20)
#print cum_returns