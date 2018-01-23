import pandas as pd

import pickle
from sklearn.externals import joblib
from sklearn import preprocessing

from ..config import develop as default_config


features = '''
สวัสดี
อะไร
ยังไง
เมื่อไหร่
บาย
'''


def get_feature(messages):
    features_result = {}
    features_count = 0
    for feature in features:
        pattern = feature
        for message, score in messages:
            matches = pattern in message
            if matches:
                try:
                    features_result[feature] += 1 * score
                except KeyError:
                    features_result[feature] = 1 * score
                features_count = features_count + 1
            else:
                try:
                    features_result[feature] += 0
                except KeyError:
                    features_result[feature] = 0
    features_result['feature_not_found'] = 1 if features_count == 0 else 0
    return features_result


def build_model():

    data = []
    training = pd.read_csv(default_config.BASE_DIR + '/data/data.csv')

    for messages in training:
        features_result = get_feature([
            (messages, 1),
        ])
        data.append(features_result)

    df = pd.DataFrame(data=data)

    x_data = df[features]
    scaler = preprocessing.Normalizer().fit(x_data)

    x_data = scaler.transform(x_data)
    y_data = df['class']

    from sklearn.linear_model import LogisticRegression
    model = LogisticRegression()
    model.fit(x_data, y_data)
    model.score(x_data, y_data)

    pickle.dump(scaler, open(default_config.BASE_DIR + '/data/scaler.p', 'wb'))
    joblib.dump(model, default_config.BASE_DIR + '/data/current_model.pkl')


def get_result(messages):
    scaler = pickle.load(open(default_config.BASE_DIR + '/data/scaler.p', 'rb'))
    pca = pickle.load(open(default_config.BASE_DIR + '/data/pca.p', 'rb'))
    model = joblib.load(default_config.BASE_DIR + '/data/current_model.pkl')

    test_data = [get_feature([(messages, 1)])]
    x_test = pd.DataFrame(data=test_data)[features]
    x_test = scaler.transform(x_test)
    x_test = pca.transform(x_test)

    predicted = model.predict(x_test)
    return predicted
