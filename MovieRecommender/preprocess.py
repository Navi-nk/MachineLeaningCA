#Custom libs
from dataload import *
from processkeywords import *
from model import *
import pickle

def preprocess():
	#Load DataSet
	credits = load_tmdb_credits("../data/tmdb_5000_credits.csv")
	movies = load_tmdb_movies("../data/tmdb_5000_movies.csv")
	formatted_data = convert_to_original_format(movies, credits)

	#add movie overiew to the list of keywords
	df_keywords_improved = add_overview_keywords(formatted_data,True)
	#rint(df_keywords_improved['plot_keywords'][0])
	#print(df_keywords_improved['overview'][0])

	#Extract keywods from the dataset
	keywords, keywords_roots, keywords_select = keywords_inventory(df_keywords_improved,column = 'plot_keywords')
	'''icount = 0
	for s in keywords_roots.keys():
		if len(keywords_roots[s]) > 1: 
			icount += 1
			if icount < 15: print(icount, keywords_roots[s],'-->', s)'''

	#Replacement of the keywords by the main keyword
	df_keywords_cleaned = replacement_df_keywords(df_keywords_improved,
															keywords_select,
															roots = True)

	#replace keywords that appear less that 5 times by a synomym of higher frequency. 
	#suppress all the keywords that appear in less than 3 films
	df_keywords_occurence, keywords = replace_synonyms(df_keywords_cleaned, keywords)
	
	#print(df_keywords_occurence['plot_keywords'][0])
	#print(df_keywords_occurence['overview'][0])

	df = df_keywords_occurence.copy(deep=True)
	df.reset_index(inplace = True, drop = True)

	df.to_pickle('../data/processedData.pkl')