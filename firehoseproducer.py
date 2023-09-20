import boto3
import os
import json
from decouple import config

# AWS Kinesis Firehose Delivery Stream name

with open('config.json') as json_data_file:
    configJson = json.load(json_data_file)

firehose_stream_name = configJson["kinesisFirehoseName"]
print(firehose_stream_name)
# AWS region
aws_region = configJson["region"]
print(aws_region)
# Create a Kinesis Firehose client
session = boto3.Session()
kinesis_client = session.client('firehose', 
                                    aws_access_key_id=config("AWS_ACCESS_KEY_ID"), 
                                    aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY"),                                             
                                    region_name=aws_region)  
print(kinesis_client)
# Folder containing video files
video_folder = 'static/videos'
outfolder = "static"
# List video files in the folder
video_files = [f for f in os.listdir(video_folder)]
print(video_files)


# Iterate through each video file and send it to Kinesis Firehose
for video_file in video_files:
    file_path = os.path.join(video_folder, video_file)
    print("file_path==", file_path)
    splitfile = os.path.split(file_path)
    print(splitfile)
    filename = video_file[:-11]
    print(filename)
    # Specify a unique record ID for each record sent to Firehose
    record_id = f'{filename}'
    print("record_id==", record_id)
    data_list = []
    # Create a record with the video file content
    with open(file_path, 'rb') as video_file:
        data_record = video_file.read()

        # video_data = bytes(data_list)
        print(type(data_record))
    try:
        print("trying to put record into firehose...................................")
        # # Put the record into the Firehose stream
        response = kinesis_client.put_record(
            DeliveryStreamName=firehose_stream_name,
            Record={'Data': data_record}
        )
        print(
            f"Uploaded {video_file} to Kinesis Firehose with RecordId: {response}")

    except Exception as e:
        print(f"Failed to upload {video_file} to Kinesis Firehose: {str(e)}")
        print({response})
    print("Video file upload completed.")
