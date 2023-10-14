from flask import Flask, render_template, Response
from flask_sse import sse
import boto3
import json
import time
import threading
import redis
from decouple import config
# from waitress import serve


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

s3 = boto3.client('s3') #, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_REGION

# Configure Redis for Flask-SSE
REDIS_URL = "redis://localhost:6379/"  # Replace with your Redis server URL
app.config["REDIS_URL"] = REDIS_URL

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

@app.route('/')
def index():
    return render_template('index1.html')


def generate_video_urls():
    with app.app_context():
        try:
        # while True:
            # List objects in your S3 bucket
            # objects = s3.list_objects(Bucket=S3_BUCKET_NAME)
            # # print("object===>", objects)
            # video_urls = []

            # # Filter for video files (you can change the filter criteria)
            # for obj in objects.get('Contents', []):
            #     if obj['Key'].endswith('.mp4'):
            #         video_url = s3.generate_presigned_url( ClientMethod='get_object', Params={ 'Bucket': S3_BUCKET_NAME, 'Key': obj['Key'] } )
            #         # video_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{obj['Key']}"
            #         # print("Video url===>", video_url)
            #         video_urls.append(video_url + "\n\n")

            
            # print("urls=====>", video_urls)
            # Send video URLs to all connected clients
            # data = { "video_urls": video_urls }
            sse.publish({ "video_urls": "this is a test" }, type="message")

            # Sleep for a while before checking again (adjust the interval as needed)
            time.sleep(10)
        except Exception as e:
            print(e)
            raise(e)

def generate():
    pass

@app.route('/events')
def events():
        response = Response(generate())
        # response.headers['Cache-Control'] = 'no-cache'
        # response.headers['X-Accel-Buffering'] = 'no'
        response.headers['Content-Type'] = 'text/event-stream'
        # response.headers['Accept-Ranges']= 'bytes'
        return response




if __name__ == '__main__':
    # Start a separate thread to continuously generate and send video URLs
    video_thread = threading.Thread(target=generate_video_urls)
    video_thread.daemon = True
    video_thread.start()

    app.register_blueprint(sse, url_prefix='/events')
    app.run(debug=True)
    # serve(app, port='5000')
