import sys
sys.path.append('/mnt/access')
import logging
import json
import boto3
import cv2
import torch
from PIL import Image
from transformers import pipeline, VivitImageProcessor

sns_client = boto3.client('sns')

class FallModel:
    def __init__(self):
        
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        
        self.model_dir = "/mnt/access/models/vit_fall_model"
        self.image_processor = VivitImageProcessor.from_pretrained(self.model_dir)
        self.logger.info("image processor initialized")
        self.logger.debug(self.image_processor)
        
        self.classifier = pipeline(task="video-classification", model=self.model_dir, image_processor=self.image_processor)
        self.logger.info("Fall model classifier loaded")
        self.logger.info(self.classifier)
        
        

    def inference(self,filepath,s3_bucket):
        
        try:
            # Reading the Video File using the VideoCapture Object
            self.logger.info("file Path of videofile:{}".format(filepath))

            # Passing the Image to the model and receiving Predicted Probabilities.
            result = self.classifier(filepath, top_k=1)
            print("result===>",result)
            if result[0]['label'] =="FallDown":
                topicResponse = sns_client.publish(TopicArn='arn:aws:sns:ap-south-1:521205806592:eldercareTopic',
                            Message="Fall of an elderly has been detected. Please coordinate and help!")
                print("Message published")

        except Exception as e:
            print(e)
            raise e
        return {
            'statusCode': 200,
            'body': json.dumps('Fall detection Model inference completed')
        }   