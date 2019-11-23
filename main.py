from flask import Flask, render_template, request, jsonify

import uuid
from google.cloud import storage

import os

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)


def upload_to_bucket(blob_name, file, bucket_name):
    """ Upload data to a bucket"""

    # Explicitly use service account credentials by specifying the private key
    # file.
    storage_client = storage.Client.from_service_account_json('creds.json')

    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_file(file)

    #returns a public url
    return blob.public_url

@app.route('/')
def root():
    return render_template('index.html')

@app.route('/video')
def video():
    return render_template('videoPage.html', title="Testtitle", videoURL="https://cdn.videvo.net/videvo_files/video/premium/video0028/small_watermarked/happy07_preview.mp4")

@app.route('/upload')
def upload_file():
   return render_template('upload.html')
	
@app.route('/uploader', methods = ['GET', 'POST'])
def uploader():
    # TODO: sanitize so only mp4 is valid
    if request.method == 'POST':
        try:
            videofile = request.files.get('file', None) # Maybe last None
            if not videofile:
                return jsonify({'msg': 'Missing image, can not change avatar'})
            filename = '{}.mp4'.format(uuid.uuid4())
            url = upload_to_bucket(filename, videofile, 'vidipedia-video-storage')
            return jsonify({'msg': 'File uploaded successfully, can be viewed at: '+str(url)})
        except Exception as err:
            return jsonify({'msg': 'Error uploading file'})
		
if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
