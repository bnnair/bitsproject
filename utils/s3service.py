import boto3
import json
import botocore
from decouple import config

class S3Service:
    
    def __init__(self) -> None:
        
        with open('config.json') as json_data_file:
            configJson = json.load(json_data_file)

        self.s3Region = configJson['region']
        self.s3RawData = configJson['s3RawData']
        self.s3VideoData = configJson['s3VideoData']
        self.s3InferData = configJson['s3InferData']
        
        session = boto3.Session()
        self.s3Client = session.client('s3',
                                       aws_access_key_id=config("AWS_ACCESS_KEY_ID"), 
                                       aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY"), 
                                       region_name=self.s3Region)         

    def createS3Bucket(self, flag):
        if flag=="Raw":
            bucketName = self.s3RawData
        elif flag =="Infer":
            bucketName=self.s3InferData
        else:
            bucketName=self.s3VideoData
            
        print(bucketName)                
        print("Location:", self.s3Region )
        try:
            response = self.s3Client.create_bucket(Bucket=bucketName, 
                                        CreateBucketConfiguration={'LocationConstraint': self.s3Region})
            
            print(response)
            access_public = self.s3Client.put_public_access_block(
                            Bucket=bucketName,
                            PublicAccessBlockConfiguration={
                                'BlockPublicAcls': True,
                                'IgnorePublicAcls': True,
                                'BlockPublicPolicy': True,
                                'RestrictPublicBuckets': True
                            },
                        )
            print(bucketName,"==:",access_public)
        except botocore.exceptions.ClientError as error:
            print("Error occured while creating s3 bucket:{}".format(error))
            raise error
        except botocore.exceptions.ParamValidationError as error:
            raise ValueError('The parameters you provided are incorrect: {}'.format(error))
            
        return response
    
    
    
    def deleteS3Bucket(self, flag):
        if flag=="Raw":
            bucketName = self.s3RawData
        elif flag =="Infer":
            bucketName=self.s3InferData
        else:
            bucketName=self.s3VideoData
            
        print(bucketName)  
        try:
            response = self.s3Client.delete_bucket(
                        Bucket=bucketName
                        )
            print(bucketName,"==:",response)
        except botocore.exceptions.ClientError as error:
            print("Error occured while creating s3 bucket:{}".format(error))
            raise error

        print(response)


if __name__ == '__main__':

    s3ServiceObj = S3Service()
    # resultRaw=s3ServiceObj.createS3Bucket("Raw")
    # print(resultRaw)
    resultVideo=s3ServiceObj.createS3Bucket("video")
    print(resultVideo)
    # resultRaw = s3ServiceObj.deleteS3Bucket("video")
    # print(resultRaw)
    # resultInfer = s3ServiceObj.deleteS3Bucket("Infer")