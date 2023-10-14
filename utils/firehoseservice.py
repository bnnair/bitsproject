import boto3
import botocore
import argparse
import sys
import json
from decouple import config
from botocore import exceptions, errorfactory
from firehoseiamservice import firhoseIamService



class FirehoseStream:
    def __init__(self):
        with open('config.json') as json_data_file:
            configJson = json.load(json_data_file)

        self.awsRegion = configJson['region']
        self.kinesisFirehoseName = configJson['kinesisFirehoseName']
        self.s3RawData = configJson['s3RawData']
        ## Create the iam role for firehose
        firehoseiamObj = firhoseIamService()
        succeed = firehoseiamObj.createfirehoseroleinIAM()
        self.roleArn =""
        if succeed:
            self.roleArn = firehoseiamObj.getRoleArn()
        else:
            return "Error creating role in IAM for Firehose."
        
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
                    'RoleARN': self.roleArn,
                    'BucketARN': 'arn:aws:s3:::'+ self.s3RawData,
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
    # response=firehoseObj.deleteVideoStream()
    print(response)


