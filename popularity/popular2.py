# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 12:49:39 2017

@author: katre
"""

import pandas as pd
import numpy as np

df = pd.read_pickle("processedData.pkl")



df_d = pd.DataFrame(df.director_name.drop_duplicates().dropna().reset_index(drop=True), columns = ['director_name'])


ar_m = np.where(df_d.ix[:,'director_name'] == 'Joss Whedon')

print(ar_m[0][0])

df_a1 = pd.DataFrame(df.actor_1_name.drop_duplicates().dropna().reset_index(drop=True), columns = ['actor_1_name'])

df_a2 = pd.DataFrame(df.actor_2_name.drop_duplicates().dropna().reset_index(drop=True), columns = ['actor_2_name'])

df_a3 = pd.DataFrame(df.actor_3_name.drop_duplicates().dropna().reset_index(drop=True), columns = ['actor_3_name'])

df_c = pd.DataFrame(df.companies.drop_duplicates().dropna().reset_index(drop=True), columns = ['companies'])


