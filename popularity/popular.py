# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 11:36:59 2017

@author: katre
"""

import pandas as pd
import numpy as np

df = pd.read_pickle("../data/processedData.pkl")

writer = pd.ExcelWriter("../data/popularitydata.xlsx", engine='xlsxwriter')

# Convert the dataframe to an XlsxWriter Excel object.
df.ix[:,'movie_title'].to_excel(writer, sheet_name='movie_title')

df_m = df.ix[:,'movie_title']

df_d = pd.DataFrame(df.director_name.drop_duplicates().dropna().reset_index(drop=True), columns = ['director_name'])

df_d.ix[:,'director_name'].to_excel(writer, sheet_name='director_name')

df_a1 = pd.DataFrame(df.actor_1_name.drop_duplicates().dropna().reset_index(drop=True), columns = ['actor_1_name'])

df_a1.ix[:,'actor_1_name'].to_excel(writer, sheet_name='actor_1_name')

df_a2 = pd.DataFrame(df.actor_2_name.drop_duplicates().dropna().reset_index(drop=True), columns = ['actor_2_name'])

df_a2.ix[:,'actor_2_name'].to_excel(writer, sheet_name='actor_2_name')

df_a3 = pd.DataFrame(df.actor_3_name.drop_duplicates().dropna().reset_index(drop=True), columns = ['actor_3_name'])

df_a3.ix[:,'actor_3_name'].to_excel(writer, sheet_name='actor_3_name')

df_c = pd.DataFrame(df.companies.drop_duplicates().dropna().reset_index(drop=True), columns = ['companies'])

df_c.ix[:,'companies'].to_excel(writer, sheet_name='companies')



writer.save()