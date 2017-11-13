import nltk
import pandas as pd
from nltk.corpus import wordnet
from nltk import pos_tag

PS = nltk.stem.PorterStemmer()


def keywords_inventory(df, column='plot_keywords'):
    keywords_roots = dict()  # collect the words / root
    keywords_select = dict()  # association: root <-> keyword
    category_keys = []
    for s in df[column]:
        if pd.isnull(s):
            continue
        for t in s.split('|'):
            t = t.lower()
            root = PS.stem(t)
            if root in keywords_roots:
                keywords_roots[root].add(t)
            else:
                keywords_roots[root] = {t}
    for s in keywords_roots.keys():
        if len(keywords_roots[s]) > 1:  
            min_length = 1000
            for k in keywords_roots[s]:
                if len(k) < min_length:
                    low = k
                    min_length = len(k)
            category_keys.append(low)
            keywords_select[s] = low
        else:
            category_keys.append(list(keywords_roots[s])[0])
            keywords_select[s] = list(keywords_roots[s])[0]
    return category_keys, keywords_roots, keywords_select


def replacement_df_keywords(df, replacement, roots=False):
    df_new = df.copy(deep=True)
    for index, row in df_new.iterrows():
        chain = row['plot_keywords']
        if pd.isnull(chain):
            continue
        new_list = []
        for s in chain.split('|'):
            low = PS.stem(s) if roots else s
            if low in replacement.keys():
                new_list.append(replacement[low])
            else:
                new_list.append(s)
        df_new.set_value(index, 'plot_keywords', '|'.join(new_list))
    return df_new


def get_synonyms(keyword):
    lemma = set()
    for ss in wordnet.synsets(keyword):
        for w in ss.lemma_names():
            index = ss.name().find('.')+1
            if ss.name()[index] == 'n':
                lemma.add(w.lower().replace('_', ' '))
    return lemma 


def test_keyword(keyword, key_count, threshold):
    return (False, True)[key_count.get(keyword, 0) >= threshold]


def count_word(df, reference_column, list1):
    keyword_count = dict()
    for s in list1:
        keyword_count[s] = 0
    for keyword_list in df[reference_column].str.split('|'):
        if type(keyword_list) == float and pd.isnull(keyword_list):
            continue
        for s in [s for s in keyword_list if s in list1]:
            if pd.notnull(s):
                keyword_count[s] += 1
    keyword_occurences = []
    for k, v in keyword_count.items():
        keyword_occurences.append([k, v])
    keyword_occurences.sort(key=lambda x: x[1], reverse=True)
    return keyword_occurences


def replacement_df_low_frequency_keywords(df, keyword_occurences):
    df_new = df.copy(deep=True)
    key_count = dict()
    for s in keyword_occurences: 
        key_count[s[0]] = s[1]    
    for index, row in df_new.iterrows():
        chain = row['plot_keywords']
        if pd.isnull(chain):
            continue
        new_list = []
        for s in chain.split('|'):
            if key_count.get(s, 4) > 3:
                new_list.append(s)
        df_new.set_value(index, 'plot_keywords', '|'.join(new_list))
    return df_new


def suppress_low_frequency_keywords(df_keywords_cleaned, replacement_dict):
    #replacement of keyword varieties by the main keyword
    df_keywords_synonyms = replacement_df_keywords(df_keywords_cleaned, replacement_dict, roots=False)
    keywords, keywords_roots, keywords_select = keywords_inventory(df_keywords_synonyms, column='plot_keywords')
    new_keyword_occurences = count_word(df_keywords_synonyms, 'plot_keywords', keywords)
    #suppressing keywords with frequency 3
    df_keywords_occurence = replacement_df_low_frequency_keywords(df_keywords_synonyms, new_keyword_occurences)
    keywords, keywords_roots, keywords_select = keywords_inventory(df_keywords_occurence, column='plot_keywords')
    return df_keywords_occurence, keywords


def replace_synonyms(df_keywords_cleaned, keywords):
    # Count of the keywords occurences
    keyword_occurences = count_word(df_keywords_cleaned, 'plot_keywords', keywords)
    keyword_occurences.sort(key=lambda x: x[1], reverse=False)
    key_count = dict()
    for s in keyword_occurences:
        key_count[s[0]] = s[1]
    # Creation of a dictionary to replace keywords by higher frequency keywords
    replacement_dict = dict()
    for index, [keyword, num_occurences] in enumerate(keyword_occurences):
        if num_occurences > 5:
            continue  # only the keywords that appear less than 5 times
        lemma = get_synonyms(keyword)
        if len(lemma) == 0:
            continue     # case of the plurals
        keyword_list = [(s, key_count[s]) for s in lemma if test_keyword(s, key_count, key_count[keyword])]
        keyword_list.sort(key=lambda x: (x[1], x[0]), reverse=True)
        if len(keyword_list) <= 1:
            continue       # no replacement
        if keyword == keyword_list[0][0]:
            continue    # replacement by itself
        replacement_dict[keyword] = keyword_list[0][0]
    #Keywords that appear both in keys and values; key1->value1, value1->value2 => key1=value2 
    for key, value in replacement_dict.items():
        if value in replacement_dict.keys():
            replacement_dict[key] = replacement_dict[value] 
    #remove less frequency keywords
    df_keywords_occurence, keywords = suppress_low_frequency_keywords(df_keywords_cleaned, replacement_dict)
    return df_keywords_occurence, keywords

def add_overview_keywords(df, bypass=False):
    if bypass : return df
    
    for index, row in df.iterrows():
        if isinstance(row['overview'], str): 
            new_keyword = []
            #print(row['overview'])
            #for s in liste_mot:
            s = nltk.word_tokenize(row['overview'])
            #print(s)
            tagged = nltk.pos_tag(s)
            #print (tagged)
            new_keyword= [x[0] for x in tagged if x[1][:1] == 'N']
            #print (new_keyword)
            
            df.set_value(index, 'overview', '|'.join(new_keyword)) 
            #df['plot_keywords']=df['plot_keywords'].map(str)+df['overview'].map(str)
        else:
            continue
    df['plot_keywords']=df['plot_keywords']+df['overview']
    return df    
