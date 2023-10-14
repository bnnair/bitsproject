import boto3
from flask import Flask, render_template, send_file, Response
from decouple import config
import json
import cv2

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

# Create an S3 client
s3 = boto3.client('s3')

# Get the S3 bucket name
bucket_name = S3_BUCKET_NAME

# Get a list of all the video files in the S3 bucket
objects = s3.list_objects(Bucket=bucket_name)['Contents']

# Create a list of all the video names
video_names = []


# Render the HTML template
@app.route('/')
def index():
    return render_template('render.html')

def generate():
    
    # Get a list of all the video files in the S3 bucket
    objects = s3.list_objects(Bucket=bucket_name)['Contents']
    
    for object in objects:
        # if object['Key'].endswith('.mp4'):
        #     # video_names.append(object['Key'])
        #     # print("video_name==:", video_names)   
        print("key==:", object['Key'])
        url = s3.generate_presigned_url( ClientMethod='get_object', Params={ 'Bucket': bucket_name, 'Key': object['Key'] } )
        print(url)
        # # Get the video object from S3
        # video_obj = s3.get_object(url)
        # print(video_obj['Body'])

        cap = cv2.VideoCapture(url)
        
        while True:
            ret, frame = cap.read()
            ret, jpeg = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

@app.route('/video')
def video():
    
        return Response(generate(),
                mimetype='multipart/x-mixed-replace; boundary=frame')



# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
