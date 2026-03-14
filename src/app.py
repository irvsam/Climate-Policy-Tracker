import streamlit as st
import pandas as pd
import os
from classifier import PolicyClassifier

# --- CONFIGURATION ---
st.set_page_config(page_title="2026 Climate Tracker", page_icon="🌍")

PATHS = {
    "Logistic Regression": {
        "model": "/Users/sammyirving/tmp/Python - policy tracker/Climate-Policy-Tracker/notebooks/logreg_model.joblib",
        "vec": "/Users/sammyirving/tmp/Python - policy tracker/Climate-Policy-Tracker/notebooks/logreg_vectorizer.joblib"
    },
    "K-Nearest Neighbors": {
        "model": "/Users/sammyirving/tmp/Python - policy tracker/Climate-Policy-Tracker/notebooks/knn_model.joblib",
        "vec": "/Users/sammyirving/tmp/Python - policy tracker/Climate-Policy-Tracker/notebooks/knn_vectorizer.joblib"
    }
}

# --- LOAD SELECTED MODEL ---
st.sidebar.title("Settings")
model_choice = st.sidebar.radio("Choose Classifier:", list(PATHS.keys()))

@st.cache_resource
def get_engine(choice):
    return PolicyClassifier(PATHS[choice]["model"], PATHS[choice]["vec"])

engine = get_engine(model_choice)

# --- UI SCREEN ---
st.title("2026 Climate Policy Tracker")
st.write(f"Currently using: **{model_choice}**")

with st.form("policy_input"):
    name = st.text_input("Policy Name")
    description = st.text_area("Policy Description")
    submitted = st.form_submit_button("Classify Policy")

if submitted and description:
    # Get Prediction
    result = engine.predict(name, description)
    
    st.subheader(f"Result: {result['prediction'].upper()}")
    st.write(f"**Confidence Score:** {result['confidence']}")
    
    # Store in session state for feedback logic
    st.session_state['last_policy'] = {"name": name, "desc": description, "pred": result['prediction']}

# --- FEEDBACK LOOP ---
# Define a clear, absolute path for your corrections
CORRECTIONS_FILE = os.path.join(os.getcwd(), "corrections.csv")

if 'last_policy' in st.session_state:
    st.divider()
    st.write("### Help the Model Learn")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Correct"):
            # Even for 'Correct' answers, we save them to build a 'Gold Standard' dataset
            new_row = pd.DataFrame([{
                "text_features": f"{st.session_state['last_policy']['name']} {st.session_state['last_policy']['desc']}",
                "classification": st.session_state['last_policy']['pred'],
                "verified": "True"
            }])
            new_row.to_csv(CORRECTIONS_FILE, mode='a', header=not os.path.exists(CORRECTIONS_FILE), index=False)
            st.success("Verified and Saved!")
            del st.session_state['last_policy']
            st.rerun() 
            
    with col2:
        if st.button("Incorrect"):
            st.session_state['show_correction'] = True

    if st.session_state.get('show_correction'):
        true_label = st.selectbox("Correct label?", ["adaptation", "mitigation", "both"])
        if st.button("Confirm & Save"):
            new_row = pd.DataFrame([{
                "text_features": f"{st.session_state['last_policy']['name']} {st.session_state['last_policy']['desc']}",
                "classification": true_label,
                "verified": "False"
            }])
            
            # Force the save to disk
            new_row.to_csv(CORRECTIONS_FILE, mode='a', header=not os.path.exists(CORRECTIONS_FILE), index=False)
            
            st.info(f"Correction saved to: {CORRECTIONS_FILE}")
            
            # Reset state and Move On
            del st.session_state['last_policy']
            st.session_state['show_correction'] = False
            st.rerun()