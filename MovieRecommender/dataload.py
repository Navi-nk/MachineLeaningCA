import pandas as pd
import json

new_col_order = [
                 'movie_title',
                 'title_year',
                 'genres',
                 'plot_keywords', 
                 'director_name',
                 'actor_1_name',
                 'actor_2_name',
                 'actor_3_name',
                 'num_voted_users',
                 'language',
                 'country',
                 'vote_average',
                 'duration',
                 'gross',
                 'overview',
                 'companies',
                 'popularity'
                 ]


TMDB_TO_IMDB_SIMPLE_EQUIVALENCIES = {
                                    'revenue': 'gross',
                                    'title': 'movie_title',
                                    'runtime': 'duration',
                                    'original_language': 'language',
                                    'keywords': 'plot_keywords',
                                    'vote_count': 'num_voted_users',
                                    'imdb_score': 'vote_average'
                                    }
def safe_access(container, index_values):
    result = container
    try:
        for idx in index_values:
            result = result[idx]
        return result
    except IndexError or KeyError:
        return pd.np.nan

def load_tmdb_movies(path):
    df = pd.read_csv(path)
    df['release_date'] = pd.to_datetime(df['release_date']).apply(lambda x: x.date())
    json_columns = [
                   'genres',
                   'keywords',
                   'production_countries',
                   'production_companies',
                   'spoken_languages'
                   ]
    for column in json_columns:
        df[column] = df[column].apply(json.loads)
    return df

def load_tmdb_credits(path):
    df = pd.read_csv(path)
    json_columns = [
                   'cast', 'crew'
                   ]
    for column in json_columns:
        df[column] = df[column].apply(json.loads)
    return df

def get_director(crew_data):
    directors = [x['name'] for x in crew_data if x['job'] == 'Director']
    return safe_access(directors, [0])

def pipe_flatten_names(keywords):
    return '|'.join([x['name'] for x in keywords])

def convert_to_original_format(movies, credits):
    tmdb_movies = movies.copy()
    tmdb_movies.rename(columns=TMDB_TO_IMDB_SIMPLE_EQUIVALENCIES, inplace=True)
    tmdb_movies['title_year'] = pd.to_datetime(tmdb_movies['release_date']).apply(lambda x: x.year)
    tmdb_movies['country'] = tmdb_movies['production_countries'].apply(lambda x: safe_access(x, [0, 'name']))
    tmdb_movies['companies'] = tmdb_movies['production_companies'].apply(lambda x: safe_access(x, [0, 'name']))
    tmdb_movies['language'] = tmdb_movies['spoken_languages'].apply(lambda x: safe_access(x, [0, 'name']))
    tmdb_movies['director_name'] = credits['crew'].apply(get_director)
    tmdb_movies['actor_1_name'] = credits['cast'].apply(lambda x: safe_access(x, [1, 'name']))
    tmdb_movies['actor_2_name'] = credits['cast'].apply(lambda x: safe_access(x, [2, 'name']))
    tmdb_movies['actor_3_name'] = credits['cast'].apply(lambda x: safe_access(x, [3, 'name']))
    tmdb_movies['genres'] = tmdb_movies['genres'].apply(pipe_flatten_names)
    tmdb_movies['plot_keywords'] = tmdb_movies['plot_keywords'].apply(pipe_flatten_names)

    tmdb_movies_formatted = tmdb_movies[new_col_order]

    return tmdb_movies_formatted