import pandas as pd
import re
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Load data
df = pd.read_csv("data/IMDB Dataset.csv")

# Basic cleaning
def clean_text(text):
    text = re.sub(r'<.*?>', ' ', text)          # remove HTML tags
    text = re.sub(r'[^a-zA-Z\s]', '', text)      # keep only letters
    text = text.lower().strip()
    return text

df['clean_review'] = df['review'].apply(clean_text)
df['label'] = df['sentiment'].map({'positive': 1, 'negative': 0})

X_train, X_test, y_train, y_test = train_test_split(
    df['clean_review'], df['label'], test_size=0.2, random_state=42
)

# Vectorize
vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Train
model = LogisticRegression(max_iter=1000)
model.fit(X_train_vec, y_train)

# Evaluate
preds = model.predict(X_test_vec)
print("Accuracy:", accuracy_score(y_test, preds))
print(classification_report(y_test, preds))

# Save model + vectorizer
with open("models/sentiment_model.pkl", "wb") as f:
    pickle.dump(model, f)
with open("models/sentiment_vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

print("Sentiment model saved!")