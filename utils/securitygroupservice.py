import boto3
import json
from decouple import config
import botocore
import time

class SGService():
    def __init__(self):
        with open('config.json') as json_data_file:
            configJson = json.load(json_data_file)
        json_data_file.close()
        
        self.awsRegion = configJson['region']
        self.ec2_client = boto3.client("ec2")
        response = self.ec2_client.describe_vpcs()
        print("response ==>", response)
        self.vpc_id = response.get("Vpcs",[{}])[0].get("VpcId","")
        print("VPC ID====>", self.vpc_id)
    
    def createEc2SG(self):
        try:
            response = self.ec2_client.create_security_group(GroupName='myec2_sg',
                        Description='security group for my bits project',
                        VpcId=self.vpc_id,
                        TagSpecifications=[
                        {
                            'ResourceType': 'security-group',
                            'Tags': [
                                {
                                    'Key': 'Name',
                                    'Value': 'ec2-project-group'
                                },
                            ]
                        },
                        ],)
            security_group_id = response['GroupId']
            print('Security Group Created %s in vpc %s.' % (security_group_id, self.vpc_id))
            data = self.ec2_client.authorize_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions=[
                    {'IpProtocol': 'tcp',
                    'FromPort': 80,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}],
                    'ToPort': 80,
                    },
                    {'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}],
                    'ToPort': 22,
                    },
                    {'IpProtocol': 'tcp',
                    'FromPort': 443,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}],
                    'ToPort': 443,
                    },
                ],)
            print('Ingress Successfully Set %s' % data)   
            return response    
        except Exception as e:
            print(e)
            return None


    def createEFSSG(self):
        try:
            response = self.ec2_client.create_security_group(GroupName='myefs_sg1',
                        Description='security group for my bits project',
                        VpcId=self.vpc_id,
                        TagSpecifications=[
                        {
                            'ResourceType': 'security-group',
                            'Tags': [
                                {
                                    'Key': 'Name',
                                    'Value': 'efs-project-group'
                                },
                            ]
                        },
                    ],)
            security_group_id = response['GroupId']
            print('Security Group Created %s in vpc %s.' % (security_group_id, self.vpc_id))
            data = self.ec2_client.authorize_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions=[
                    {'IpProtocol': 'tcp',
                    'FromPort': 2049,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}],
                    'ToPort': 2049,
                    },
                ],)
            print('Ingress Successfully Set %s' % data)    
            return response   
        except Exception as e:
            print(e)
            return None
            
    def createSG(self):
        ec2response = self.createEc2SG()
        efsresponse = self.createEFSSG()
        with open('config.json') as json_data:
            data = json.load(json_data)
        json_data.close()
        data['securitygroup'] = [ec2response['GroupId'],efsresponse['GroupId']]
        data['efs_secgroup'] = efsresponse['GroupId']
        with open('config.json', "w") as jsonfile:
            myJSON = json.dump(data, jsonfile) # Writing to the file
            print("Write successful")
            jsonfile.close()
        return ec2response,efsresponse

    def deleteSGs(self):
        try:
            with open('config.json') as json_data:
                data = json.load(json_data)
            json_data.close()
            for sg in data['securitygroup']:
                response = self.ec2_client.delete_security_group(
                    GroupId= sg,
                )
                print(response)
                time.sleep(5)
            data['securitygroup'] = ""
            data['efs_secgroup'] = ""    

            with open('config.json', "w") as jsonfile:
                myJSON = json.dump(data, jsonfile) # Writing to the file
                print("Write successful")
                jsonfile.close()            

        except Exception as e:
            print(e)
            

if __name__ == "__main__":
    sgService = SGService()
    # response= sgService.createSG()
    # print(response)
    sgService.deleteSGs()