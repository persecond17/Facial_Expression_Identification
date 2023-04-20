from flask import Flask
from flask import jsonify
import pandas as pd
import random

app = Flask(__name__)

df = pd.read_csv('song_list.csv')

@app.route("/get_recommendations/")
def get_recommendations():
    emotions = ['happy', 'fear', 'sad', 'surprise', 'disgust', 'angry', 'neutral']
    predicted_emotion = emotions[random.randint(0, len(emotions) - 1)] # should be replaced by model_call function
    target = df.loc[df['category']==predicted_emotion]
    song_list = target['name'].tolist()
    song_url_dict = target[['name', 'urls']].set_index('name').to_dict()['urls']
    song_list = random.sample(song_list, 10)
    url_list = [song_url_dict[song] for song in song_list]

    response = jsonify(song_list, url_list)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

app.run(host='0.0.0.0')
