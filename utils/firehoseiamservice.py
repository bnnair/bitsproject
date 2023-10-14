import boto3
import botocore
import json


class firhoseIamService:
    def __init__(self) -> None:
        with open('config.json') as json_data_file:
            configJson = json.load(json_data_file)

        self.awsRegion = configJson['region']
        self.roleName = configJson['firehoserolename']
        self.policies = configJson['firehosepolicies']
        session = boto3.Session()
        self.iam_client = session.client("iam")
        self.roleArn = ""
        self.policyArn = "arn:aws:iam::aws:policy/"
        
    def deletefirehoseroleinIAM(self):
        try:
            listRoles = self.iam_client.list_roles()
            # print(listRoles['Roles'])
            for role in listRoles['Roles']:
                print("role===:", role )
                rolename = role["RoleName"]
                print(rolename)
                if rolename==self.roleName:
                    print("inside the if loop")
                    
                    listPolicies = self.iam_client.list_attached_role_policies(
                        RoleName= self.roleName
                    )
                    # print(listPolicies)
                    print(listPolicies['AttachedPolicies'])
                    for polName in listPolicies['AttachedPolicies']:
                        print("inside the for loop ==", polName['PolicyName'])
                        policyarn = self.policyArn + polName['PolicyName']
                        detach_resp = self.iam_client.detach_role_policy(
                                RoleName=self.roleName,
                                PolicyArn=policyarn
                        )    
                    delresp = self.iam_client.delete_role(
                        RoleName = self.roleName
                    )
                    break             
        except Exception as e:
            print(e)
            return False
        return True
        
    def getRoleArn(self):
        return self.roleArn    
    
    def createfirehoseroleinIAM(self):
        trustRole = '''{
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "firehose.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }'''
        try:
            if self.deletefirehoseroleinIAM():
                response = self.iam_client.create_role(
                    RoleName=self.roleName,
                    AssumeRolePolicyDocument=trustRole
                )
                print(response)
                self.roleArn = response["Role"]["Arn"]
                print("self.roleArn=====>",self.roleArn)
                for policy in self.policies:
                    policyarn = self.policyArn + policy
                    print(policyarn)
                    self.iam_client.attach_role_policy(
                        PolicyArn=policyarn,
                        RoleName=self.roleName
                    )
                
                print("Success: done attaching policy to role")
                return "success"
            else:
                return "Error happened!"
        except botocore.exceptions.ClientError as e:
            print("Error: {0}".format(e))
            return "Error"

if __name__ == '__main__':

    firehoseiamService = firhoseIamService()
    response=firehoseiamService.createfirehoseroleinIAM()
    # response=firehoseiamService.deletefirehoseroleinIAM()
    arn = firehoseiamService.getRoleArn()
    print(response,"=====", arn)


