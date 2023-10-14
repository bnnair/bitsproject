import sys
sys.path.append('/mnt/access')
import os
import json
import boto3
import tempfile
import logging
from concurrent.futures import ThreadPoolExecutor
from lambdafiles.firemodel import FireModel
from lambdafiles.fallmodel import FallModel


logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')
logger.info("s3 client initialized")
s3 = boto3.resource("s3")
logger.info("S3 resource initialized")
s3_infer_bucket = os.environ['s3_infer_bucket']



def getTempVideoFile(filename):
    fileTemp = open(filename,"rb")
    byte = fileTemp.read()
    return byte


def lambda_handler(event, context):
    # TODO implement
    logger.info('event parameter: {}'.format(event))

    try:
        record = event['Records'][0]
        s3_bucket = record["s3"]["bucket"]["name"]
        logger.info("record==:{}".format(record))
        file_key = record['s3']['object']['key']
        
        logger.info("file Key===:{}".format(file_key))
        if file_key.startswith("camvideo"):
            file_key = file_key.replace("+"," ")
            logger.info("file_key after replace:{}".format(file_key))
        
        ## These two lines are only for testing        
        # file_key="camvideo2023-10-02 18-23-43.mp4"

        s3.meta.client.download_file(s3_bucket, file_key, '/tmp/'+file_key)
        logger.info("downloaded the video file from s3 bucket")

        fileTemp = "/tmp/{}".format(file_key)
        name, extn = os.path.splitext(fileTemp)
        fireoutfilepath = name+"_fireprocessed"+extn
        falloutfilepath = name+"_fallprocessed"+extn
        logger.info("read the file from the downloaded file.")
        
        firemodel = FireModel()
        fallmodel = FallModel()
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            fire_thread = executor.submit(firemodel.inference, fileTemp,s3_bucket,fireoutfilepath)
            fall_thread = executor.submit(fallmodel.inference, fileTemp,s3_bucket)
        
        fire_response = fire_thread.result()
        fall_response = fall_thread.result()

        return_response = {
            "fire": fire_response,
            "fall": fall_response
        }
        print("return_response===>:", return_response)
        # # response=firemodel.inference(filepath=fileTemp, s3_bucket=s3_bucket, outfilepath=fireoutfilepath)
        # # logger.info("response==>:{}".format(response))
        # # logger.info("filedata got from the inference model")

        # response=fallmodel.inference(filepath=fileTemp, s3_bucket=s3_bucket, outfilepath=falloutfilepath)
        # logger.info("response==>:{}".format(response))
        # # logger.info("filedata got from the inference model")

        byteArr = getTempVideoFile(fireoutfilepath) 
            
        falloutfilename = file_key.replace(extn,"_fallprocessed"+extn)
        logger.debug("outfilename:{}".format(falloutfilename))
        with tempfile.NamedTemporaryFile(mode="wb", delete="True") as mp4v:
            mp4v.write(byteArr)
            s3_client.upload_file(mp4v.name,s3_infer_bucket,falloutfilename)        
        logger.info("-----------------------------------------------------------")

    except Exception as e:
        print(e)
        raise e

    return {
        'statusCode': 200,
        'body': json.dumps('completed the inference and uploaded the inferred data!')
    }
