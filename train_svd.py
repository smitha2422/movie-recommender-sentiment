import pickle
import pandas as pd
from surprise import Dataset, Reader, SVD

print("1. Loading ratings.csv...")
ratings_df = pd.read_csv("data/ratings.csv")  # Your updated path

print("2. Setting up data structures...")
reader = Reader(rating_scale=(0.5, 5.0))
data = Dataset.load_from_df(ratings_df[['userId', 'movieId', 'rating']], reader)

print("3. Training the SVD algorithm...")
trainset = data.build_full_trainset()
algo = SVD()
algo.fit(trainset)

print("4. Saving trained model to svd_model.pkl...")
with open("svd_model.pkl", "wb") as f:
    pickle.dump(algo, f)

print("🎉 svd_model.pkl successfully created!")