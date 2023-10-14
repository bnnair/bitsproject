import boto3
import botocore
import json


class S3TriggerLambda2IAMService():
    def __init__(self):
        with open('config.json') as json_data_file:
            configJson = json.load(json_data_file)

        self.awsRegion = configJson['region']
        self.s3videoData = configJson['s3VideoData']
        self.s3VideoRole = configJson['videos3triggerrole']
        self.policies = configJson['s3triggerpolicies']
        self.s3VideoRoleARN = ""
        self.policyArn = "arn:aws:iam::aws:policy/"
        self.modelExecLambda = configJson['modelExecLambda']
        self.inlinepolicy1 = "videolambdapolicy"
        self.inlinepolicy2 = "snslambdapolicy"

        self.iam_client = boto3.client('iam') 



    def deleteRoleForLambda(self):
        try:
            listRoles = self.iam_client.list_roles()
            # print(listRoles['Roles'])
            for role in listRoles['Roles']:
                # print("role===:", role )
                rolename = role["RoleName"]
                print(rolename)
                if rolename==self.s3VideoRole:
                    print("inside the if loop")
                    
                    listPolicies = self.iam_client.list_attached_role_policies(
                        RoleName= self.s3VideoRole
                    )
                    # print(listPolicies)
                    print(listPolicies['AttachedPolicies'])
                    for polName in listPolicies['AttachedPolicies']:
                        print("inside the for loop ==", polName['PolicyArn'])
                        policyarn = polName['PolicyArn']
                        detach_resp = self.iam_client.detach_role_policy(
                                RoleName=self.s3VideoRole,
                                PolicyArn=policyarn
                        )    
                    delresp = self.iam_client.delete_role(
                        RoleName = self.s3VideoRole
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
        my_inline_policy1 = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "VisualEditor0",
                    "Effect": "Allow",
                    "Action": "lambda:InvokeFunction",
                    "Resource": "arn:aws:lambda:"+self.awsRegion+":521205806592:function:"+self.modelExecLambda,
                    "Condition": {
                        "StringEquals": {
                            "aws:SourceAccount": "521205806592"
                        },
                        "ArnLike": {
                            "AWS:SourceArn": "arn:aws:s3:::"+self.s3videoData
                        }
                    }
                }
            ]
        }
        my_inline_policy2 = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "VisualEditor0",
                    "Effect": "Allow",
                    "Action": "sns:Publish",
                    "Resource": "*"
                }
            ]
        }      
        
        try:
            if self.deleteRoleForLambda():
                response = self.iam_client.create_role(
                    RoleName=self.s3VideoRole,
                    AssumeRolePolicyDocument=trustRole
                )
                print(response)
                self.s3VideoRoleARN = response["Role"]["Arn"]
                print("self.roleArn=====>",self.s3VideoRoleARN)

                for policy in self.policies:
                    policyarn = self.policyArn + policy
                    print(policyarn)
                    self.iam_client.attach_role_policy(
                        PolicyArn=policyarn,
                        RoleName=self.s3VideoRole
                    )

                self.iam_client.put_role_policy(
                    PolicyName=self.inlinepolicy1,
                    RoleName=self.s3VideoRole,
                    PolicyDocument=json.dumps(my_inline_policy1)
                )
                self.iam_client.put_role_policy(
                    PolicyName=self.inlinepolicy2,
                    RoleName=self.s3VideoRole,
                    PolicyDocument=json.dumps(my_inline_policy2)
                )
                print("Success: done attaching policy to role")
                return "success"
            else:
                return "Error happened!"
        except botocore.exceptions.ClientError as e:
            print("Error: {0}".format(e))
            return "Error"
        
        
if __name__=='__main__':
    iamservice = S3TriggerLambda2IAMService()
    response = iamservice.createRoleForLambda()