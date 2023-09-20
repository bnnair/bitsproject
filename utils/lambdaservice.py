import boto3
import json
import yaml
from decouple import config
import zipfile

class FirehoseLambda:
    
    def __init__(self) -> None:
        
        with open('config.json') as json_data_file:
            configJson = json.load(json_data_file)
        self.lambdaRegion = configJson['region']
        self.lambdaName = configJson['firehoseLambdaName']
        
        
        
        session = boto3.Session()
        self.lambdaClient = session.client('lambda',
                                            aws_access_key_id=config("AWS_ACCESS_KEY_ID"), 
                                            aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY"), 
                                            region_name=self.lambdaRegion)                                           

        self.s3Client = session.client('s3',
                                            aws_access_key_id=config("AWS_ACCESS_KEY_ID"), 
                                            aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY"), 
                                            region_name=self.lambdaRegion)  

        self.configLambda = yaml.load("""
                            role: arn:aws:iam::521205806592:role/lambda_s3-trigger_role
                            runtime: python3.10
                            zip: lambdaProcess.zip
                            path: ./lambdaprocess.py
                            handler: lambdaprocess.lambda_handler
                            """, Loader=yaml.FullLoader)
        
    def createFirehoseLambdaFunc(self):
        # Creates a zip file containing our handler code.
        with zipfile.ZipFile(self.configLambda['zip'], 'w') as z:
            z.write(self.configLambda['path'])
        
        # Loads the zip file as binary code. 
        with open(self.configLambda['zip'], 'rb') as f:
            code = f.read()


        response = self.lambdaClient.create_function(
                    FunctionName=self.lambdaName,
                    Runtime=self.configLambda['runtime'],
                    Role= self.configLambda['role'],
                    Handler=self.configLambda['handler'],
                    Code={'ZipFile': code})
        print(response['FunctionArn'])

        response1 = self.lambdaClient.add_permission(FunctionName=response['FunctionArn'],
                                    StatementId='response2-id-2',
                                    Action='lambda:InvokeFunction',
                                    Principal='s3.amazonaws.com',
                                    SourceArn='arn:aws:s3:::bitsprojects3rawdatastore'
                                    )
        #lambda_policy = self.lambdaClient.get_policy(FunctionName=response['FunctionArn'])
        s3triggerresponse = self.s3Client.put_bucket_notification_configuration(   
                            Bucket='bitsprojects3rawdatastore',
                            NotificationConfiguration= {'LambdaFunctionConfigurations':[
                                {'LambdaFunctionArn': response['FunctionArn'], 
                                 'Events': ['s3:ObjectCreated:*']}]})


        return response

if __name__=='__main__':
    
    lambdafunc = FirehoseLambda()
    response = lambdafunc.createFirehoseLambdaFunc()
    # print(response)
    
    