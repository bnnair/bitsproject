import sys
sys.path.append('/mnt/access')
import logging
import json
import boto3
import cv2
import torch
from PIL import Image
from transformers import pipeline, ViTImageProcessor

sns_client = boto3.client('sns')

class FireModel:
    def __init__(self):
        
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        
        self.model_dir = "/mnt/access/models/vit_fire_model"
        self.image_processor = ViTImageProcessor.from_pretrained(self.model_dir)
        self.logger.info("image processor initialized")
        self.logger.debug(self.image_processor)
        
        self.classifier = pipeline(task="image-classification", model=self.model_dir, image_processor=self.image_processor)
        self.logger.info("Fire model classifier loaded")
        self.logger.info(self.classifier)
        
        

    def inference(self,filepath,s3_bucket, outfilepath):
        
        try:
            topicResponse = ""
            # Reading the Video File using the VideoCapture Object
            self.logger.info("file Path of videofile:{}".format(filepath))
            video_reader = cv2.VideoCapture(filepath)
            self.logger.info("video reader initialized ")
            
            # Getting the width and height of the video
            original_video_width = int(video_reader.get(cv2.CAP_PROP_FRAME_WIDTH))
            original_video_height = int(video_reader.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
            # Writing the Overlayed Video Files Using the VideoWriter Object
            video_writer = cv2.VideoWriter(outfilepath, cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), 24,
                                    (original_video_width, original_video_height))
            self.logger.info("video writer initialized")
            pil_img = ""
            while True:
        
                # Reading The Frame
                status, frame = video_reader.read()
                if not status:
                    break
        
                pil_img=Image.fromarray(frame)
    
                # Passing the Image to the model and receiving Predicted Probabilities.
                result = self.classifier(pil_img, top_k=1)
                frame_result = result[0]['label']
                if frame_result =="fire" or frame_result =="smoke":
                    topicResponse = sns_client.publish(TopicArn='arn:aws:sns:ap-south-1:521205806592:eldercareTopic',
                                Message="Fire or Smoke has been detected. Please help!")
                    print("Message published")

                # Overlaying Class Name Text Ontop of the Frame
                cv2.putText(frame, frame_result, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                # Writing The Frame
                video_writer.write(frame)
            self.logger.info("video writer task completed.")
            video_writer.release()
            video_reader.release()
            self.logger.info("video writer and reader object released.")
        except Exception as e:
            print(e)
            raise e
        return {
            'statusCode': 200,
            'body': json.dumps('fire detection model inference completed')
        }   