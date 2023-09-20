import json
import boto3

import tempfile

def reassembleVideoFile(filename):
    fileTemp = open("/tmp/{}".format(filename),"rb")
    byte = fileTemp.read()
    return byte



def lambda_handler(event, context):
    # TODO implement
    s3_client = boto3.client('s3')
    s3_target_bucket = "lambdastorevideobuck"
    for record in event['Records']:
        s3_bucket = record["s3"]["bucket"]["name"]
        print("record==", record)
        file_key = record['s3']['object']['key']
        print("file Key===", file_key)
        
        file_name = "abcdefghijkl"
        
        with open("/tmp/{}".format(file_name), 'wb') as data:
            s3_client.download_fileobj(s3_bucket, file_key, data)
        
    byteArr = reassembleVideoFile(file_name)        
        
    with tempfile.NamedTemporaryFile(mode="wb", delete="True") as mp4v:
        mp4v.write(byteArr)
        s3_client.upload_file(mp4v.name,s3_target_bucket,file_name)        
        print("-=----------------------------------------------------------")
        
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
