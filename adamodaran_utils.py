# ------------------------------------------------------------------------------------------------------------------
# adamodaran_utils.py 
# Description:
#   This file contains all the API code for accessing data from Prof. Aswath Damodaran's website
# ------------------------------------------------------------------------------------------------------------------

import sys
import os
import pandas as pd
import requests
from common_utils import is_file_cached

# ------------------------------------------------------------------------------------------------------------------
# extract_industry_tickers
# Description:
#   The function collects the stock tickers for all the U.S. companies that belong to one or more industries.
# The industry names are based on Prof. Damodaran's classification of industries( which can be found here: 
# https://www.stern.nyu.edu/~adamodar/pc/datasets/indname.xls) and not other methods such # as SIC code. In 
# general it is better to use Professor's classification as it is based on careful study of what the company's
# do 
# Inputs
#   industry_list: A python list of industry names
# Output
#   ticker_list: A list of stock tickers corresponding to all the companies that belong to all the industries
# user supplied in the input
# ------------------------------------------------------------------------------------------------------------------
def extract_industry_tickers(industry_list):
    local_dir_name = os.path.dirname(__file__)
    indname_file_path = local_dir_name + "\\cache\\" + "indname.xls"
              
    if is_file_cached(indname_file_path, 7) == False: # We don't expect industry company name lists to change in a week
        resp = requests.get("https://www.stern.nyu.edu/~adamodar/pc/datasets/indname.xls", verify=False)
        with open(indname_file_path, "wb") as f:  
            f.write(resp.content) 

    industry_df = pd.read_excel(indname_file_path, sheet_name="US by industry")
    valid_industry_values = industry_df["Industry Group"].unique()

    # Sanity check
    if not set(industry_list).issubset(set(valid_industry_values)):
        print("One or more industry values you input is wrong. The following are valid values")
        for indname in valid_industry_values:
            print(indname)
        sys.exit("Input Error")

    exchange_ticker_list = list(industry_df.loc[industry_df["Industry Group"].isin(industry_list), 'Exchange:Ticker'])   # Extract only rows that correspond 
                                                                                                # to the industries we are interested in  
    ticker_list = list(map(lambda s:s.split(":")[1], exchange_ticker_list))
    return(ticker_list)

print("Dummy")