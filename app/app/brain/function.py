import pandas as pd

import pickle
from sklearn.externals import joblib
from sklearn import preprocessing
import sys
sys.path.append("..")

from ..config import develop as default_config


features = ''''''
# features = '''สวัสดี
# อะไร
# ยังไง
# เมื่อไหร่
# บาย
# โครงการ
# ค้นหา
# ขอบคุณ
# หวัดดี
# ขอบคุณค่า
# สวัสดีค่ะ
# สวัสดีครับ
# มีโครงการอะไรบ้าง'''

with open(default_config.BASE_DIR + '/brain/feature.txt','r') as f:
    for line in f:
        features += line

features = features.split('\n')

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

 # /Users/matus/Desktop/taejaiBot-demo/app/app/data/data.csv
def build_model():
    training = pd.read_csv(default_config.BASE_DIR + '/data/data.csv')
    data = []
    # training = pd.read_csv('/Users/matus/Desktop/taejaiBot-demo/app/app/data/data.csv')

    for i in range(len(training)):
        messages = training.get_value(i, 'description')
        features_result = get_feature([(messages, 1),])
        features_result['class'] = training.get_value(i, 'class')
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

    pickle.dump(scaler, open(default_config.BASE_DIR + '/brain/scaler.p', 'wb'))
    joblib.dump(model, default_config.BASE_DIR + '/brain/current_model.pkl')


def get_result(messages):
    scaler = pickle.load(open(default_config.BASE_DIR + '/brain/scaler.p', 'rb'))
    model = joblib.load(default_config.BASE_DIR + '/brain/current_model.pkl')

    test_data = [get_feature([(messages, 1)])]
    x_test = pd.DataFrame(data=test_data)[features]
    x_test = scaler.transform(x_test)

    predicted = model.predict(x_test)
    return predicted
