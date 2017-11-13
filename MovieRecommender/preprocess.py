from dataload import *
from processkeywords import *
from model import *
import pickle


def preprocess():
    # Load DataSet
    credits = load_tmdb_credits("../data/tmdb_5000_credits.csv")
    movies = load_tmdb_movies("../data/tmdb_5000_movies.csv")
    formatted_data = convert_to_original_format(movies, credits)

    # Extract keywords from the dataset
    keywords, keywords_roots, keywords_select = keywords_inventory(formatted_data, column='plot_keywords')

    # Replacement of the keywords by the main keyword
    df_keywords_cleaned = replacement_df_keywords(formatted_data, keywords_select, roots=True)

    # replace keywords that appear less that 5 times by a synomym of higher frequency.
    # suppress all the keywords that appear in less than 3 films
    df_keywords_occurence, keywords = replace_synonyms(df_keywords_cleaned, keywords)

    # add movie overview to the list of keywords
    df_keywords_improved = add_overview_keywords(df_keywords_occurence, keywords, True)
    df = df_keywords_improved.copy(deep=True)
    df.reset_index(inplace=True, drop=True)
    df.to_pickle('../data/processedData.pkl')
