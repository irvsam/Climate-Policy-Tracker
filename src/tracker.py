from classifier import PolicyClassifier

path_to_logreg_model = '/Users/sammyirving/tmp/Python - policy tracker/Climate-Policy-Tracker/notebooks/logreg_model.joblib'
path_to_logreg_vectorizer = '/Users/sammyirving/tmp/Python - policy tracker/Climate-Policy-Tracker/notebooks/logreg_vectorizer.joblib'  
path_to_knn_model = '/Users/sammyirving/tmp/Python - policy tracker/Climate-Policy-Tracker/notebooks/knn_model.joblib'
path_to_knn_vectorizer = '/Users/sammyirving/tmp/Python - policy tracker/Climate-Policy-Tracker/notebooks/knn_vectorizer.joblib'

# Instantiate both models
logreg_engine = PolicyClassifier(path_to_logreg_model, path_to_logreg_vectorizer)
knn_engine = PolicyClassifier(path_to_knn_model, path_to_knn_vectorizer)

# New Policy
new_policy = {
    "name": "Mekong Delta Dike Expansion",
    "desc": "Coastal engineering to prevent saltwater intrusion into rice paddies."
}

# Get predictions from both
res_log = logreg_engine.predict(new_policy['name'], new_policy['desc'])
res_knn = knn_engine.predict(new_policy['name'], new_policy['desc'])

print(f"LogReg says: {res_log['prediction']} ({res_log['confidence']})")
print(f"KNN says: {res_knn['prediction']} ({res_knn['confidence']})")