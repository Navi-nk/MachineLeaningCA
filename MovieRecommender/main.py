
#Custom libs
from dataload import *
from preprocess import *
from model import *
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

def movie_recommender(movie_title):
    df = get_combined_data_frame()
    movies_recommended = []
    id_entry = get_entry_id(df, movie_title)
    print("recommended for:%s"%movie_title)
    recommended_movies = find_similarities(df, id_entry=id_entry)
    for i in range(len(recommended_movies)):
        movie_title = recommended_movies[i][0]
        movies_recommended.append(movie_title)
        string = '%s. %s'%(i+1, movie_title)
        print(string)
    return movies_recommended

if __name__ == '__main__':
    movie_recommender('Doctor Strange')
