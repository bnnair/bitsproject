from utils.ec2service import EC2Service
from utils.efsservice import EFSService
import paramiko
import json
import time
import boto3
import select
import sys
from decouple import config

class InfraServices():
    def __init__(self):
        with open('config.json') as json_data_file:
            configJson = json.load(json_data_file)
                
        self.awsRegion = configJson['region']
        self.retry_time = 10
        self.ec2_client = boto3.client('ec2', aws_access_key_id=config("AWS_ACCESS_KEY_ID"), 
                                            aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY"),                                             
                                            region_name=self.awsRegion )
        ec2 = EC2Service()
        efs = EFSService()    

        result = efs.createEFS()
        print("EFS response===:", result)
        self.efsFileSysId = result['FileSystemId']
        print("efs file systemid==>", self.efsFileSysId)
        
        instance = ec2.launch_ec2_instance()
        print("EC2 instance===>", instance)
        self.ec2Instance = instance
        # Wait until instance enters the running state
        instance[0].wait_until_running()
        time.sleep(10)
        # Load updated attributes to populate public_ip_address
        instance[0].reload()
        # Read public IP address
        self.ec2Ip = instance[0].public_ip_address
        print("self.ec2Ip====>",self.ec2Ip)
        
    def getCommandList(self):
        tempList = []
        commandList = []
        
        # removing the new line characters
        with open("./site/ec2Script.txt") as f:
            tempList = [line.strip() for line in f]
        
        for line in tempList:
            if(len(line)!=0 and not line.startswith("#")):
                commandList.append(line)
            
        print(commandList)
        return commandList
    
    def get_sshClient(self):
        print("get ssh client method")
        key = paramiko.RSAKey.from_private_key_file(r"C:\\Users\\bnnai\\.ssh\\bits-key.pem") ##pemfile

        i = 0
        while True:
            print("Trying to connect to (%i/%i)" % (i, self.retry_time))
            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                # Here 'ubuntu' is user name and 'instance_ip' is public IP of EC2
                print("ip addr ===>", self.ec2Ip)
                client.connect(hostname=self.ec2Ip, username="ubuntu", pkey=key)
                break
            except paramiko.AuthenticationException:
                print("Authentication failed when connecting to %s" % self.ec2Ip)
                sys.exit(1)
            except:
                print("Could not SSH to %s, waiting for it to start" % self.ec2Ip)
                i += 1
                time.sleep(2)

            # If we could not connect within time limit
            if i >= self.retry_time:
                print("Could not connect to %s. Giving up" % self.ec2Ip)
                sys.exit(1)
        return client   

    
    def ec2pythoninstall(self):
        time.sleep(10)
        print("inside the ec2 python and nfs utils install function")
        commandList = ["sudo apt install -y python3-pip",
                       "sudo mkdir -p /mnt","sudo chmod -R 777 /mnt"]
        sshClient = self.get_sshClient()
        self.execute_cmd(sshClient,commandList)
        # close the client connection once the job is done
        sshClient.close()
    
    
    def mountEFS(self):
        time.sleep(10)
        print("inside the mount efs function")
        command = "sudo mount -t nfs4 -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport "+self.efsFileSysId+".efs."+self.awsRegion+".amazonaws.com:/ /mnt"
        print(command)
        commandList =[]
        commandList.append(command)
        sshClient = self.get_sshClient()
        self.execute_cmd(sshClient,commandList)
        # close the client connection once the job is done
        sshClient.close()
        
    def ec2update(self):
        print("inside the ec2 update and upgrade function")
        commandList = ["sudo apt update", "sudo apt upgrade -y", "sudo apt install -y nfs-common"]
        sshClient = self.get_sshClient()
        self.execute_cmd(sshClient,commandList)
        # close the client connection once the job is done
        sshClient.close()
        
            
    def efsdependencyInstall(self):
        time.sleep(10)
        print("inside the efs dependency installation function")
        commandList = self.getCommandList()
        sshClient = self.get_sshClient()
        self.execute_cmd(sshClient,commandList)
        # close the client connection once the job is done
        sshClient.close()
        
    def execute_all(self):
        self.ec2update()
        self.ec2pythoninstall()
        self.mountEFS()
        self.efsdependencyInstall()
        
        
    def execute_cmd(self, client, commandList):
        try:
            # After connection is successful
            # Send the command
            for command in commandList:
                # print command
                print("> " + command)
                time.sleep(1)
                # execute commands
                stdin, stdout, stderr = client.exec_command(command)
                print("-----------------------------------------------------------")
                # TODO() : if an error is thrown, stop further fules
                # Wait for the command to terminate
                while not stdout.channel.exit_status_ready():
                    # Only print data if there is data to read in the channel
                    if stdout.channel.recv_ready():
                        rl, wl, xl = select.select([ stdout.channel ], [ ], [ ], 0.0)
                        if len(rl) > 0:
                            tmp = stdout.channel.recv(1024)
                            output = tmp.decode()
                            print (output)

        except Exception as e:
            print(e)
            client.close()
            sys.exit(1)
     
     
        
if __name__ == '__main__':
    infraservice = InfraServices()
    infraservice.execute_all()
    