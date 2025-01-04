# ------------------------------------------------------------------------------------------------------------------
# edgar_utils.py
# Author: Dinesh Thogulua
# Description:
#   This contains some utility functions that use SEC's EDGAR APIs to extract financial information directly from 
# SEC's database, curates them and returns information in forms that are suitable for further manipulation using
# python code. 
#   Note: You don't need an API key to access EDGAR database. For reference, you can got throught their API 
# documentation: https://www.sec.gov/edgar/sec-api-documentation
# ------------------------------------------------------------------------------------------------------------------

import requests
import json
import pandas as pd
import os
from common_utils import is_file_cached

# ------------------------------------------------------------------------------------------------------------------
# tickers_to_ciks
# Inputs
#   ticker: Stock tickers of the company of interest. Ex: 'AAPL'
# Output
#   cik: The CIK number for that company (as a 10 digit string)
# ------------------------------------------------------------------------------------------------------------------
def ticker_to_cik(ticker):
    local_dir_name = os.path.dirname(__file__)
    file_path = local_dir_name + "\\cache\\" + "ticker_to_cik.csv"
    if is_file_cached(file_path, 7) == False:   # If the data is not in the cache, get it from the SEC database
        headers = {'User-Agent': 'Fordham University sthoguluachandraseka@fordham.edu', 'Accept-Encoding': 'gzip,deflate', 'Host':'www.sec.gov'}
        resp = requests.get("https://www.sec.gov/files/company_tickers.json", headers=headers)
        try:
            map_dict = json.loads(resp.text)   
        except:
            return None   # Return None in case of an error
        
        map_df = pd.DataFrame.from_dict(map_dict, orient="index")
        map_df.sort_values(by='ticker', inplace=True)
        map_df.to_csv(file_path, index=False)
    else:   # If the data is indeed in the cache, just take it from it. 
        map_df = pd.read_csv(file_path)

    map_df.set_index('ticker', inplace=True)
    cik_temp = map_df.loc[ticker, 'cik_str']
    cik = str(cik_temp).zfill(10)    # Pad with leading zeros so that the string is 10 characters long

    return (cik)


# ------------------------------------------------------------------------------------------------------------------
# tickers_to_ciks
# Inputs
#   ticker_list: A list of stock tickers of companies interested in. Ex: ['AAPL', 'MSFT','NVDA']
# Output
#   cik_list: A list of corresponding CIK values (as a 10 digit string)
# ------------------------------------------------------------------------------------------------------------------
def tickers_to_ciks(ticker_list):
    local_dir_name = os.path.dirname(__file__)
    file_path = local_dir_name + "\\cache\\" + "ticker_to_cik.csv"
    if is_file_cached(file_path, 7) == False:
        headers = {'User-Agent': 'Fordham University sthoguluachandraseka@fordham.edu', 'Accept-Encoding': 'gzip,deflate', 'Host':'www.sec.gov'}
        resp = requests.get("https://www.sec.gov/files/company_tickers.json", headers=headers)
        try:
            map_dict = json.loads(resp.text)   
        except:
            return []   # Return an empty list in case of an error

        map_df = pd.DataFrame.from_dict(map_dict, orient="index")
        map_df.sort_values(by='ticker', inplace=True)
        map_df.to_csv(file_path, index=False)
    else:
        map_df = pd.read_csv(file_path)

    cik_list = list(map_df.loc[map_df['ticker'].isin(ticker_list),'cik_str'])
    cik_str_list = [str(ele).zfill(10) for ele in cik_list]

    return cik_str_list


# ------------------------------------------------------------------------------------------------------------------
# get_financial_item 
# Description
#   Gets the values of a financial item for a company across time
# Inputs
#   ticker: 
#       Company stock ticker
#   concept_of_interest: 
#       IS/BS/CFS item in standard EDGAR terminology. Example: "AccountsPayableCurrent"
#       Tip: To find out the EDGAR standard terms go to https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json . -
#       You will see the latest financial data of Apple. You can scan through it to identify the EDGAR standard term for 
#       whatever financial item you are looking for
# Output
#   data_df: A data frame that contains quarterly, annual values of the concept_of_interest for several years
# ------------------------------------------------------------------------------------------------------------------
def get_financial_item(ticker, concept_of_interest):
    local_dir_name = os.path.dirname(__file__)
    file_path = local_dir_name + "\\cache\\" +ticker+"_"+concept_of_interest+".csv"
    if is_file_cached(file_path, 30) == False:   # If the data is not in the cache, get it from the SEC database
        cik_str = ticker_to_cik(ticker)
        headers = {'User-Agent': 'Fordham University sthoguluachandraseka@fordham.edu', 'Accept-Encoding': 'gzip,deflate', 'Host':'data.sec.gov'}
        URL = "https://data.sec.gov/api/xbrl/companyconcept/CIK"+cik_str+"/us-gaap/"+ concept_of_interest+".json"
        resp = requests.get(URL, headers=headers)
        try:
            data_dict = json.loads(resp.text)   
        except:
            return []   # Return an empty list in case of an error
    
        data_df = pd.DataFrame.from_dict(data_dict['units']['USD']).dropna()
        fin_df = data_df[~data_df.frame.str.contains("Q")][['end','val']]
        fin_df['date'] = pd.to_datetime(fin_df['end'], format="%Y-%m-%d")
        fin_df['year'] = fin_df['date'].dt.year
        fin_df.rename(columns={'val':'value'}, inplace=True)
        fin_df.drop(columns=['end'], inplace=True)
        fin_df.set_index('year', inplace=True)
        fin_df.to_csv(file_path, index=True)
    else:
        fin_df = pd.read_csv(file_path, index_col=[0])

    return(fin_df)

# ------------------------------------------------------------------------------------------------------------------
# get_revenue
# Description
#   
# ------------------------------------------------------------------------------------------------------------------

#   
# ------------------------------------------------------------------------------------------------------------------
# get_companywide_concepts(cik_str_list, concepts_of_interest)
#   Gets the values of a financial item for several companies (annual, not quarterly) across time
# Inputs
#   ticker_list: 
#       A list of company tickers Example: ["AAPL", "NVDA"] 
#   concepts_of_interest: 
#       A list of IS/BS/CFS items in standard EDGAR terminology. 
#       Example: ["AccountsPayableCurrent", "ResearchAndDevelopmentExpense"]
#       Tip:  See the description of get_financial_item to figure out how to find standard term for a concept 
#       item of interest
# Output
#   all_companies_dict = A dictionary that has a dataframe for each company with company CIK as the key. The dataframe 
#   for each company has three columns: concept, end and val, several years of data. 
# ------------------------------------------------------------------------------------------------------------------
def get_companywide_concepts(ticker_list, concepts_of_interest):
    all_companies_dict = dict.fromkeys(ticker_list, None)
    for company in all_companies_dict:  # EDGAR APIs are built around individual companies. We have to fetch data one company at a time
        headers = {'User-Agent': 'Fordham University sthoguluachandraseka@fordham.edu', 'Accept-Encoding': 'gzip,deflate', 'Host':'data.sec.gov'}
        URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK"+ticker_to_cik(company)+".json"
        resp = requests.get(URL, headers=headers)
        try:
            data_dict = json.loads(resp.text)   
        except:
            continue    # We skip that company

        concept_dict = dict.fromkeys(concepts_of_interest, None)
        for concept in concepts_of_interest:    
            company_fin_df = pd.DataFrame.from_dict(data_dict['facts']['us-gaap'][concept]['units']['USD'])
            temp_df = company_fin_df.loc[company_fin_df['form'] == "10-K", ['end','val','frame']].dropna()
                                                                                # 'frame' variable tells whether the data was found in a 10K or 10Q or something else.
                                                                                # By using "dropna" we take care of removing data from something other than a 10K/Q. 
                                                                                # Then we extract just the figures from the 10-K values because 
                                                                                # we don't care about 10-Q data for this function.  
            concept_dict[concept] = temp_df[~temp_df.frame.str.contains("Q")][['end','val']]
            concept_dict[concept]['end'] = pd.to_datetime(concept_dict[concept]['end']) # We want the 'end' to be a datetime variable 
        company_facts_df = pd.concat(concept_dict, axis=0)  # We want to convert the dictionary we created into a dataframe and do some clean up
        company_facts_df.reset_index(inplace=True) 
        company_facts_df.drop(columns=['level_1'], inplace=True)
        company_facts_df.rename(columns = {'level_0':'concept'}, inplace=True)
        all_companies_dict[company] = company_facts_df

    return(company_facts_df)