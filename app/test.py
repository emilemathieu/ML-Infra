import sys
import os
import shutil
import time
import traceback
from pathlib import Path

import pandas as pd
from sklearn.externals import joblib

from datetime import timedelta, datetime
from functools import update_wrapper

from sklearn.ensemble import RandomForestClassifier as rf

training_data = 'data/custom.csv'
include = ['OS', 'browser', 'currentResolution', 'currentResolution', 'language', 'timeZone', 'isFlash']
dependent_variable = include[-1]

df = pd.read_csv(training_data)
df_ = df[include]
y = df_[dependent_variable]
df_ = df_[df_.columns.difference([dependent_variable])]

from sklearn.feature_extraction import FeatureHasher

h = FeatureHasher(n_features=10, non_negative=True, input_type='string')
f = h.transform(df_.T.to_dict().values())
x = f.toarray()
print(x)
clf = rf()
start = time.time()
clf.fit(x, y)
print ('Trained in %.1f seconds' % (time.time() - start))
print ('Model training score: %s' % clf.score(x, y))