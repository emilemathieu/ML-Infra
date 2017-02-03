import sys
import os
import shutil
import time
import traceback
from pathlib import Path

from flask import Flask, request, jsonify
# from flask_cors import CORS, cross_origin
import pandas as pd
from sklearn.externals import joblib
from sklearn.feature_extraction import FeatureHasher

from datetime import timedelta, datetime
from flask import make_response, request, current_app
from functools import update_wrapper

app = Flask(__name__)

# inputs
training_data = 'data/custom.csv'
include = ['OS', 'browser', 'currentResolution', 'currentResolution', 'language', 'timeZone', 'isFlash']
dependent_variable = include[-1]

model_directory = 'model'
model_file_name = '%s/model.pkl' % model_directory
model_columns_file_name = '%s/model_columns.pkl' % model_directory

# These will be populated at training time
model_columns = None
clf = None

@app.route('/predict', methods=['POST'])
def predict():
    if clf:
        try:
            json_ = request.json
            query = pd.DataFrame(json_)
            h = FeatureHasher(n_features=10, non_negative=True, input_type='string')
            x = h.transform(query.T.to_dict().values()).toarray()
            prediction = list(clf.predict(x))
            prediction = int(prediction[0])

            return jsonify({'prediction': prediction})

        except Exception as e:

            return jsonify({'error': str(e), 'trace': traceback.format_exc()})
    else:
        print ('train first')
        return 'no model here'


@app.route('/train', methods=['GET'])
def train():
    # using random forest as an example
    # can do the training separately and just update the pickles
    from sklearn.ensemble import RandomForestClassifier as rf
    from sklearn.feature_extraction import FeatureHasher

    df = pd.read_csv(training_data)
    df_ = df[include]
    y = df_[dependent_variable]
    df_ = df_[df_.columns.difference([dependent_variable])]

    h = FeatureHasher(n_features=10, non_negative=True, input_type='string')
    f = h.transform(df_.T.to_dict().values())
    x = f.toarray()
    print(x)
    print(y)

    # capture a list of columns that will be used for prediction
    global model_columns
    model_columns = list(include)
    joblib.dump(model_columns, model_columns_file_name)

    global clf
    clf = rf()
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

@app.route('/data', methods=['PUT', 'OPTIONS'])
def data():
    try:
        json_ = request.json
        print(request)
        print(json_)

        if json_ is not None:
            query = pd.DataFrame(json_)
            query['datetime'] = datetime.today()
            datetimeCol = query['datetime']
            query.drop(labels=['datetime'], axis=1,inplace = True)
            query.insert(0, 'datetime', datetimeCol)

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

@app.route('/click', methods=['PUT'])
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
            soon_enough = datetime_diff.total_seconds()/3600/2 < 1

            if len(row_index_found) > 0 and soon_enough:
                df.iloc[row_index_found[-1], df.columns.get_loc('worksClicked')] = 1

            df.to_csv(training_data+'_click', mode='w', header=True, index=False)

        return 'Success'

    except Exception as e:
        print (str(e))
        return 'Could not add click'


if __name__ == '__main__':
    try:
        port = int(sys.argv[1])
    except Exception as e:
        port = 80

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

    app.run(host='0.0.0.0', port=port, debug=True)
