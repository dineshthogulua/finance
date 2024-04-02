# ------------------------------------------------------------------------------------------------------------------
# common_utils.py 
# Description:
#   This is intended to contain miscellaneous functions
# ------------------------------------------------------------------------------------------------------------------

import os
from datetime import datetime
# ------------------------------------------------------------------------------------------------------------------
# is_file_cached
# Description:
#   Throughout the APIs in this project, we need to check if a piece of data we need from some database is already
# cached in the "cache" directory or download it fresh. This function contains that code which would otherwise be
# replicated multiple times throughout the project
# Inputs:
#   file_path: Full OS path to the file
#   days: Max no. of days elpased since the last download (Different data have different thresholds for stale data)
# Output:
#   file_cached: A boolean variable that is True if there is indeed a file in the cache and it is not state and False
# otherwise.
# ------------------------------------------------------------------------------------------------------------------
def is_file_cached(file_path, days):
    file_cached = False
    if os.path.exists(file_path):
        last_modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        if (datetime.now() - last_modified_time).days < days: # We don't think industry classification will change within a week
            file_cached = True

    return(file_cached)