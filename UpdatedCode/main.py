
#Custom libs
from dataload import *
from preprocess import *
from model import *
import os
import pandas as pd

def get_combined_data_frame(train=False):
    if train:
        preprocess()
    if not os.path.isfile('../data/processedData.pkl'):
        preprocess()
    df = pd.read_pickle('../data/processedData.pkl')
    return df

def get_entry_id(df, movie):
    df_movie_id_list = list(df['movie_title'].values)
    id_entry = df_movie_id_list.index(movie)
    return id_entry

def movie_recommender(movie_title):
    df = get_combined_data_frame()
    id_entry = get_entry_id(df, movie_title)
    recommended_movies = find_similarities(df, id_entry=id_entry)
    for i in range(len(recommended_movies)):
    	movie_title = recommended_movies[i][0]
    	string = '%s. %s'%(i+1, movie_title)
    	print(string)

if __name__ == '__main__':
    movie_recommender('The Avengers')
