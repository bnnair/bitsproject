from flask import Flask, render_template, send_from_directory
import boto3
import json
from decouple import config

app = Flask(__name__)

with open('config.json') as json_data_file:
    configJson = json.load(json_data_file)

# Configure AWS S3 settings
AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
AWS_REGION = configJson["region"]
S3_BUCKET_NAME = configJson['s3BucketinferStore']

print(AWS_ACCESS_KEY_ID)
print(AWS_SECRET_ACCESS_KEY)
print(AWS_REGION)
print(S3_BUCKET_NAME)
s3 = boto3.resource('s3')

@app.route('/')
def index():
    # Get the list of videos from the S3 bucket
    bucket = s3.Bucket(S3_BUCKET_NAME)
    # videos = bucket.objects.all()
    videos = bucket.objects.filter(Prefix='videos/')
    print(videos)
    # print(videos1)
    
    for video in videos:
        print("aaaaa=:",video.get()['Body'])
    
    # Render the HTML template
    return render_template('collection.html', videos=videos)

# This function serves the video file from S3
@app.route('/videos/<filename>')
def serve_video(filename):
    print("===========:",filename)
    return send_from_directory('videos', filename)

if __name__ == '__main__':
    app.run(debug=True)