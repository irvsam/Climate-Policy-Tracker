import pandas as pd
import os
from cpdb_api import request

# --- CONFIGURATION ---
DB_FILE = "cpdb_master.csv"
COUNTRY_LIST = ["RWA", "DEU", "IND", "BRA", "ZAF", "JPN", "CAN"]
SIMULATION_CUTOFF = 2023  # Everything before this is "Old", after is "New"

# --- CLASSIFIER ---
def classify_policy_row(row):
    """
    Improved classifier that takes a row directly from the pipeline.
    This avoids reloading the CSV for every single row.
    """
    # Combine fields
    name = str(row.get('policy_name', ''))
    inst = str(row.get('policy_instrument', ''))
    desc = str(row.get('policy_description', ''))
    text_blob = f"{name} {inst} {desc}".lower()
    
    progressive_terms = {
        'subsidy': 2, 'grant': 2, 'investment': 1, 'social': 3, 
        'rebate': 2, 'low-income': 3, 'public transit': 2, 'fund': 1
    }
    regressive_terms = {
        'tax': 2, 'levy': 2, 'carbon price': 2, 'fee': 1, 
        'duty': 2, 'excise': 2, 'removal': 1
    }
    
    score = 0
    for term, weight in progressive_terms.items():
        if term in text_blob: score += weight
    for term, weight in regressive_terms.items():
        if term in text_blob: score -= weight

    if score > 0: return "Likely Progressive"
    elif score < 0: return "Likely Regressive"
    return "Neutral/Unclassified"

# --- CORE LOGIC ---
def fetch_all_api_data():
    """Fetches full history for all countries in the list."""
    all_data = []
    for country in COUNTRY_LIST:
        print(f"Fetching data from API for: {country}")
        r = request.Request()
        r.set_country(country)
        try:
            df = r.issue()
            if df is not None: 
                # Ensure decision_date is datetime for filtering
                df['decision_date'] = pd.to_datetime(df['decision_date'], errors='coerce')
                all_data.append(df)
        except Exception as e:
            print(f"Failed for {country}: {e}")
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

def run_simulation():
    # Clear old DB if it exists for a fresh simulation
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"Cleaned up old {DB_FILE} for simulation.")

    # FETCH EVERYTHING
    full_df = fetch_all_api_data()
    if full_df.empty: return

    # CREATE HISTORICAL BASELINE (Policies < 2023)
    print(f"\n--- STEP 1: Creating Baseline (Pre-{SIMULATION_CUTOFF}) ---")
    baseline_df = full_df[full_df['decision_date'].dt.year < SIMULATION_CUTOFF].copy()
    
    # Pre-classify the baseline so the DB is complete
    baseline_df['classification'] = baseline_df.apply(classify_policy_row, axis=1)
    baseline_df.to_csv(DB_FILE, index=False)
    print(f"Baseline saved with {len(baseline_df)} policies.")

    # 4. RUN TRACKER (Policies >= 2023)
    print(f"\n--- STEP 2: Running Tracker for New Policies ({SIMULATION_CUTOFF}+) ---")
    
    # Reload DB to simulate a real "Tracking" environment
    current_df = pd.read_csv(DB_FILE)
    current_ids = set(current_df['policy_id'].astype(str))

    # Identify "New" policies (those from 2023 onwards)
    new_entries = full_df[~full_df['policy_id'].astype(str).isin(current_ids)].copy()

    if not new_entries.empty:
        print(f"ALERT: Found {len(new_entries)} NEW policies")
        
        # Classify only the new entries
        new_entries['classification'] = new_entries.apply(classify_policy_row, axis=1)
        
        for _, row in new_entries.iterrows():
            print(f"  • New Policy in {row['country']}: {row['policy_name']} -> {row['classification']}")

        # Final Merge
        final_df = pd.concat([current_df, new_entries], ignore_index=True)
        final_df.to_csv(DB_FILE, index=False)
        print(f"Workflow complete. Master DB now contains {len(final_df)} policies.")
    else:
        print("No newer policies found.")

if __name__ == "__main__":
    run_simulation()