import boto3
import botocore
import argparse
import sys
import json
from decouple import config
from botocore import exceptions, errorfactory


class FirehoseStream:
    def __init__(self) -> None:
        with open('config.json') as json_data_file:
            configJson = json.load(json_data_file)

        self.awsRegion = configJson['region']
        self.kinesisFirehoseName = configJson['kinesisFirehoseName']
        session = boto3.Session()
        self.kinesis_client = session.client('firehose', 
                                            aws_access_key_id=config("AWS_ACCESS_KEY_ID"), 
                                            aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY"),                                             
                                            region_name=self.awsRegion)        
        
    
    def createFirehoseStream(self):
        try:
            result= self.kinesis_client.create_delivery_stream(
                DeliveryStreamName=self.kinesisFirehoseName,
                DeliveryStreamType='DirectPut',
                S3DestinationConfiguration={
                    'RoleARN': "arn:aws:iam::521205806592:role/firehosedeliveryrole",
                    'BucketARN': 'arn:aws:s3:::bitsprojects3rawdatastore',
                    'CloudWatchLoggingOptions': {
                        'Enabled': True,
                        'LogGroupName': 'kinesisfirehosedeliveryloggroup',
                        'LogStreamName': 'firehouselogstream'
                        }   
                    }
                )
            print("Firehose Create result:", result)
        except botocore.exceptions.ClientError as e:
            print(str("Error: {0}").format(e))
        return result


    def deleteVideoStream(self):
        try:
            response = self.kinesis_client.delete_delivery_stream(
                    DeliveryStreamName=self.kinesisFirehoseName,
                    AllowForceDelete=True
                )
            print("filehose delete Response=:", response)
        except exceptions.ClientError as e:
            print("Error happened while deleting ",
                self.kinesisFirehoseName, ". Error Message: ", e)


if __name__ == '__main__':

    firehoseObj = FirehoseStream()
    response=firehoseObj.createFirehoseStream()
    print(response)


