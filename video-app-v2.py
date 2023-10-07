from flask import Flask, render_template, request, redirect, Response
import os
import boto3
from boto3 import Session
import cv2
import json
from decouple import config

app = Flask(__name__)

with open('config.json') as json_data_file:
    configJson = json.load(json_data_file)

## Kinesis firehose delivery stream
firehose_delivery_stream = configJson["kinesisFirehoseName"]
print(firehose_delivery_stream)
# AWS region
aws_region = configJson["region"]
print(aws_region)
# Define the path to the video folder
video_folder = configJson["folder_path"]
frame_folder = configJson["frame_path"]

session = Session()
# credentials = session.get_credentials()
# curr_cred = credentials.get_frozen_credentials()

# Initialize the AWS Firehose client
client = boto3.client(
    'firehose',
    region_name=aws_region,
    aws_access_key_id=config("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY")
)

def send_to_firehose(frame):
        
        # Convert the frame to bytes
        frame_bytes = cv2.imencode('.jpg', frame)[1].tobytes()

        try:
            # Send the frame to the Firehose delivery stream
            response = client.put_record(
                DeliveryStreamName=firehose_delivery_stream,
                Record={
                    'Data': frame_bytes
                }
            )
            print("Frame sent to Firehose successfully")
        except Exception as e:
            print(f"Error sending frame to Firehose: {str(e)}")
    

@app.route('/')
def index():
    return render_template('index.html')


def generate():
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        ret, jpeg = cv2.imencode('.jpg', frame)
        
        send_to_firehose(frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

@app.route('/webcam')
def webcam():
    
        return Response(generate(),
                mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/folder')
def folder():
    # Get a list of video files in the folder
    video_files = [file for file in os.listdir(video_folder)]
    # send_video_to_firehose(video_files)
    return render_template('index.html',source_type='video', video_files=video_files)

@app.route('/upload', methods=['POST'])
def upload():
    if 'video' in request.files:
        video_files =[]
        video_file = request.files['video']
        if video_file.filename != '':
            video_file.save(os.path.join(video_folder, video_file.filename))
        video_files.append(video_file.filename)
        print(video_files)
            # Send the video to Kinesis Firehose
            # send_video_to_firehose(video_file.filename)
    return render_template('index.html',source_type='video', video_files=video_files)


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