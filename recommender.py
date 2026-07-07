import pickle
import sqlite3
import pandas as pd

def get_recommendations(user_id, top_n=5):
    # 1. Load the trained SVD model
    with open("svd_model.pkl", "rb") as f:
        algo = pickle.load(f)
        
    # 2. Fetch movies from SQLite database
    conn = sqlite3.connect("movies.db")
    movies_df = pd.read_sql_query("SELECT * FROM movies", conn)
    conn.close()
    
    # 3. Predict ratings for all movies this user hasn't seen
    # (For simplicity, we'll predict for all movies in the DB)
    predictions = []
    for _, row in movies_df.iterrows():
        movie_id = row['movieId']
        title = row['title']
        # algo.predict(uid, iid) predicts the rating
        pred = algo.predict(str(user_id), str(movie_id))
        predictions.append((title, pred.est))
        
    # 4. Sort by highest predicted rating
    predictions.sort(key=lambda x: x[1], reverse=True)
    
    return predictions[:top_n]