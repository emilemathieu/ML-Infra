import sys
import os
import shutil
import time
import traceback
from pathlib import Path

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import pandas as pd
from sklearn.externals import joblib
from sklearn.feature_extraction import FeatureHasher
from sklearn.feature_extraction import DictVectorizer
import numpy as np

from datetime import timedelta, datetime
from flask import make_response, request, current_app
from functools import update_wrapper
import logging

app = Flask(__name__)
app.logger.setLevel(logging.WARNING)
app.debug = True
CORS(app, resources=r'/*')

# inputs
training_data = 'users_data.csv'
include = ['OS', 'browser', 'language', 'timeZone', 'worksClicked']
dependent_variable = include[-1]

model_directory = 'model'
model_file_name = '%s/model.pkl' % model_directory
model_columns_file_name = '%s/model_columns.pkl' % model_directory

# These will be populated at training time
model_columns = None
clf = None

@app.route('/predict', methods=['POST'])
@cross_origin(allow_headers=['Content-Type'])
def predict():
    print('predict')
    if clf:
        try:
            json_ = request.json
            query = pd.DataFrame(json_)
            query = query[include[:-1]]
            D = query.T.to_dict().values()
            print(D)
            # v = DictVectorizer()
            # F = v.fit_transform(D)
            # x = F.toarray()
            h = FeatureHasher(n_features=10, non_negative=True, input_type='string')
            x = h.transform(D).toarray()
            print(x)
            prediction = list(clf.predict(x))
            prediction = int(prediction[0])

            add_data_point(prediction, json_)

            return jsonify({'prediction': prediction})

        except Exception as e:

            return jsonify({'error': str(e), 'trace': traceback.format_exc()})
    else:
        print ('train first')
        add_data_point(np.nan, json_)
        return 'no model here'

# @app.route('/data', methods=['PUT', 'OPTIONS'])
# @cross_origin(allow_headers=['Content-Type'])
def add_data_point(prediction, json_):
    print('add_data_point')
    try:
        if json_ is not None:
            query = pd.DataFrame(json_)
            
            if Path(training_data).is_file():
                df = pd.read_csv(training_data)
                row_index_found = df[df['fingerprint'] == int(query['fingerprint'])].index.tolist()

                if len(row_index_found) > 0:

                    string_date = df.iloc[row_index_found[-1], df.columns.get_loc('datetime')]
                    past = datetime.strptime(string_date, "%Y-%m-%d %H:%M:%S.%f")
                    now = datetime.today()
                    datetime_diff = now - past
                    soon_enough = datetime_diff.total_seconds() < 3600 * 2

                    if soon_enough:
                        return 'Too soon to add new point'

            query['datetime'] = datetime.today()
            datetimeCol = query['datetime']
            query.drop(labels=['datetime'], axis=1,inplace = True)
            query.insert(0, 'datetime', datetimeCol)

            query['worksClickedPrediction'] = prediction

            print(query)
            if Path(training_data).is_file():
                print('file exists')
                query.to_csv(training_data, mode='a', header=False, index=False)
            else:
                print('does not exists')
                query.to_csv(training_data, mode='w', header=True, index=False)

        return 'Success'

    except Exception as e:
        print (str(e))
        return 'Could not add new point'

@app.route('/train', methods=['GET'])
def train():
    # using random forest as an example
    # can do the training separately and just update the pickles
    from sklearn.ensemble import RandomForestClassifier as rf
    from sklearn.linear_model import LogisticRegression as lr
    from sklearn.feature_extraction import FeatureHasher
    from sklearn.feature_extraction import DictVectorizer

    df = pd.read_csv(training_data)
    df_ = df[include]

    y = df_[dependent_variable]
    y = y.fillna(value=0);
    print(y)
    df_ = df_[df_.columns.difference([dependent_variable])]
    
    D = df_.T.to_dict().values()
    print(D)
    h = FeatureHasher(n_features=10, non_negative=True, input_type='string')
    f = h.transform(D)
    x = f.toarray()
    # print(x)

    # v = DictVectorizer()
    # F = v.fit_transform(D)
    # x = F.toarray()
    print(x)

    # capture a list of columns that will be used for prediction
    global model_columns
    model_columns = list(include)
    joblib.dump(model_columns, model_columns_file_name)

    global clf
    # clf = rf()
    clf = lr()
    start = time.time()
    clf.fit(x, y)
    print ('Trained in %.1f seconds' % (time.time() - start))
    print ('Model training score: %s' % clf.score(x, y))

    joblib.dump(clf, model_file_name)

    return 'Success'


@app.route('/wipe', methods=['GET'])
def wipe():
    try:
        shutil.rmtree('model')
        os.makedirs(model_directory)
        return 'Model wiped'

    except Exception as e:
        print (str(e))
        return 'Could not remove and recreate the model directory'


@app.route('/click', methods=['PUT'])
@cross_origin(allow_headers=['Content-Type'])
def click():
    try:
        json_ = request.json
        print(request)
        print(json_)

        if json_ is not None:
            query = pd.DataFrame(json_)
            now = datetime.today()

            df = pd.read_csv(training_data)
            if 'worksClicked' not in df.columns:
                df['worksClicked'] = 0

            row_index_found = df[df['fingerprint'] == int(query['fingerprint'])].index.tolist()
            string_date = df.iloc[row_index_found[-1], df.columns.get_loc('datetime')]
            past = datetime.strptime(string_date, "%Y-%m-%d %H:%M:%S.%f")

            datetime_diff = now - past
            soon_enough = datetime_diff.total_seconds() < 3600 * 2

            if len(row_index_found) > 0 and soon_enough:
                df.iloc[row_index_found[-1], df.columns.get_loc('worksClicked')] = 1

            df.to_csv(training_data, mode='w', header=True, index=False)

        return 'Success'

    except Exception as e:
        print (str(e))
        return 'Could not add click'

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == '__main__':
    try:
        port = int(sys.argv[1])
    except Exception as e:
        port = 8080

    try:
        clf = joblib.load(model_file_name)
        print ('model loaded')
        model_columns = joblib.load(model_columns_file_name)
        print ('model columns loaded')

    except Exception as e:
        print ('No model here')
        print ('Train first')
        print (str(e))
        clf = None

    app.run(host='127.0.0.1', port=port, debug=True)
