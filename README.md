This repo is a intended to be a collection of APIs that make it easier to interface with finance related databases such as EDGAR, AlphaVantage etc. 

## Guidelines
  1. Please add comments in the code for all the non obvious sections of the code so others can interpret what you are trying to do
  2. Please ensure that the every file has a top header that describes at a high level what all the code in the file is about. For all the functions, add descriptions, input(s) and output(s)
  3. If the data you are accessing from a web resource is large or takes a long time to download, consider implementing a way of saving the data in cache and retrieving it from the cache instead of always accessing the web resource (But make sure you check if the data is stale before returning it to the user). For example, check extract_industry_tickers in adamodaran_utils.py