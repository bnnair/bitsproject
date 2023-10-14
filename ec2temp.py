import boto3
from decouple import config
import json

def getinstanceid():
    with open('config.json') as json_data_file:
        configJson = json.load(json_data_file)

    awsRegion = configJson['region']
    ec2 = boto3.resource('ec2', aws_access_key_id=config("AWS_ACCESS_KEY_ID"),
                                        aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY"),
                                        region_name = awsRegion)
    
    for instance in ec2.instances.all():
        print (instance.id , instance.state)
        
        
if __name__=="__main__":
    getinstanceid()
    