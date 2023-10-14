import os
import sys

import json
import boto3
import random
import tempfile
import cv2
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)
s3_target_bucket = "bitsvideodatastore"

def getTempVideoFile(filename):
    fileTemp = open("/tmp/{}".format(filename),"rb")
    byte = fileTemp.read()
    return byte

def reAssembleFrame(url, filename):
    logger.info("inside the assemble frame method")

    filepath = open("/tmp/{}".format(filename), "wb")       
    try:
        fourcc = cv2.VideoWriter_fourcc("m", "p", "4", "v")
        video_writer = cv2.VideoWriter(filepath.name, fourcc, 24, (480, 640))
        cap = cv2.VideoCapture(url)
        logger.info("After video capture using fileobject")
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            width, height, layer = frame.shape
            frame = cv2.resize(frame, dsize=(width, height))
            video_writer.write(frame)

        logger.info("video writer task completed.")
        video_writer.release()
        cap.release()
        logger.info("video writer and reader object released.")
    except Exception as e:
        print(e)
  


def lambda_handler(event, context):

    logger.info('event parameter: {}'.format(event))
    s3_client = boto3.client('s3')

    for record in event['Records']:
        s3_bucket = record["s3"]["bucket"]["name"]
        logger.info("record==:{}".format(record))
        file_key = record['s3']['object']['key']
        logger.info("file Key===:{}".format(file_key))
        
        dt = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        file_name = "camvideo"+str(dt)+".mp4"        
        logger.info("file_name--:{}".format(file_name))

        dlfilepath ="/tmp/{}".format("temp")
        logger.info("dlfilepath--:{}".format(dlfilepath))
        with open(dlfilepath, 'wb') as data:
            s3_client.download_fileobj(s3_bucket, file_key, data)
        
        logger.info("store in temp dir in S3")
        reAssembleFrame(dlfilepath, file_name)
        logger.info("Assembly of frame completed.")
        byteArr = getTempVideoFile(file_name)        

    with tempfile.NamedTemporaryFile(mode="wb", delete="True") as mp4v:
        mp4v.write(byteArr)
        s3_client.upload_file(mp4v.name,s3_target_bucket,file_name)        
        logger.info("-----------------------------------------------------------")
        
    return {
        'statusCode': 200,
        'body': json.dumps({
            "message": "Video saved to s3://"+s3_target_bucket+"/"+file_name,
        }),
    }
