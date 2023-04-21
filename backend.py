from flask import Flask
from flask_cors import CORS
from flask import jsonify, request
import pandas as pd
import urllib
import random
from models_src.load_model import *

app = Flask(__name__)
CORS(app, origins='http://localhost:3000')

model_path = 'models/fer_cnn_v01.pth'
df = pd.read_csv('song_list.csv')
output_path = 'image.jpg'

def convert_binary_to_image(data, output_path):
    response = urllib.request.urlopen(data)
    with open(output_path, 'wb') as f:
        f.write(response.file.read())
    return output_path

@app.route("/get_recommendations/", methods=['POST'])
def get_recommendations():
    try:
        if 'image' not in request.form:
            return jsonify({'error': 'No image file found'}), 400

        image_file = convert_binary_to_image(request.form['image'], output_path)
        predicted_emotion = predict(model_path, image_file)
        print("Emotion: ", predicted_emotion)
        target = df[df['category'] == predicted_emotion]
        song_pool = target['name'].tolist()
        song_url_dict = target[['name', 'urls']].set_index('name').to_dict()['urls']
        song_list = random.sample(song_pool, 10)
        url_list = [song_url_dict[song] for song in song_list]
        response = jsonify({'songs': song_list, 'urls': url_list})
        return response, 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
