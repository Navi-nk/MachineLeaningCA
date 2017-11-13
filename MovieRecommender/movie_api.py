import requests
import json
import pandas as pd
import csv
import ast
from main import *
from dataload import *

API_KEY = '333a07756aaff60e9afcc29ec3b69215'
BASE_MOVIE_URL = r'https://api.themoviedb.org/3/movie/'
BASE_SEARCH_URL = r'https://api.themoviedb.org/3/search/movie'
API_KEY_URL = r'?api_key=%s&language=en-US' % API_KEY


def get_movie_id_title(movie):
    search_append = r'&query=%s&page=1&include_adult=false' % movie
    url = BASE_SEARCH_URL + API_KEY_URL + search_append
    response = requests.get(url)
    data = json.loads(response.content.decode('utf-8'))
    try:
        movie_id = data['results'][0]['id']
        movie_title = data['results'][0]['title']
    except Exception:
        movie_id = None
        movie_title = None
    return movie_id, movie_title


def get_movie_keywords(movie_id):
    url = BASE_MOVIE_URL + str(movie_id) + '/keywords' + API_KEY_URL
    response = requests.get(url)
    keywords = json.loads(response.content.decode('utf-8'))
    return keywords


def get_movie_credits(movie_id):
    url = BASE_MOVIE_URL + str(movie_id) + '/credits' + API_KEY_URL
    response = requests.get(url)
    credits = json.loads(response.content.decode('utf-8'))
    return credits


def is_movie_in_credits(movie_id):
    found = False
    df = pd.read_csv('../data/tmdb_5000_credits.csv')
    if movie_id in list(df['movie_id'].values):
        found = True
    return found


def get_movie_details_online(movie_id):
    keywords = get_movie_keywords(movie_id)
    credits = get_movie_credits(movie_id)
    url = BASE_MOVIE_URL + str(movie_id) + API_KEY_URL
    response = requests.get(url)
    details = json.loads(response.content.decode('utf-8'))
    details['keywords'] = keywords['keywords']
    details['cast'] = credits['cast']
    details['crew'] = credits['crew']
    return details


def load_movie(df):
    df['release_date'] = pd.to_datetime(df['release_date']).apply(lambda x: x.date())
    json_columns = ['genres', 'keywords', 'production_countries', 'production_companies', 'spoken_languages']
    for column in json_columns:
        df[column] = df[column].apply(json.dumps)
    return df


def load_credit(df):
    json_columns = ['cast', 'crew']
    for column in json_columns:
        df[column] = df[column].apply(json.dumps)
    return df


def call_recommend(movie, delete_sequels):
    movie_id, movie_title = get_movie_id_title(movie)
    if not movie_id:
        recommended = "Movie not found. Type correctly!!"
        print(recommended)
        return recommended
    if not is_movie_in_credits(movie_id):
        print("Getting movie details online!")
        data = get_movie_details_online(movie_id)
        movies = [data['budget'], data['genres'], data['homepage'], data['id'], data['keywords'],
                  data['original_language'], data['original_title'], data['overview'], data['popularity'],
                  data['production_companies'], data['production_countries'], data['release_date'], data['revenue'],
                  data['runtime'], data['spoken_languages'], data['status'], data['tagline'], data['title'],
                  data['vote_average'], data['vote_count']]
        credits = [data['id'], data['title'], data['cast'], data['crew']]
        mf = load_movie(pd.DataFrame([movies], columns=['budget', 'genres', 'homepage', 'id', 'keywords',
                                                        'original_language', 'original_title', 'overview', 'popularity',
                                                        'production_companies', 'production_countries', 'release_date',
                                                        'revenue', 'runtime', 'spoken_languages', 'status', 'tagline',
                                                        'title', 'vote_average', 'vote_count']))
        cf = load_credit(pd.DataFrame([credits], columns=['id', 'title', 'cast', 'crew']))
        with open('../data/tmdb_5000_movies.csv', 'a') as f:
            mf.to_csv(f, header=None, index=None)
        with open('../data/tmdb_5000_credits.csv', 'a') as f:
            cf.to_csv(f, header=None, index=None)
        print("Training with new data")
        get_combined_data_frame(True)
    else:
        print("Movie found in the database!")
    print("Running recommendation")
    recommended = movie_recommender(movie_title, delete_sequels)
    return recommended


def get_movie_image(movie):
    search_append = r'&query=%s&page=1&include_adult=false' % movie
    url = BASE_SEARCH_URL + API_KEY_URL + search_append
    response = requests.get(url)
    data = json.loads(response.content.decode('utf-8'))
    try:
        movie_image = data['results'][0]['poster_path']
    except Exception as e:
        movie_image = None
        print(e)
    return movie_image


if __name__ == '__main__':
    call_recommend('dumbo', True)
