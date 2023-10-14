import boto3
from time import sleep
import json
from decouple import config



class EFSService:
    def __init__(self):
        with open('config.json') as json_data_file:
            configJson = json.load(json_data_file)

        self.awsRegion = configJson['region']
        self.efsName = "bijuEfs" #configJson['efsName']
        self.efsFileSysId = ""
        self.efs_sg = configJson['efs_secgroup']
        self.subnetId1 = configJson['subnet_id1']
        self.subnetId2 = configJson['subnet_id2']
        session = boto3.Session(region_name =self.awsRegion)
        self.efs_client = session.client('efs', 
                                            aws_access_key_id=config("AWS_ACCESS_KEY_ID"), 
                                            aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY"),                                             
                                            region_name=self.awsRegion) 

    
    
    
    def createEFS(self):
        response = self.efs_client.create_file_system(
            PerformanceMode='generalPurpose',
            Encrypted=True,
            ThroughputMode='elastic',
            Backup=False,
            Tags=[
                    {
                        'Key': 'Name',
                        'Value': self.efsName
                    },
                ]
        )
        # print(response)
        self.efsFileSysId = response['FileSystemId']
        print("efs sys id==>", self.efsFileSysId)

        response1 = self.createAccessPoint()

        return response
    
    def createAccessPoint(self):
        sleep(10)
        response = self.efs_client.create_access_point(
                FileSystemId=self.efsFileSysId,
                    PosixUser={
                'Uid': 1001,
                'Gid': 1001,
            },
            RootDirectory={
                'Path': '/access',
                'CreationInfo': {
                    'OwnerUid': 1001,
                    'OwnerGid': 1001,
                    'Permissions': '0775'
                }
            }
        )

        self.create_misc()
        # print(response)
        return response
    
    def create_misc(self):
        sleep(10)
        try:
            lifecycle = self.efs_client.put_lifecycle_configuration(
                FileSystemId=self.efsFileSysId,
                LifecyclePolicies=[
                    {
                        'TransitionToIA': 'AFTER_30_DAYS',
                    },
                ]
            )
            # print("lifeecycle===>", lifecycle)
            sub1= self.efs_client.create_mount_target(
                FileSystemId=self.efsFileSysId,
                SubnetId=self.subnetId1,
                SecurityGroups=[self.efs_sg]
            )
            # print("sub1==>", sub1)
            sub2=self.efs_client.create_mount_target(
                FileSystemId=self.efsFileSysId, 
                SubnetId=self.subnetId2,
                SecurityGroups=[self.efs_sg]
            )
            # print("sub2===>", sub2)

        except Exception as e:
            print(e)

    def deleteEFS(self, fileSystemId):
        response = self.efs_client.delete_file_system(
            FileSystemId=fileSystemId
        )
        # print(response)
        return response

    
if __name__ == '__main__':
    
    efsService =  EFSService()
    result = efsService.createEFS()
    # result = efsService.deleteEFS('fs-011231d812b9ed19a')
    # print(result)
