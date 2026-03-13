# Once we find a new policy we need to use the following logic to classify whether a policy is likely to be regressive or progressive. 
# This is a very simple logic and needs to be improved later

from turtle import pd


def classify_policy(policy):
    """Classifies a policy as regressive, progressive, or neutral based on its characteristics."""
   
    filepath = "../data/cpdb_master_df.csv"
    cpdb_master_df = pd.read_csv(filepath)
    # find the row of given policy in the dataframe
    policy_row = cpdb_master_df[cpdb_master_df['policy_name'] == policy]

    # Combine the three fields into one searchable string
    text_blob = f"{policy_row['policy_name']} {policy_row['policy_instrument']} {policy_row['policy_description']}".lower()
    
    # Define weights
    progressive_terms = {
        'subsidy': 2, 'grant': 2, 'investment': 1, 'social': 3, 
        'rebate': 2, 'low-income': 3, 'public transit': 2, 'fund': 1
    }
    
    regressive_terms = {
        'tax': 2, 'levy': 2, 'carbon price': 2, 'fee': 1, 
        'duty': 2, 'excise': 2, 'removal': 1
    }
    
    score = 0
    
    # Calculate score
    for term, weight in progressive_terms.items():
        if term in text_blob:
            score += weight
            
    for term, weight in regressive_terms.items():
        if term in text_blob:
            score -= weight

    # Return classification
    if score > 0:
        return "Likely Progressive"
    elif score < 0:
        return "Likely Regressive"
    else:
        return "Neutral/Unclassified"
