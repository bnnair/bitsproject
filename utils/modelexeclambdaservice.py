import boto3
import json
import yaml
import botocore
import time
from decouple import config
import zipfile

class ModelExecLambdaService:
    
    def __init__(self) -> None:
        
        with open('config.json') as json_data_file:
            configJson = json.load(json_data_file)
            
        self.lambdaRegion = configJson['region']
        self.lambdaName = configJson['modelExecLambda']
        self.s3VideoData = configJson['s3VideoData']
        self.s3VideoRole = configJson['videos3triggerrole']
        # self.s3VideoRoleARN = ""
        self.subnet1 = configJson['subnet_id1']
        self.subnet2 = configJson['subnet_id2']
        self.efs_sg = configJson['efs_secgroup']
        
        session = boto3.Session()
        print("boto session for lambda created.")
        self.lambdaClient = session.client('lambda',
                                            aws_access_key_id=config("AWS_ACCESS_KEY_ID"), 
                                            aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY"), 
                                            region_name=self.lambdaRegion)
        print("lambda client created.")
        self.s3Client = session.client('s3',
                                       aws_access_key_id=config("AWS_ACCESS_KEY_ID"), 
                                       aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY"), 
                                       region_name=self.lambdaRegion)
        print("s3 client created.")
        config1=[{"lambda":{
                "role" : "arn:aws:iam::521205806592:role/{}".format(self.s3VideoRole),
                "runtime" : "python3.10",
                "zip" : "modelactivate.zip",
                "path" : "./lambdafiles/modelactivate.py",
                "path1" : "./lambdafiles/firemodel.py",
                "path2" : "./lambdafiles/fallmodel.py",
                "handler" : "lambdafiles.modelactivate.lambda_handler"
                }}]
        yamlConfig = yaml.dump(config1)
        print(yamlConfig)
        self.configLambda = yaml.load(yamlConfig, Loader=yaml.FullLoader)
        print(self.configLambda)
        print(self.configLambda[0]['lambda']['path'])
    
    
    def updateLambdaFunc(self):
        time.sleep(10)
        print("inside the update lambda function.")
        response = self.lambdaClient.update_function_configuration(
            FunctionName=self.lambdaName,
            VpcConfig={
                'SubnetIds': [self.subnet1,
                    self.subnet2,
                ],
                'SecurityGroupIds': [
                    self.efs_sg,
                ]
            })
                
    def createLambdaFunc(self):
        print("inside the create lambda function.")
        # Creates a zip file containing our handler code.
        with zipfile.ZipFile(self.configLambda[0]['lambda']['zip'], 'w') as z:
            z.write(self.configLambda[0]['lambda']['path'])
            z.write(self.configLambda[0]['lambda']['path1'])
            z.write(self.configLambda[0]['lambda']['path2'])
        print("zip file for lambda export created")
                             
        # Loads the zip file as binary code. 
        with open(self.configLambda[0]['lambda']['zip'], 'rb') as f:
            code = f.read()


        response = self.lambdaClient.create_function(
                    FunctionName=self.lambdaName,
                    Runtime=self.configLambda[0]['lambda']['runtime'],
                    Role= self.configLambda[0]['lambda']['role'],
                    Handler=self.configLambda[0]['lambda']['handler'],
                    Code={'ZipFile': code})
        print("launching create function for lambda. Response==>", response['FunctionArn'])

        response1 = self.lambdaClient.add_permission(FunctionName=response['FunctionArn'],
                                    StatementId='response2-id-2',
                                    Action='lambda:InvokeFunction',
                                    Principal='s3.amazonaws.com',
                                    SourceArn='arn:aws:s3:::'+self.s3VideoData
                                    )
        print("permissions added to the created function", response1)
        time.sleep(20)
        #lambda_policy = self.lambdaClient.get_policy(FunctionName=response['FunctionArn'])
        s3triggerresponse = self.s3Client.put_bucket_notification_configuration(   
                            Bucket=self.s3VideoData,
                            NotificationConfiguration= {'LambdaFunctionConfigurations':[
                                {'LambdaFunctionArn': response['FunctionArn'], 
                                 'Events': ['s3:ObjectCreated:*']}]})
        print("s3 trigger created for lambda function.", s3triggerresponse)
        updateResponse = self.updateLambdaFunc() 
        print("update lambda function completed.", updateResponse)

        return response

if __name__=='__main__':
    
    lambdafunc = ModelExecLambdaService()
    response = lambdafunc.createLambdaFunc()
    # print(response)
    
    