from flask import Flask, render_template, request, redirect
import os
import boto3
from boto3 import Session

app = Flask(__name__)

# Define the path to the video folder
video_folder = 'static/videos/'

# AWS credentials and Firehose delivery stream name
# aws_access_key_id = 'YOUR_ACCESS_KEY_ID'
# aws_secret_access_key = 'YOUR_SECRET_ACCESS_KEY'
firehose_delivery_stream = 'bitsprojectstream'
aws_region = 'ap-south-1'

session = Session()
credentials = session.get_credentials()
curr_cred = credentials.get_frozen_credentials()

# Initialize the AWS Firehose client
client = boto3.client(
    'firehose',
    region_name=aws_region,
    aws_access_key_id=curr_cred.access_key,
    aws_secret_access_key=curr_cred.secret_key
)

# Get a list of video files in the folder
video_files = [file for file in os.listdir(video_folder)]

@app.route('/')
def index():
    send_video_to_firehose(video_files)
    return render_template('index.html', video_files=video_files)

@app.route('/upload', methods=['POST'])
def upload():
    if 'video' in request.files:
        video_file = request.files['video']
        if video_file.filename != '':
            video_file.save(os.path.join(video_folder, video_file.filename))
            
            # Send the video to Kinesis Firehose
            send_video_to_firehose(video_file.filename)

    return redirect('/')

def send_video_to_firehose(videofiles):
    for file in videofiles:
        filename = file
        
        video_path = os.path.join(video_folder, filename)
        # Specify a unique record ID for each record sent to Firehose
        record_id = f'video_{filename}'
        try:
           
            with open(video_path, 'rb') as video_file:
                response = client.put_record(
                    DeliveryStreamName=firehose_delivery_stream,
                    Record={'Data': video_file.read()
                            }
                )
                print(f"Uploaded {filename} to Kinesis Firehose. Record ID: {response['RecordId']}")
        except Exception as e:
            print(f"Failed to upload {video_file} to Kinesis Firehose: {str(e)}")

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000)
    # app.run(debug=True)