# ------------------------------------------------------------------------------------------------------------------
# company_benchmarking.py 
# Description:
#   We compare a company's performance to its peers in the code. Examples of performance indicators we use for the 
# comparison are gross margin, revenue growth and SG&A margin
# ------------------------------------------------------------------------------------------------------------------
import sys

sys.path.append("../")
from edgar_utils import ticker_to_cik, get_companywide_concepts
from adamodaran_utils import extract_industry_tickers

company = "CROX"    # Ticker of the company which we wish to benchmark against a peer group

# Create a list that contains the target company and its peers
industry = "Shoe"   # A good starting point to look for peer companies is to look into the players in the same industry
ticker_list = extract_industry_tickers(list(industry))  # This will automatically contain (hopefully) the company in 
                                                        # question. But we do a sanity check nevertheless.
if company not in ticker_list:
    sys.exit("Critical error: The company is not in the industry list!! Exiting code")
cik_str_list = ticker_to_cik(ticker_list)

concepts_of_interest = ["AccountsPayableCurrent", "ResearchAndDevelopmentExpense"]

