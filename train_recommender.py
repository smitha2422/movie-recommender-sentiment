import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

movies = pd.read_csv("data/movies.csv")

# genres column looks like "Adventure|Animation|Children"
movies['genres_clean'] = movies['genres'].str.replace('|', ' ', regex=False)

# TF-IDF on genres (you can enrich this later with plot/overview from TMDB API)
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies['genres_clean'])

# Cosine similarity between all movies
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Save everything needed for lookup
movies.reset_index(drop=True, inplace=True)
indices = pd.Series(movies.index, index=movies['title'].str.lower())

with open("models/movies_df.pkl", "wb") as f:
    pickle.dump(movies, f)
with open("models/cosine_sim.pkl", "wb") as f:
    pickle.dump(cosine_sim, f)
with open("models/indices.pkl", "wb") as f:
    pickle.dump(indices, f)

print("Recommender model saved!")