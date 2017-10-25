import nltk
import pandas as pd
from nltk.corpus import wordnet

PS = nltk.stem.PorterStemmer()

def keywords_inventory(dataframe, column = 'plot_keywords'):
    keywords_roots  = dict()  # collect the words / root
    keywords_select = dict()  # association: root <-> keyword
    category_keys = []
    icount = 0
    for s in dataframe[column]:
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

def get_synonymes(keyword):
    lemma = set()
    for ss in wordnet.synsets(keyword):
        for w in ss.lemma_names():
            # We just get the 'nouns':
            index = ss.name().find('.')+1
            if ss.name()[index] == 'n': lemma.add(w.lower().replace('_',' '))
    return lemma 

def test_keyword(keyword, key_count, threshold):
    return (False , True)[key_count.get(keyword, 0) >= threshold]

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
    return keyword_occurences

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

def supress_low_frequency_keywords(df_keywords_cleaned,replacement_dict):
    #replacement of keyword varieties by the main keyword
    df_keywords_synonyms = replacement_df_keywords(df_keywords_cleaned,
                                                                 replacement_dict,
                                                                 roots = False)
    keywords, keywords_roots, keywords_select = keywords_inventory(df_keywords_synonyms,
                                                                                     column = 'plot_keywords')
    new_keyword_occurences = count_word(df_keywords_synonyms,
                                                            'plot_keywords',
                                                             keywords)
    #supressing keywords with frequency 3
    df_keywords_occurence = replacement_df_low_frequency_keywords(df_keywords_synonyms,
                                                                                    new_keyword_occurences)
    keywords, keywords_roots, keywords_select = keywords_inventory(df_keywords_occurence,
                                                                                 column = 'plot_keywords')
    return df_keywords_occurence,keywords



def replace_synonyms(df_keywords_cleaned, keywords):
    # Count of the keywords occurences
    keyword_occurences = count_word(df_keywords_cleaned,'plot_keywords',keywords)

    keyword_occurences.sort(key = lambda x:x[1], reverse = False)
    key_count = dict()
    for s in keyword_occurences:
        key_count[s[0]] = s[1]

    # Creation of a dictionary to replace keywords by higher frequency keywords
    replacement_dict = dict()
    icount = 0
    for index, [keyword, num_occurences] in enumerate(keyword_occurences):
        if num_occurences > 5: continue  # only the keywords that appear less than 5 times
        
        lemma = get_synonymes(keyword)
        if len(lemma) == 0: continue     # case of the plurals

        liste_keywords = [(s, key_count[s]) for s in lemma
                                        if test_keyword(s, key_count, key_count[keyword])]
        liste_keywords.sort(key = lambda x:(x[1],x[0]), reverse = True)    
        if len(liste_keywords) <= 1: continue       # no replacement
        if keyword == liste_keywords[0][0]: continue    # replacement by itself

        replacement_dict[keyword] = liste_keywords[0][0]

    #Keywords that appear both in keys and values; key1->value1, value1->value2 => key1=value2 
    for key, value in replacement_dict.items():
        if value in replacement_dict.keys():
            replacement_dict[key] = replacement_dict[value] 
    #remove less frequency keywords
    df_keywords_occurence,keywords = supress_low_frequency_keywords(df_keywords_cleaned,replacement_dict)
    
    return df_keywords_occurence, keywords

def add_overview_keywords(df, keywords, bypass=False):
    if bypass : return df
    for index, row in df.iterrows():
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
            df.set_value(index, 'plot_keywords', '|'.join(new_keyword)) 
    return df    
