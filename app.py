# # from flask import Flask

# # app = Flask(__name__)

# # @app.route("/")
# # def home():
# #     return "Movie Recommender & Sentiment API is running perfectly inside .venv!"

# # if __name__ == "__main__":
# #     app.run(debug=True)

# from flask import Flask, render_template, request, jsonify
# import pickle
# import pandas as pd
# import re

# app = Flask(__name__)

# # Load recommendation artifacts
# movies = pickle.load(open("models/movies_df.pkl", "rb"))
# cosine_sim = pickle.load(open("models/cosine_sim.pkl", "rb"))
# indices = pickle.load(open("models/indices.pkl", "rb"))

# # Load sentiment artifacts
# sentiment_model = pickle.load(open("models/sentiment_model.pkl", "rb"))
# vectorizer = pickle.load(open("models/sentiment_vectorizer.pkl", "rb"))

# def clean_text(text):
#     text = re.sub(r'<.*?>', ' ', text)
#     text = re.sub(r'[^a-zA-Z\s]', '', text)
#     return text.lower().strip()

# def get_recommendations(title, num=8):
#     title = title.lower().strip()
#     if title not in indices:
#         return []
#     idx = indices[title]
#     sim_scores = list(enumerate(cosine_sim[idx]))
#     sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
#     sim_scores = sim_scores[1:num+1]
#     movie_indices = [i[0] for i in sim_scores]
#     return movies.iloc[movie_indices][['title', 'genres']].to_dict(orient='records')

# @app.route('/')
# def home():
#     return render_template('index.html')

# @app.route('/api/recommend', methods=['POST'])
# def recommend():
#     data = request.get_json()
#     title = data.get('title', '')
#     results = get_recommendations(title)
#     if not results:
#         return jsonify({"error": "Movie not found. Try another title."}), 404
#     return jsonify({"recommendations": results})

# @app.route('/api/sentiment', methods=['POST'])
# def sentiment():
#     data = request.get_json()
#     review = data.get('review', '')
#     cleaned = clean_text(review)
#     vec = vectorizer.transform([cleaned])
#     pred = sentiment_model.predict(vec)[0]
#     prob = sentiment_model.predict_proba(vec)[0]
#     result = "Positive" if pred == 1 else "Negative"
#     confidence = round(max(prob) * 100, 2)
#     return jsonify({"sentiment": result, "confidence": confidence})

# @app.route('/api/search', methods=['GET'])
# def search():
#     query = request.args.get('q', '').lower()
#     matches = movies[movies['title'].str.lower().str.contains(query, na=False)]
#     return jsonify({"titles": matches['title'].head(10).tolist()})

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import pickle
import re

app = Flask(__name__)
app.secret_key = "change-this-to-a-random-secret-string"  # needed for sessions

# ---------- Load ML artifacts (same as before) ----------
movies = pickle.load(open("models/movies_df.pkl", "rb"))
cosine_sim = pickle.load(open("models/cosine_sim.pkl", "rb"))
indices = pickle.load(open("models/indices.pkl", "rb"))
sentiment_model = pickle.load(open("models/sentiment_model.pkl", "rb"))
vectorizer = pickle.load(open("models/sentiment_vectorizer.pkl", "rb"))

def clean_text(text):
    text = re.sub(r'<.*?>', ' ', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text.lower().strip()

def get_db():
    return sqlite3.connect('movies.db')

def login_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return view_func(*args, **kwargs)
    return wrapper

# ---------- Page routes ----------
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=session.get('username'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

# ---------- Auth API ----------
@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    password_hash = generate_password_hash(password)
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        return jsonify({"message": "Registration successful! You can now log in."}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 400
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[1], password):
        session['user_id'] = user[0]
        session['username'] = username
        return jsonify({"message": "Login successful!", "redirect": url_for('dashboard')}), 200
    return jsonify({"error": "Invalid username or password"}), 401

# ---------- Recommendation + Sentiment API (protected) ----------
def get_recommendations(title, num=8):
    title = title.lower().strip()
    if title not in indices:
        return []
    idx = indices[title]
    sim_scores = sorted(list(enumerate(cosine_sim[idx])), key=lambda x: x[1], reverse=True)[1:num+1]
    movie_indices = [i[0] for i in sim_scores]
    return movies.iloc[movie_indices][['title', 'genres']].to_dict(orient='records')

@app.route('/api/recommend', methods=['POST'])
@login_required
def recommend():
    data = request.get_json()
    results = get_recommendations(data.get('title', ''))
    if not results:
        return jsonify({"error": "Movie not found. Try another title."}), 404
    return jsonify({"recommendations": results})

@app.route('/api/sentiment', methods=['POST'])
@login_required
def sentiment():
    data = request.get_json()
    review = data.get('review', '')
    cleaned = clean_text(review)
    vec = vectorizer.transform([cleaned])
    pred = sentiment_model.predict(vec)[0]
    prob = sentiment_model.predict_proba(vec)[0]
    result = "Positive" if pred == 1 else "Negative"
    confidence = round(max(prob) * 100, 2)

    # Save to review history (innovative feature #1)
    conn = get_db()
    conn.execute(
        "INSERT INTO review_history (user_id, review_text, sentiment, confidence) VALUES (?, ?, ?, ?)",
        (session['user_id'], review, result, confidence)
    )
    conn.commit()
    conn.close()

    return jsonify({"sentiment": result, "confidence": confidence})

@app.route('/api/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('q', '').lower()
    matches = movies[movies['title'].str.lower().str.contains(query, na=False)]
    return jsonify({"titles": matches['title'].head(10).tolist()})

# ---------- Watchlist API (innovative feature #2) ----------
@app.route('/api/watchlist', methods=['GET'])
@login_required
def get_watchlist():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT movie_title FROM watchlist WHERE user_id = ?", (session['user_id'],))
    titles = [row[0] for row in cursor.fetchall()]
    conn.close()
    return jsonify({"watchlist": titles})

@app.route('/api/watchlist/add', methods=['POST'])
@login_required
def add_to_watchlist():
    title = request.get_json().get('title', '').strip()
    conn = get_db()
    conn.execute("INSERT INTO watchlist (user_id, movie_title) VALUES (?, ?)", (session['user_id'], title))
    conn.commit()
    conn.close()
    return jsonify({"message": f"{title} added to watchlist!"})

@app.route('/api/watchlist/remove', methods=['POST'])
@login_required
def remove_from_watchlist():
    title = request.get_json().get('title', '').strip()
    conn = get_db()
    conn.execute("DELETE FROM watchlist WHERE user_id = ? AND movie_title = ?", (session['user_id'], title))
    conn.commit()
    conn.close()
    return jsonify({"message": f"{title} removed from watchlist."})

# ---------- Review history API (innovative feature #1 continued) ----------
@app.route('/api/history', methods=['GET'])
@login_required
def get_history():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT review_text, sentiment, confidence FROM review_history WHERE user_id = ? ORDER BY id DESC LIMIT 10",
        (session['user_id'],)
    )
    rows = cursor.fetchall()
    conn.close()
    history = [{"review": r[0], "sentiment": r[1], "confidence": r[2]} for r in rows]
    return jsonify({"history": history})

if __name__ == '__main__':
    app.run(debug=True)