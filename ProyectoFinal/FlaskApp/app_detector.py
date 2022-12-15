from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
import pickle
import pandas as pd


app = Flask(__name__)

tfvect = TfidfVectorizer(stop_words='english', max_df=0.7)

loaded_model = pickle.load(open('model.pkl', 'rb'))

#datset usados para el entrenamiento de la app
true = pd.read_csv('True.csv')
fake = pd.read_csv('Fake.csv')
data = pd.read_csv('news.csv')

#etiquetar las noticias
true['target'] = 'true'
fake['target'] = 'fake'

x = data['text']
y = data['label']

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)

def concat_file(file_true, file_fake):
    #concatenar los archivos true y fake en un solo dataset
    dataset = pd.concat([file_true, file_fake]).reset_index(drop = True)
    dataset['text'] = dataset['text'].apply(lambda x: x.lower())
    return dataset

def shuffling_file(dataset):
    data = shuffle(dataset)
    data = data.reset_index(drop=True)
    return data

def clear_file(dataset):
    clear_data = dataset.drop(["date"],axis=1,inplace=True)
    clear_data = dataset.drop(["title"],axis=1,inplace=True)
    return clear_data

def detect_news(news):
    tfid_x_train = tfvect.fit_transform(x_train)
    tfid_x_test = tfvect.transform(x_test)
    input_data = [news]
    vectorized_input_data = tfvect.transform(input_data)
    prediction = loaded_model.predict(vectorized_input_data)
    return prediction

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        message = request.form['message']
        pred = detect_news(message)
        print(pred)
        return render_template('index.html', prediction=pred)
    else:
        return render_template('index.html', prediction="Something went wrong")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81, debug=True)