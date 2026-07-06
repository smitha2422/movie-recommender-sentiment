# from flask import Flask

# app = Flask(__name__)

# @app.route("/")
# def home():
#     return "Movie Recommender & Sentiment API is running perfectly inside .venv!"

# if __name__ == "__main__":
#     app.run(debug=True)

from flask import Flask, render_template, request, jsonify
import pickle
import pandas as pd
import re

app = Flask(__name__)

# Load recommendation artifacts
movies = pickle.load(open("models/movies_df.pkl", "rb"))
cosine_sim = pickle.load(open("models/cosine_sim.pkl", "rb"))
indices = pickle.load(open("models/indices.pkl", "rb"))

# Load sentiment artifacts
sentiment_model = pickle.load(open("models/sentiment_model.pkl", "rb"))
vectorizer = pickle.load(open("models/sentiment_vectorizer.pkl", "rb"))

def clean_text(text):
    text = re.sub(r'<.*?>', ' ', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text.lower().strip()

def get_recommendations(title, num=8):
    title = title.lower().strip()
    if title not in indices:
        return []
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:num+1]
    movie_indices = [i[0] for i in sim_scores]
    return movies.iloc[movie_indices][['title', 'genres']].to_dict(orient='records')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    title = data.get('title', '')
    results = get_recommendations(title)
    if not results:
        return jsonify({"error": "Movie not found. Try another title."}), 404
    return jsonify({"recommendations": results})

@app.route('/api/sentiment', methods=['POST'])
def sentiment():
    data = request.get_json()
    review = data.get('review', '')
    cleaned = clean_text(review)
    vec = vectorizer.transform([cleaned])
    pred = sentiment_model.predict(vec)[0]
    prob = sentiment_model.predict_proba(vec)[0]
    result = "Positive" if pred == 1 else "Negative"
    confidence = round(max(prob) * 100, 2)
    return jsonify({"sentiment": result, "confidence": confidence})

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '').lower()
    matches = movies[movies['title'].str.lower().str.contains(query, na=False)]
    return jsonify({"titles": matches['title'].head(10).tolist()})

if __name__ == '__main__':
    app.run(debug=True)