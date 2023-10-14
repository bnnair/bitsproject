import boto3
import json
import os
from decouple import config
import botocore
from time import sleep
 
# REGION = 'us-east-1'


# DISK_SIZE_GB = 16
# DEVICE_NAME = '/dev/sda1'
# NAME = 'codeflex-ec2'
# OWNER = 'codeflex'
# RUNID = 'ec2-1'
# SUBNET_ID = 'subnet-02cd0004db6df93fa'
# SECURITY_GROUPS_IDS = ['sg-067401826623ccbad']
# PUBLIC_IP = None
# ROLE_PROFILE = 'ec2-creator-role'
 
class EC2Service():
    def __init__(self):
        with open('config.json') as json_data_file:
            configJson = json.load(json_data_file)

        self.awsRegion = configJson['region']
        self.ec2Name = configJson['ec2Name']
        self.securitygrp = configJson['securitygroup']
        self.ec2InstanceId =""
        self.amiImageId = configJson['ami_image_id']
        self.instanceType = configJson['instance_type']
        self.disk_size = configJson['disk_size_gb']
        self.device_name = configJson['device_name']
        self.keyname = configJson['keyname']
        session = boto3.Session()
        # ,
        self.ec2 = session.resource('ec2', aws_access_key_id=config("AWS_ACCESS_KEY_ID"),
                                        aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY"),
                                        region_name = self.awsRegion)
        if self.ec2 is None:
            raise ConnectionError("Could not create ec2 resource! Check your connection or aws config!")


    def terminateEC2(self,instanceId):
        response = self.ec2.instances.filter(InstanceIds = [instanceId]).terminate()
        return response


    def assign_tags_to_instance(self):
        print("Waiting for instance to be ready ...")
        sleep(10)
        print("Assigning tags to instance " + self.ec2InstanceId)
        self.ec2.create_tags(Resources=[self.ec2InstanceId], Tags=[{'Key': 'Name', 'Value': self.ec2Name}])
        print("Tags assigned to instance successfully!")
 
 
    def launch_ec2_instance(self):
        try:
            print("Attempting to create ec2 Instance in region: %s" % self.awsRegion)           
            blockDeviceMappings = [
                {
                    'DeviceName': self.device_name,
                    'Ebs': {
                        'DeleteOnTermination': True,
                        'VolumeSize': self.disk_size,
                        'VolumeType': 'gp2'
                    }
                },
            ]
            instance = self.ec2.create_instances(ImageId=self.amiImageId,
                                            InstanceType=self.instanceType,
                                            SecurityGroupIds=self.securitygrp,
                                            KeyName=self.keyname,
                                            MinCount=1, MaxCount=1,
                                            BlockDeviceMappings=blockDeviceMappings)
            if instance is None:
                raise Exception("Failed to create instance! Check the AWS console to verify creation or try again")
        
            print("Instance created and launched successfully!")
            print("#### Instance id: " + instance[0].id)
            self.ec2InstanceId = instance[0].id
            self.assign_tags_to_instance()
            os.environ['EC2_INSTANCE'] =self.ec2InstanceId 

            return instance
        except Exception as e:
            print (e)
            return "Failure to launch an EC2 instance."

    
if __name__ == "__main__":
    ec2Service = EC2Service()
    instance = ec2Service.launch_ec2_instance()
    # response = ec2Service.terminateEC2('i-0c52d3141cd4969cb')
    # ec2Service.mount_efs()
    print(instance)

                