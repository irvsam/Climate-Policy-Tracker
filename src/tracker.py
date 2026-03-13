import pandas as pd
import os
from cpdb_api import request

from classifyer import classify_policy

# Configuration
DB_FILE = "cpdb_master.csv"
COUNTRIES = [  "RWA", # Rwanda: Primary case study (Unitary, High Vulnerability)
  "DEU", # Germany: Global North leader (Federal, High Mitigation Stringency)
  "IND", # India: Global South power (Federal, High Growth/Sectoral Complexity)
  "BRA", # Brazil: Land-Use Focus (Federal, High Biodiversity/Adaptation Significance)
  "ZAF", # South Africa: Just Transition Model (Unitary, Coal-to-Green Transition focus)
  "JPN", # Japan: Vulnerable North (Unitary, Technology-led Adaptation)
  "CAN"  # Canada: Federal Resource Exporter (Federal, Mitigation/Adaptation tension)
  ]


def fetch_latest_from_api():
    """Fetches full history for countries."""
    all_data = []
    for country in COUNTRIES:
        print(f"Fetching data for: {country}")
        r = request.Request()
        r.set_country(country)
        try:
            df = r.issue()
            if df is not None: all_data.append(df)
        except Exception as e:
            print(f"Failed {country}: {e}")
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

def main():
    # Load History
    if os.path.exists(DB_FILE):
        current_df = pd.read_csv(DB_FILE)
        current_ids = set(current_df['policy_id'].astype(str))
    else:
        current_df = pd.DataFrame()
        current_ids = set()

    # Fetch New
    new_api_df = fetch_latest_from_api()
    if new_api_df.empty: return

    # Compare using IDs 
    new_entries = new_api_df[~new_api_df['policy_id'].astype(str).isin(current_ids)].copy()

    if not new_entries.empty:
        print(f"Found {len(new_entries)} new policies")
        
        # Classify ONLY the new ones
        new_entries['classification'] = new_entries.apply(classify_policy, axis=1)
        
        # Save/Merge
        updated_df = pd.concat([current_df, new_entries], ignore_index=True)
        updated_df.to_csv(DB_FILE, index=False)
        print("Database updated.")
    else:
        print(" No new policies found.")

if __name__ == "__main__":
    main()