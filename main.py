from flask import Flask, render_template, request, jsonify

import uuid
from google.cloud import storage
import pymongo
import os

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)


# access to mongo in python
# myclient = pymongo.MongoClient("vidipedia-cluster-lfvr7.gcp.mongodb.net:27017")

# mydb = myclient["mydatabase"]
# mycol = mydb["customers"]
# mydict = { "name": "John", "address": "Highway 37" }

# x = mycol.insert_one(mydict)
# print(myclient.list_database_names())

def upload_to_bucket(blob_name, file, bucket_name):
    """ Upload data to a bucket"""

    # Explicitly use service account credentials by specifying the private key
    # file.
    storage_client = storage.Client.from_service_account_json('creds.json')

    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_file(file)

    # returns a public url
    return blob.public_url


@app.route('/')
def root():
    return render_template('index.html')


@app.route('/video/<videoname>')
def video(videoname):
    url = "https://storage.googleapis.com/vidipedia-video-storage/{}.mp4".format(videoname)
    return render_template('video.html', title=videoname, videoURL=url)


@app.route('/upload', methods=['POST'])
def upload():
    # TODO: sanitize so only mp4 is valid
    if request.method == 'POST':
        try:
            videofile = request.files.get('file', None)  # Maybe last None
            videoname = videofile.filename
            if not videofile:
                return jsonify({'msg': 'Missing image, can not change avatar'})
            url = upload_to_bucket(videoname, videofile, 'vidipedia-video-storage')
            return jsonify({'msg': 'File uploaded successfully, can be viewed at: ' + str(url)})
        except Exception as err:
            return jsonify({'msg': str(err)})


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
