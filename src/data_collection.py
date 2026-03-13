import pandas as pd
from cpdb_api import request

# List of countries
country_list = [  "RWA", # Rwanda: Primary case study (Unitary, High Vulnerability)
  "DEU", # Germany: Global North leader (Federal, High Mitigation Stringency)
  "IND", # India: Global South power (Federal, High Growth/Sectoral Complexity)
  "BRA", # Brazil: Land-Use Focus (Federal, High Biodiversity/Adaptation Significance)
  "ZAF", # South Africa: Just Transition Model (Unitary, Coal-to-Green Transition focus)
  "JPN", # Japan: Vulnerable North (Unitary, Technology-led Adaptation)
  "CAN"  # Canada: Federal Resource Exporter (Federal, Mitigation/Adaptation tension)
  ]

def fetch_country_bulk(country):
    print(f"Fetching full history for: {country}")
    
    # Initialize the request
    r = request.Request()
    r.set_country(country)
    r.set_decision_date
    # No date or status filters applied to get the full history
    
    try:
        # Assuming .issue() returns a pandas DataFrame or similar object
        df = r.issue()
        return df
    except Exception as e:
        print(f"Failed for {country}: {e}")
        return None

# Execute the calls and combine results
results = [fetch_country_bulk(c) for c in country_list]

# Filter out None values and concatenate into a single master DataFrame
cpdb_master_df = pd.concat([res for res in results if res is not None], ignore_index=True)

print("Fetch complete.")
