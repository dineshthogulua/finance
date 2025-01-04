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
# get_raw_industry_df
# Description: Basically converts the excel sheet for US companies in Prof. Damodaran's indname.xlsx data
# 
# Inputs
#   None
# Output
#   industry_df: A pandas dataframe containing columns such as company name, tickers, industry the belong to etc.
# ------------------------------------------------------------------------------------------------------------------
def get_raw_industry_df():
    local_dir_name = os.path.dirname(__file__)
    indname_file_path = local_dir_name + "\\cache\\" + "indname.xlsx"
              
    if is_file_cached(indname_file_path, 7) == False: # We don't expect industry company name lists to change in a week
        resp = requests.get("https://www.stern.nyu.edu/~adamodar/pc/datasets/indname.xlsx", verify=False)
        with open(indname_file_path, "wb") as f:  
            f.write(resp.content) 

    industry_df = pd.read_excel(indname_file_path, sheet_name="US by industry")
    return(industry_df)


# ------------------------------------------------------------------------------------------------------------------
# extract_industry_tickers
# Description:
#   The function collects the stock tickers for all the U.S. companies that belong to one or more industries.
# The industry names are based on Prof. Damodaran's classification of industries( which can be obtained by using 
# the get_industry_list utility function) and not other methods such # as SIC code. In general it is better to use
# Professor's classification as it is based on careful study of what the company's actually do
#
# Inputs
#   industry_list: A python list of industry names
# Output
#   ticker_list: A list of stock tickers corresponding to all the companies that belong to all the industries
# user supplied in the input
# ------------------------------------------------------------------------------------------------------------------
def extract_industry_tickers(industry_list):
    industry_df = get_raw_industry_df()
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

# ------------------------------------------------------------------------------------------------------------------
# get_industry_list
# Description:
#   The function gathers the industry names as Prof. Damodaran uses. 
# Inputs
#   None
# Output
#   indlist = A list of industry names
# ------------------------------------------------------------------------------------------------------------------
def get_industry_list():
    industry_df = get_raw_industry_df()
    indlist = industry_df["Industry Group"].unique()
    return(indlist)

# ------------------------------------------------------------------------------------------------------------------
# get_sector_list
# Description:
#   The function gathers sectors different companies in an industry serve. Remember that, most often, the same sector
# would be connected to several industries. For instance, some companies in the "Apparel" industry as well as the
# "Autoparts" industry are both connected to the "Consumer Discretionary" sector. 
# Inputs
#   industry: The name of the industry as a string. To get a list of industries, use get_industry_list()
# Output
#   sectorlist = A list of sector names
# ------------------------------------------------------------------------------------------------------------------
def get_sector_list(industry):
    industry_df = get_industry_df()
    sectorlist = industry_df[industry_df.industry==industry]['sector'].unique()
    return(sectorlist)

# ------------------------------------------------------------------------------------------------------------------
# get_industry_df
# Description:
#   The function collects the company names, stock tickers, industry group, primary sector format for all the U.S. 
# companies that belong to one or more industries. The industry names are based on Prof. Damodaran's classification  
# of industries( which can be obtained by using the get_industry_list utility function) and not other methods such # 
# as SIC code. In general it is better to useProfessor's classification as it is based on careful study of what the 
# company's actually do
#
# Inputs
#   industry_list: A python list of industry names. This input is optional. If not provided, data is returned for 
#                  industries.
#   no_pink: Tells the function to discard pink sheet stocks
# Output
#   industry_df: A pandas data frame containing the following columns:
#       'company_name': The name of the company
#       'exchange': NYSE, NASDAQ etc. (extended exchange tag, like "NASDAQGS")
#       '
# user supplied in the input
# ------------------------------------------------------------------------------------------------------------------
def get_industry_df(industry_list=None, no_pink=True):
    rawdf = get_raw_industry_df()
    rawdf.drop(columns=['Country', 'Broad Group', 'Sub Group'], inplace=True)
    if no_pink:
        subdf = rawdf[rawdf['Exchange:Ticker'].str.contains("OTCPK")==False]
    else:
        subdf = rawdf.copy()

    del rawdf
    if industry_list is None:
        industry_df = subdf.copy()
    else:
        industry_df = subdf.loc[subdf["Industry Group"].isin(industry_list)]

    del subdf
    
    industry_df[['exchange', 'ticker']] = industry_df['Exchange:Ticker'].str.split(":", expand=True)
    industry_df.drop(columns=['Exchange:Ticker'],inplace=True)
    industry_df.rename(columns={'Company Name':'company', 'Industry Group':'industry', 'Primary Sector':'sector'}, inplace=True)

    return(industry_df)

# ------------------------------------------------------------------------------------------------------------------
# get_industry_and_sector
# Description:
#   For a given company ticker, returns the industry and sector that company belongs to
# Inputs
#   company ticker as a string. Ex. "MSFT"
# Output
#   [industry, sector] as a python list
# ------------------------------------------------------------------------------------------------------------------
def get_industry_and_sector(ticker):
    industry_df = get_industry_df()
    industry = industry_df[industry_df.ticker == ticker].iloc[0]['industry']
    sector = industry_df[industry_df.ticker == ticker].iloc[0]['sector']
    return([industry, sector])