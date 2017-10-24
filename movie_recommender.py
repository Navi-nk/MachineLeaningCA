import json
import pandas as pd
import numpy as np
import nltk
import math
from nltk.corpus import wordnet
from sklearn.neighbors import NearestNeighbors
from fuzzywuzzy import fuzz

PS = nltk.stem.PorterStemmer()

gaussian_filter = lambda x,y,sigma: math.exp(-(x-y)**2/(2*sigma**2))

LOST_COLUMNS = [
               'actor_1_facebook_likes',
               'actor_2_facebook_likes',
               'actor_3_facebook_likes',
               'aspect_ratio',
               'cast_total_facebook_likes',
               'color',
               'content_rating',
               'director_facebook_likes',
               'facenumber_in_poster',
               'movie_facebook_likes',
               'movie_imdb_link',
               'num_critic_for_reviews',
               'num_user_for_reviews'
               ]

TMDB_TO_IMDB_SIMPLE_EQUIVALENCIES = {
                                    'budget': 'budget',
                                    'genres': 'genres',
                                    'revenue': 'gross',
                                    'title': 'movie_title',
                                    'runtime': 'duration',
                                    'original_language': 'language',
                                    'keywords': 'plot_keywords',
                                    'vote_count': 'num_voted_users'
                                    }

IMDB_COLUMNS_TO_REMAP = {
                        'imdb_score': 'vote_average'
                        }

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

def safe_access(container, index_values):
    result = container
    try:
        for idx in index_values:
            result = result[idx]
        return result
    except IndexError or KeyError:
        return pd.np.nan

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
    tmdb_movies['language'] = tmdb_movies['spoken_languages'].apply(lambda x: safe_access(x, [0, 'name']))
    tmdb_movies['director_name'] = credits['crew'].apply(get_director)
    tmdb_movies['actor_1_name'] = credits['cast'].apply(lambda x: safe_access(x, [1, 'name']))
    tmdb_movies['actor_2_name'] = credits['cast'].apply(lambda x: safe_access(x, [2, 'name']))
    tmdb_movies['actor_3_name'] = credits['cast'].apply(lambda x: safe_access(x, [3, 'name']))
    tmdb_movies['genres'] = tmdb_movies['genres'].apply(pipe_flatten_names)
    tmdb_movies['plot_keywords'] = tmdb_movies['plot_keywords'].apply(pipe_flatten_names)
    return tmdb_movies

def count_word(df, ref_col, liste):
    keyword_count = dict()
    for s in liste: keyword_count[s] = 0
    for liste_keywords in df[ref_col].str.split('|'):
        if type(liste_keywords) == float and pd.isnull(liste_keywords): continue
        for s in [s for s in liste_keywords if s in liste]:
            if pd.notnull(s): keyword_count[s] += 1
    keyword_occurences = []
    for k,v in keyword_count.items():
        keyword_occurences.append([k,v])
    keyword_occurences.sort(key = lambda x:x[1], reverse = True)
    return keyword_occurences, keyword_count

def keywords_inventory(dataframe, colonne = 'plot_keywords'):
    keywords_roots  = dict()  # collect the words / root
    keywords_select = dict()  # association: root <-> keyword
    category_keys = []
    icount = 0
    for s in dataframe[colonne]:
        if pd.isnull(s): continue
        for t in s.split('|'):
            t = t.lower() ; racine = PS.stem(t)
            if racine in keywords_roots:                
                keywords_roots[racine].add(t)
            else:
                keywords_roots[racine] = {t}
    for s in keywords_roots.keys():
        if len(keywords_roots[s]) > 1:  
            min_length = 1000
            for k in keywords_roots[s]:
                if len(k) < min_length:
                    clef = k ; min_length = len(k)            
            category_keys.append(clef)
            keywords_select[s] = clef
        else:
            category_keys.append(list(keywords_roots[s])[0])
            keywords_select[s] = list(keywords_roots[s])[0]
    print("No. of keywords in variable '{}': {}".format(colonne,len(category_keys)))
    return category_keys, keywords_roots, keywords_select

def replacement_df_keywords(df, dico_remplacement, roots = False):
    df_new = df.copy(deep = True)
    for index, row in df_new.iterrows():
        chaine = row['plot_keywords']
        if pd.isnull(chaine): continue
        nouvelle_liste = []
        for s in chaine.split('|'): 
            clef = PS.stem(s) if roots else s
            if clef in dico_remplacement.keys():
                nouvelle_liste.append(dico_remplacement[clef])
            else:
                nouvelle_liste.append(s)       
        df_new.set_value(index, 'plot_keywords', '|'.join(nouvelle_liste)) 
    return df_new

def get_synonymes(mot_cle):
    lemma = set()
    for ss in wordnet.synsets(mot_cle):
        for w in ss.lemma_names():
            index = ss.name().find('.')+1
            if ss.name()[index] == 'n': lemma.add(w.lower().replace('_',' '))
    return lemma

def test_keyword(mot, key_count, threshold):
    return (False , True)[key_count.get(mot, 0) >= threshold]

def replacement_df_low_frequency_keywords(df, keyword_occurences):
    df_new = df.copy(deep = True)
    key_count = dict()
    for s in keyword_occurences: 
        key_count[s[0]] = s[1]    
    for index, row in df_new.iterrows():
        chaine = row['plot_keywords']
        if pd.isnull(chaine): continue
        nouvelle_liste = []
        for s in chaine.split('|'): 
            if key_count.get(s, 4) > 3: nouvelle_liste.append(s)
        df_new.set_value(index, 'plot_keywords', '|'.join(nouvelle_liste))
    return df_new

def fill_year(df):
    col = ['director_name', 'actor_1_name', 'actor_2_name', 'actor_3_name']
    usual_year = [0 for _ in range(4)]
    var        = [0 for _ in range(4)]
    for i in range(4):
        usual_year[i] = df.groupby(col[i])['title_year'].mean()
    actor_year = dict()
    for i in range(4):
        for s in usual_year[i].index:
            if s in actor_year.keys():
                if pd.notnull(usual_year[i][s]) and pd.notnull(actor_year[s]):
                    actor_year[s] = (actor_year[s] + usual_year[i][s])/2
                elif pd.isnull(actor_year[s]):
                    actor_year[s] = usual_year[i][s]
            else:
                actor_year[s] = usual_year[i][s]
    missing_year_info = df[df['title_year'].isnull()]
    icount_replaced = 0
    for index, row in missing_year_info.iterrows():
        value = [ np.NaN for _ in range(4)]
        icount = 0 ; sum_year = 0
        for i in range(4):            
            var[i] = df.loc[index][col[i]]
            if pd.notnull(var[i]): value[i] = actor_year[var[i]]
            if pd.notnull(value[i]): icount += 1 ; sum_year += actor_year[var[i]]
        if icount != 0: sum_year = sum_year / icount 
        if int(sum_year) > 0:
            icount_replaced += 1
            df.set_value(index, 'title_year', int(sum_year))
            if icount_replaced < 10: 
                print("{:<45} -> {:<20}".format(df.loc[index]['movie_title'],int(sum_year)))
    return df

def entry_variables(df, id_entry): 
    col_labels = []    
    if pd.notnull(df['director_name'].iloc[id_entry]):
        for s in df['director_name'].iloc[id_entry].split('|'):
            col_labels.append(s)
            
    for i in range(3):
        column = 'actor_NUM_name'.replace('NUM', str(i+1))
        if pd.notnull(df[column].iloc[id_entry]):
            for s in df[column].iloc[id_entry].split('|'):
                col_labels.append(s)
                
    if pd.notnull(df['plot_keywords'].iloc[id_entry]):
        for s in df['plot_keywords'].iloc[id_entry].split('|'):
            col_labels.append(s)
    return col_labels

def add_variables(df, REF_VAR):    
    for s in REF_VAR: df[s] = pd.Series([0 for _ in range(len(df))])
    colonnes = ['genres',
                'actor_1_name',
                'actor_2_name',
                'actor_3_name',
                'director_name',
                'plot_keywords'
                ]
    for categorie in colonnes:
        for index, row in df.iterrows():
            if pd.isnull(row[categorie]): continue
            for s in row[categorie].split('|'):
                if s in REF_VAR: df.set_value(index, s, 1)            
    return df

def recommend(df, id_entry):    
    df_copy = df.copy(deep = True)    
    liste_genres = set()
    for s in df['genres'].str.split('|').values:
        liste_genres = liste_genres.union(set(s))    
    variables = entry_variables(df_copy, id_entry)
    variables += list(liste_genres)
    df_new = add_variables(df_copy, variables)
    X = df_new.as_matrix(variables)
    nbrs = NearestNeighbors(n_neighbors=31, algorithm='auto', metric='euclidean').fit(X)
    distances, indices = nbrs.kneighbors(X)    
    xtest = df_new.iloc[id_entry].as_matrix(variables)
    xtest = xtest.reshape(1, -1)
    distances, indices = nbrs.kneighbors(xtest)
    return indices[0][:]

def extract_parameters(df, liste_films):     
    parametres_films = ['_' for _ in range(31)]
    i = 0
    max_users = -1
    for index in liste_films:
        parametres_films[i] = list(df.iloc[index][[
        	                                       'movie_title',
        	                                       'title_year',
                                                   'imdb_score', 
                                                   'num_user_for_reviews', 
                                                   'num_voted_users'
                                                   ]])
        parametres_films[i].append(index)
        max_users = max(max_users, parametres_films[i][4] )
        i += 1
    title_main = parametres_films[0][0]
    annee_ref  = parametres_films[0][1]
    parametres_films.sort(key = lambda x:critere_selection(title_main, max_users,
                                    annee_ref, x[0], x[1], x[2], x[4]), reverse = True)
    return parametres_films 
    
def sequel(titre_1, titre_2):    
    if fuzz.ratio(titre_1, titre_2) > 50 or fuzz.token_set_ratio(titre_1, titre_2) > 50:
        return True
    else:
        return False

def critere_selection(title_main, max_users, annee_ref, titre, annee, imdb_score, votes):    
    if pd.notnull(annee_ref):
        facteur_1 = gaussian_filter(annee_ref, annee, 20)
    else:
        facteur_1 = 1        
    sigma = max_users * 1.0
    if pd.notnull(votes):
        facteur_2 = gaussian_filter(votes, max_users, sigma)
    else:
        facteur_2 = 0
    if sequel(title_main, titre):
        note = 0
    else:
        note = imdb_score**2 * facteur_1 * facteur_2
    return note

def add_to_selection(film_selection, parametres_films):    
    film_list = film_selection[:]
    icount = len(film_list)    
    for i in range(31):
        already_in_list = False
        for s in film_selection:
            if s[0] == parametres_films[i][0]: already_in_list = True
            if sequel(parametres_films[i][0], s[0]): already_in_list = True            
        if already_in_list: continue
        icount += 1
        if icount <= 5:
            film_list.append(parametres_films[i])
    return film_list

def remove_sequels(film_selection):    
    removed_from_selection = []
    for i, film_1 in enumerate(film_selection):
        for j, film_2 in enumerate(film_selection):
            if j <= i: continue 
            if sequel(film_1[0], film_2[0]): 
                last_film = film_2[0] if film_1[1] < film_2[1] else film_1[0]
                removed_from_selection.append(last_film)
    film_list = [film for film in film_selection if film[0] not in removed_from_selection]
    return film_list

def find_similarities(df, id_entry, del_sequels = True, verbose = False):    
    if verbose: 
        print(90*'_' + '\n' + "QUERY: films similar to id={} -> '{}'".format(id_entry,
                                df.iloc[id_entry]['movie_title']))
    liste_films = recommend(df, id_entry)
    parametres_films = extract_parameters(df, liste_films)
    film_selection = []
    film_selection = add_to_selection(film_selection, parametres_films)
    if del_sequels: film_selection = remove_sequels(film_selection)
    film_selection = add_to_selection(film_selection, parametres_films)
    selection_titres = []
    for i,s in enumerate(film_selection):
        selection_titres.append([s[0].replace(u'\xa0', u''), s[5]])
        if verbose: print("No{:<2}     -> {:<30}".format(i+1, s[0]))
    return selection_titres

## 1. Load the data
credits = load_tmdb_credits("./data/tmdb_5000_credits.csv")
movies = load_tmdb_movies("./data/tmdb_5000_movies.csv")
df_initial = convert_to_original_format(movies, credits)

## 2. List no. of occurrences based on keyword 'plot_keywords'
#set_keywords = set()
#for liste_keywords in df_initial['plot_keywords'].str.split('|').values:
#    if isinstance(liste_keywords, float): continue  # only happen if liste_keywords = NaN
#    set_keywords = set_keywords.union(liste_keywords)
#keyword_occurences, dum = count_word(df_initial, 'plot_keywords', set_keywords)
#print('List no. of occurrences based on keyword \'plot_keywords\':\n')
#print(keyword_occurences[:5])

## 3. List no. of occurrences based on genres
#genre_labels = set()
#for s in df_initial['genres'].str.split('|').values:
#    genre_labels = genre_labels.union(set(s))
#keyword_occurences, dum = count_word(df_initial, 'genres', genre_labels)
#print('List no. of occurrences based on genres:\n')
#print(keyword_occurences[:5])

## 4. Remove duplicate entries
#df_temp = df_initial
#list_var_duplicates = [
#                      'movie_title',
#                      'title_year',
#                      'director_name'
#                      ]
#liste_duplicates = df_temp['movie_title'].map(df_temp['movie_title'].value_counts() > 1)
#print("No. of duplicate entries: {}".format(len(df_temp[liste_duplicates][list_var_duplicates])))
#print("Duplicate entries but values differ:\n%s"%df_temp[liste_duplicates][list_var_duplicates])
#df_duplicate_cleaned = df_temp

## 5. Remove duplicated keywords and replace it with main keyword
#keywords, keywords_roots, keywords_select = keywords_inventory(df_duplicate_cleaned,
keywords, keywords_roots, keywords_select = keywords_inventory(df_initial,
                                                               colonne = 'plot_keywords')
#icount = 0
#for s in keywords_roots.keys():
#   if len(keywords_roots[s]) > 1: 
#        icount += 1
#       if icount < 15: print(icount, keywords_roots[s], len(keywords_roots[s]))
#df_keywords_cleaned = replacement_df_keywords(df_duplicate_cleaned,
df_keywords_cleaned = replacement_df_keywords(df_initial,
	                                                   keywords_select,
                                                       roots = True)
keyword_occurences, keywords_count = count_word(df_keywords_cleaned,
	                                                              'plot_keywords',
	                                                              keywords)
print("Count of keyword occurences:\n")
print(keyword_occurences[:5])
keyword_occurences.sort(key = lambda x:x[1], reverse = False)
key_count = dict()
for s in keyword_occurences:
    key_count[s[0]] = s[1]
replacement_mot = dict()
icount = 0
for index, [mot, nb_apparitions] in enumerate(keyword_occurences):
    if nb_apparitions > 5: continue  # only the keywords that appear less than 5 times
    lemma = get_synonymes(mot)
    if len(lemma) == 0: continue     # case of the plurals
    liste_mots = [(s, key_count[s]) for s in lemma 
                  if test_keyword(s, key_count, key_count[mot])]
    liste_mots.sort(key = lambda x:(x[1],x[0]), reverse = True)    
    if len(liste_mots) <= 1: continue       # no replacement
    if mot == liste_mots[0][0]: continue    # replacement by himself
    icount += 1
    if  icount < 8:
        print('{:<12} -> {:<12} (init: {})'.format(mot, liste_mots[0][0], liste_mots))    
    replacement_mot[mot] = liste_mots[0][0]
print(90*'_'+'\n'+'The replacement concerns {}% of the keywords.'
      .format(round(len(replacement_mot)/len(keywords)*100,2)))
print('Keywords that appear both in keys and values:'.upper()+'\n'+45*'-')
icount = 0
for s in replacement_mot.values():
    if s in replacement_mot.keys():
        icount += 1
        if icount < 10: print('{:<20} -> {:<20}'.format(s, replacement_mot[s]))
for key, value in replacement_mot.items():
    if value in replacement_mot.keys():
        replacement_mot[key] = replacement_mot[value]
df_keywords_synonyms = replacement_df_keywords(df_keywords_cleaned,
	                                                             replacement_mot,
	                                                             roots = False)   
keywords, keywords_roots, keywords_select = keywords_inventory(df_keywords_synonyms,
	                                                                             colonne = 'plot_keywords')
new_keyword_occurences, keywords_count = count_word(df_keywords_synonyms,
                                                                      'plot_keywords',
                                                                      keywords)
print('new keyword occurrences:\n')
print(new_keyword_occurences[:5])
df_keywords_occurence = replacement_df_low_frequency_keywords(df_keywords_synonyms,
	                                                                            new_keyword_occurences)
keywords, keywords_roots, keywords_select = keywords_inventory(df_keywords_occurence,
	                                                                             colonne = 'plot_keywords')
new_keyword_occurences, keywords_count = count_word(df_keywords_occurence,
                                                    'plot_keywords',
                                                    keywords)
print('New keyword occurrencces after deleting low frequency keywords:\n')
print(new_keyword_occurences[:5])

## 6. Drop columns that no longer exists
new_col_order = [
                 'movie_title',
                 'title_year',
                 'genres',
                 'plot_keywords', 
                 'director_name',
                 'actor_1_name',
                 'actor_2_name',
                 'actor_3_name',
                 'director_facebook_likes',
                 'actor_1_facebook_likes',
                 'actor_2_facebook_likes',
                 'actor_3_facebook_likes',
                 'movie_facebook_likes',
                 'num_critic_for_reviews', 
                 'num_user_for_reviews',
                 'num_voted_users',
                 'language',
                 'country',
                 'imdb_score',
                 'movie_imdb_link',
                 'color',
                 'duration',
                 'gross',
                 'overview'
                 ]
new_col_order = [col for col in new_col_order if col not in LOST_COLUMNS]
new_col_order = [IMDB_COLUMNS_TO_REMAP[col] 
                 if col in IMDB_COLUMNS_TO_REMAP
                 else col
                 for col in new_col_order]
new_col_order = [TMDB_TO_IMDB_SIMPLE_EQUIVALENCIES[col]
                 if col in TMDB_TO_IMDB_SIMPLE_EQUIVALENCIES 
                 else col
                 for col in new_col_order]
df_var_cleaned = df_keywords_occurence[new_col_order]

## 7. Fill missing title years
df_filling = df_var_cleaned.copy(deep=True)
missing_year_info = df_filling[df_filling['title_year'].isnull()][[
                                                                   'director_name',
                                                                   'actor_1_name', 
                                                                   'actor_2_name', 
                                                                   'actor_3_name'
                                                                   ]]
print('Missing Year Info:\n')
print(missing_year_info[:10])
df_filling = fill_year(df_filling)

for index, row in df_filling.iterrows():
    if isinstance(row['overview'], str): 
        liste_mot = row['overview'].replace('\D+', '').strip().split()
    else:
        continue
    new_keyword = []
    for s in liste_mot:
        lemma = get_synonymes(s)
        for t in list(lemma):
            if t in keywords: 
                new_keyword.append(t)                
    if new_keyword:
        df_filling.set_value(index, 'plot_keywords', '|'.join(new_keyword))
df = df_filling.copy(deep=True)
df.reset_index(inplace = True, drop = True)

## 8. Recommendation Engine
dum = find_similarities(df, 120, del_sequels = True, verbose = True)
#print(dum)
#dum = find_similarities(df, 12, del_sequels = True, verbose = True)
#print(dum)
#dum = find_similarities(df, 2, del_sequels = True, verbose = True)
#print(dum)


## 9. Test
selection = dict()
for i in range(0, 20, 2):
    selection[i] = find_similarities(df, i, del_sequels = False, verbose = True)
#print(selection)
