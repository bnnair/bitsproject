import boto3
import json
import yaml
import botocore
from decouple import config
import zipfile

class FirehoseLambdaService:
    
    def __init__(self) -> None:
        
        with open('config.json') as json_data_file:
            configJson = json.load(json_data_file)
            
        self.lambdaRegion = configJson['region']
        self.lambdaName = configJson['firehoseLambda']
        self.s3RawData = configJson['s3RawData']
        self.s3RawRole = configJson['raws3triggerrole']
        # self.s3RawRoleARN = ""
        self.subnet1 = configJson['subnet_id1']
        self.subnet2 = configJson['subnet_id2']
        self.efs_sg = configJson['efs_secgroup']
        
        session = boto3.Session()
        self.lambdaClient = session.client('lambda',
                                            aws_access_key_id=config("AWS_ACCESS_KEY_ID"), 
                                            aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY"), 
                                            region_name=self.lambdaRegion)
        self.s3Client = session.client('s3',
                                       aws_access_key_id=config("AWS_ACCESS_KEY_ID"), 
                                       aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY"), 
                                       region_name=self.lambdaRegion)
                                    
        config1=[{"lambda":{
                "role" : "arn:aws:iam::521205806592:role/{}".format(self.s3RawRole),
                "runtime" : "python3.10",
                "zip" : "lambdaProcess.zip",
                "path" : "./lambdafiles/lambdaprocess.py",
                "handler" : "lambdafiles.lambdaprocess.lambda_handler"
                }}]
        yamlConfig = yaml.dump(config1)
        print(yamlConfig)
        self.configLambda = yaml.load(yamlConfig, Loader=yaml.FullLoader)
        print(self.configLambda)
        print(self.configLambda[0]['lambda']['path'])
    
    
    def updateLambdaFunc(self):
        response = self.lambdaClient.update_function_configuration(
            FunctionName=self.lambdaName,
            VpcConfig={
                'SubnetIds': [self.subnet1,
                    self.subnet2,
                ],
                'SecurityGroupIds': [
                    self.efs_sg,
                ]
            }
            )
                
    def createFirehoseLambdaFunc(self):
        # Creates a zip file containing our handler code.
        with zipfile.ZipFile(self.configLambda[0]['lambda']['zip'], 'w') as z:
            z.write(self.configLambda[0]['lambda']['path'])
        
        # Loads the zip file as binary code. 
        with open(self.configLambda[0]['lambda']['zip'], 'rb') as f:
            code = f.read()


        response = self.lambdaClient.create_function(
                    FunctionName=self.lambdaName,
                    Runtime=self.configLambda[0]['lambda']['runtime'],
                    Role= self.configLambda[0]['lambda']['role'],
                    Handler=self.configLambda[0]['lambda']['handler'],
                    Code={'ZipFile': code})
        print(response['FunctionArn'])

        response1 = self.lambdaClient.add_permission(FunctionName=response['FunctionArn'],
                                    StatementId='response2-id-2',
                                    Action='lambda:InvokeFunction',
                                    Principal='s3.amazonaws.com',
                                    SourceArn='arn:aws:s3:::'+self.s3RawData
                                    )
        #lambda_policy = self.lambdaClient.get_policy(FunctionName=response['FunctionArn'])
        s3triggerresponse = self.s3Client.put_bucket_notification_configuration(   
                            Bucket=self.s3RawData,
                            NotificationConfiguration= {'LambdaFunctionConfigurations':[
                                {'LambdaFunctionArn': response['FunctionArn'], 
                                 'Events': ['s3:ObjectCreated:*']}]})
        updateResponse = self.updateLambdaFunc() 

        return response

if __name__=='__main__':
    
    lambdafunc = FirehoseLambdaService()
    response = lambdafunc.createFirehoseLambdaFunc()
    # print(response)
    
    