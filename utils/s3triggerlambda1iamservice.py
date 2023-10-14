import boto3
import botocore
import json


class S3TriggerLambda1IAMService():
    def __init__(self):
        with open('config.json') as json_data_file:
            configJson = json.load(json_data_file)

        self.awsRegion = configJson['region']
        self.s3RawData = configJson['s3RawData']
        self.s3RawRole = configJson['raws3triggerrole']
        self.policies = configJson['s3triggerpolicies']
        self.s3RawRoleARN = ""
        self.policyArn = "arn:aws:iam::aws:policy/"
        self.firehoseLambda = configJson['firehoseLambda']
        self.inlinepolicy = "lambdarolepolicy1"

        self.iam_client = boto3.client('iam') 



    def deleteRoleForLambda(self):
        try:
            listRoles = self.iam_client.list_roles()
            # print(listRoles['Roles'])
            for role in listRoles['Roles']:
                # print("role===:", role )
                rolename = role["RoleName"]
                print(rolename)
                if rolename==self.s3RawRole:
                    print("inside the if loop")
                    
                    listPolicies = self.iam_client.list_attached_role_policies(
                        RoleName= self.s3RawRole
                    )
                    # print(listPolicies)
                    print(listPolicies['AttachedPolicies'])
                    for polName in listPolicies['AttachedPolicies']:
                        print("inside the for loop ==", polName['PolicyArn'])
                        policyarn = polName['PolicyArn']
                        detach_resp = self.iam_client.detach_role_policy(
                                RoleName=self.s3RawRole,
                                PolicyArn=policyarn
                        )    
                    delresp = self.iam_client.delete_role(
                        RoleName = self.s3RawRole
                    )
                    break             
        except Exception as e:
            print(e)
            return False
        return True
    

    def createRoleForLambda(self):
        trustRole = '''{
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "lambda.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }'''
        # Create an inline policy
        my_inline_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "VisualEditor0",
                    "Effect": "Allow",
                    "Action": "lambda:InvokeFunction",
                    "Resource": "arn:aws:lambda:"+self.awsRegion+":521205806592:function:"+self.firehoseLambda,
                    "Condition": {
                        "StringEquals": {
                            "aws:SourceAccount": "521205806592"
                        },
                        "ArnLike": {
                            "AWS:SourceArn": "arn:aws:s3:::"+self.s3RawData
                        }
                    }
                }
            ]
        }
        
        try:
            if self.deleteRoleForLambda():
                response = self.iam_client.create_role(
                    RoleName=self.s3RawRole,
                    AssumeRolePolicyDocument=trustRole
                )
                print(response)
                self.s3RawRoleARN = response["Role"]["Arn"]
                print("self.roleArn=====>",self.s3RawRoleARN)

                for policy in self.policies:
                    policyarn = self.policyArn + policy
                    print(policyarn)
                    self.iam_client.attach_role_policy(
                        PolicyArn=policyarn,
                        RoleName=self.s3RawRole
                    )

                self.iam_client.put_role_policy(
                    PolicyName=self.inlinepolicy,
                    RoleName=self.s3RawRole,
                    PolicyDocument=json.dumps(my_inline_policy)
                )
                print("Success: done attaching policy to role")
                return "success"
            else:
                return "Error happened!"
        except botocore.exceptions.ClientError as e:
            print("Error: {0}".format(e))
            return "Error"
        
        
if __name__=='__main__':
    iamservice = S3TriggerLambda1IAMService()
    response = iamservice.createRoleForLambda()