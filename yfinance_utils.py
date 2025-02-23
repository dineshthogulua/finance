# ------------------------------------------------------------------------------------------------------------------
# yfinance_utils.py
# Author: Dinesh Thogulua
# Description:
#   Contains utility functions using yfinance library
# ------------------------------------------------------------------------------------------------------------------

import requests
import json
import pandas as pd
import yfinance as yf

from requests import Session
from requests_cache import CacheMixin, SQLiteCache
from requests_ratelimiter import LimiterMixin, MemoryQueueBucket
from pyrate_limiter import Duration, RequestRate, Limiter
import os
from common_utils import is_file_cached

# Set up the environment
yf.set_tz_cache_location("../cache/yfinance")
pd.set_option('display.width', 1000)
class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
   pass

session = CachedLimiterSession(
   limiter=Limiter(RequestRate(2, Duration.SECOND*5)),  # max 2 requests per 5 seconds
   bucket_class=MemoryQueueBucket,
   backend=SQLiteCache("../cache/yfinance/yfinance.cache"),
)
session.headers['User-agent'] = 'my-program/1.0'

# get_historical_returns ---------------------------------------------------------------------------------------------------------------
#   Returns the total anualized returns in percentage for a given ticker and no. of years. The no. of years defaults to 10
# --------------------------------------------------------------------------------------------------------------------------------------
def get_historical_returns(ticker, no_of_years = 10):
    try:
        price_df = yf.download(ticker, period="1d", session=session,progress=False)
        if price_df.empty:
            return(None)
    except:
        return(None)
    end_date = price_df.index[0]
    start_date = end_date - pd.DateOffset(years=no_of_years+1)  # We need 11 years of data to be able to calculate 10 years of returns

    try:
        data = yf.download(ticker, start=start_date, end=end_date, interval="3mo", progress=False)
        if data.empty:
            return(None)
    except:
        return(None)
    price_data = data['Adj Close'].resample("YE").last()
    total_annual_return = price_data.pct_change()*100
    total_annual_return.drop(index=total_annual_return.index[0], inplace=True)
    return(total_annual_return)
