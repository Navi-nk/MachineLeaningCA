from dataload import *
from preprocess import *
from model import *
from popularity import popularity
import os
import pandas as pd


def get_combined_data_frame(train=False):
    if not os.path.isfile('../data/processedData.pkl') or train:
        preprocess()
    df = pd.read_pickle('../data/processedData.pkl')
    return df


def get_entry_id(df, movie):
    df_movie_id_list = list(df['movie_title'].values)
    id_entry = df_movie_id_list.index(movie)
    return id_entry


def movie_recommender(movie_title, delete_sequels):
    df = get_combined_data_frame()
    movies_recommended = []
    popularity_list = []
    id_entry = get_entry_id(df, movie_title)
    print("recommended for:%s" % movie_title)
    recommended_movies, all_movies_found = find_similarities(df, id_entry=id_entry, delete_sequels=delete_sequels)
    for j in range(len(all_movies_found)):
        popularity_list.append(all_movies_found[j][6])
    print("Predicted movie popularity is %s" % popularity(popularity_list))
    for i in range(len(recommended_movies)):
        movie_title = recommended_movies[i][0]
        movies_recommended.append(movie_title)
        string = '%s. %s' % (i+1, movie_title)
        print(string)
    return movies_recommended
