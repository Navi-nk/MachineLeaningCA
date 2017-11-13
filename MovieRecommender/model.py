import pandas as pd
import math
from sklearn.neighbors import NearestNeighbors
from fuzzywuzzy import fuzz


def gaussian_filter(x, y, sigma):
    return math.exp(-(x-y)**2/(2*sigma**2))


def entry_variables(df, id_entry): 
    column_labels = []
    if pd.notnull(df['director_name'].iloc[id_entry]):
        for s in df['director_name'].iloc[id_entry].split('|'):
            column_labels.append(s)
    for i in range(3):
        column = 'actor_NUM_name'.replace('NUM', str(i+1))
        if pd.notnull(df[column].iloc[id_entry]):
            for s in df[column].iloc[id_entry].split('|'):
                column_labels.append(s)
    if pd.notnull(df['plot_keywords'].iloc[id_entry]):
        for s in df['plot_keywords'].iloc[id_entry].split('|'):
            column_labels.append(s)
    return column_labels


def add_variables(df, reference_variable):
    for s in reference_variable:
        df[s] = pd.Series([0 for _ in range(len(df))])
    columns = ['genres', 'actor_1_name', 'actor_2_name', 'actor_3_name', 'director_name', 'plot_keywords']
    for categories in columns:
        for index, row in df.iterrows():
            if pd.isnull(row[categories]):
                continue
            for s in row[categories].split('|'):
                if s in reference_variable:
                    df.at[index, s] = 1
    return df


def recommend(df, id_entry):    
    df_copy = df.copy(deep=True)
    genres_list = set()
    for s in df['genres'].str.split('|').values:
        genres_list = genres_list.union(set(s))
    variables = entry_variables(df_copy, id_entry)
    variables += list(genres_list)
    df_new = add_variables(df_copy, variables)
    x = df_new.as_matrix(variables)
    neighbors = NearestNeighbors(n_neighbors=31, algorithm='auto', metric='euclidean').fit(x)
    x_test = df_new.iloc[id_entry].as_matrix(variables)
    x_test = x_test.reshape(1, -1)
    distances, indices = neighbors.kneighbors(x_test)
    return indices[0][:]


def extract_parameters(df, film_list):
    film_parameters = ['_' for _ in range(31)]
    i = 0
    max_users = -1
    for index in film_list:
        film_parameters[i] = list(df.iloc[index][['movie_title', 'title_year', 'imdb_score', 'num_user_for_reviews',
                                                  'num_voted_users', 'companies', 'popularity']])
        film_parameters[i].append(index)
        max_users = max(max_users, film_parameters[i][4])
        i += 1
    title_main = film_parameters[0][0]
    year_ref = film_parameters[0][1]
    film_parameters.sort(key=lambda x: criteria_selection(title_main, max_users, year_ref, x[0], x[1], x[2], x[4]),
                         reverse=True)
    return film_parameters


def sequel(title_1, title_2):
    if fuzz.ratio(title_1, title_2) > 50 or fuzz.token_set_ratio(title_1, title_2) > 50:
        return True
    else:
        return False


def criteria_selection(title_main, max_users, year_ref, titre, year, imdb_score, votes):
    if pd.notnull(year_ref):
        factor1 = gaussian_filter(year_ref, year, 20)
    else:
        factor1 = 1
    sigma = max_users * 1.0
    if pd.notnull(votes):
        factor2 = gaussian_filter(votes, max_users, sigma)
    else:
        factor2 = 0
    if sequel(title_main, titre):
        note = 0
    else:
        note = imdb_score**2 * factor1 * factor2
    return note


def add_to_selection(film_selection, film_parameters, id_entry):
    film_list = film_selection[:]
    i_count = len(film_list)
    for i in range(31):
        if id_entry == film_parameters[i][7]:
            continue
        already_in_list = False
        for s in film_selection:
            if s[0] == film_parameters[i][0]:
                already_in_list = True
            if sequel(film_parameters[i][0], s[0]):
                already_in_list = True
        if already_in_list:
            continue
        i_count += 1
        if i_count <= 5:
            film_list.append(film_parameters[i])
    return film_list


def remove_sequels(film_selection):    
    removed_from_selection = []
    for i, film_1 in enumerate(film_selection):
        for j, film_2 in enumerate(film_selection):
            if j <= i:
                continue
            if sequel(film_1[0], film_2[0]): 
                last_film = film_2[0] if film_1[1] < film_2[1] else film_1[0]
                removed_from_selection.append(last_film)
    film_list = [film for film in film_selection if film[0] not in removed_from_selection]
    return film_list


def find_similarities(df, id_entry, delete_sequels=False, verbose=False):
    if verbose: 
        print(90*'_' + '\n' + "QUERY: films similar to id={} -> '{}'".format(id_entry,
                                                                             df.iloc[id_entry]['movie_title']))
    list_films = recommend(df, id_entry)
    film_parameters = extract_parameters(df, list_films)
    film_selection = []
    film_selection = add_to_selection(film_selection, film_parameters, id_entry)
    if delete_sequels:
        film_selection = remove_sequels(film_selection)
        film_selection = add_to_selection(film_selection, film_parameters, id_entry)
    selection_titles = []
    for i, s in enumerate(film_selection):
        selection_titles.append([s[0].replace(u'\xa0', u''), s[5]])
        if verbose:
            print("No{:<2}     -> {:<30}".format(i+1, s[0]))
    return selection_titles, film_parameters
