# ------------------------------------------------------------------------------------------------------------------
# company_filters.py
# Author: Dinesh Thogulua
# Description:
#   Investors are spoilt for choice: There are thousands of publicly traded companies. But the can only actively
# invest in a handful of companies. This file is a collection of filters, with each filter being a function, that 
# will help an investor narrow down the list of companies 
# ------------------------------------------------------------------------------------------------------------------

import pandas as pd
from adamodaran_utils import get_industry_df

# ------------------------------------------------------------------------------------------------------------------
# filter_by_market_share
# Inputs
#   industry: 
#   The industry name as a string. This is a mandatory input. The industry name is based on 
#   Prof. Damodaran's classification of industries. Use get_industry_list function in adamodaran_utils.py to find out
#   the names.
#   Ex: "Retail (Special Lines)"
#
#   top_share_percentage: 
#   The topmost pertage of market share within which the passing companies must fall, as a percentage figure. This is 
#   an optional input. The default value is 33 (i.e., 33% or roughly the top 1/3rd of companies)
#
#   sector: 
#   This is the sector that you want to focus on, as a string. This is an optional input.
#   Ex: "Consumer Discretionary"
#
# Output
#   A dataframe consisting of the following details for the top players in the industry and/or sector by market share.
#   company_name
#   company_ticker
#   market_share
# ------------------------------------------------------------------------------------------------------------------
def filter_by_market_share(industry, top_share_percentage=33, sector=None):
    industry_df = get_industry_df()

    if sector is None:
        subdf = industry_df[industry_df.industry==industry]
    else:
        subdf = industry_df[(industry_df.industry==industry) & (industry_df.sector==sector)]

    

