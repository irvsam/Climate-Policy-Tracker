import joblib
import re

class PolicyClassifier:
    def __init__(self, model_path, vectorizer_path):
        self._clf = joblib.load(model_path)
        self._vectorizer = joblib.load(vectorizer_path)

    def _preprocess(self, text):
        # For text cleaning
        text = str(text).lower()
        text = re.sub(r'\b\d{4}\b', '', text) # Remove years
        return text

    def predict(self, name, description):
        """
        Pass a policy, get a prediction.
        """
        raw_text = f"{name} {description}"
        cleaned_text = self._preprocess(raw_text)
        
        # Transform the text using the loaded vectorizer
        vector = self._vectorizer.transform([cleaned_text])
        
        # Get prediction and probability
        label = self._clf.predict(vector)[0]
        prob = self._clf.predict_proba(vector).max()
        
        return {
            "prediction": label,
            "confidence": f"{prob:.2%}",
            "model_type": type(self._clf).__name__
        }