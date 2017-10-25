
#Custom libs
from dataload import *
from preprocess import *
from model import *
import os
import pandas as pd

if not os.path.isfile('../data/processedData.pkl'):
	preprocess()

df = pd.read_pickle('../data/processedData.pkl')

selection = dict()
#for i in range(0, 20, 2):
#selection[i] = 
find_similarities(df, 16, del_sequels = False, verbose = True)
    #print(selection)

