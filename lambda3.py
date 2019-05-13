import setup
import json
import boto3
import os
import numpy as np
import PIL
from PIL import Image


MODEL_BUCKET = 'e6765'
cache = {}
s3 = boto3.resource('s3') 
url = "https://s3.amazonaws.com/chat-bot-hanzhou2/source.jpg"
def lambda_handler(event, context):
    # TODO implement
    #print(os.listdir("/tmp/"))
    filename = event["Records"][0]["s3"]["object"]["key"];
    print(filename)
    sourceFile = get_image("gu.jpg")
    targetFile = get_image(filename)
    client=boto3.client('rekognition')
   
    imageSource=open(sourceFile,'rb')
    imageTarget=open(targetFile,'rb')

    response=client.compare_faces(SimilarityThreshold=90,
                                  SourceImage={'Bytes': imageSource.read()},
                                  TargetImage={'Bytes': imageTarget.read()})
    
    s3_client = boto3.client('s3')
    if len(response['FaceMatches']) == 0:
        message = "tresspassing found " 
        s3_client.upload_file(targetFile, 'chat-bot-hanzhou2', 'source.jpg')
    else:
        faceMatch = response['FaceMatches'][0]
        similarity = faceMatch['Similarity']
        imageSource.close()
        imageTarget.close()     
        #image = np.expand_dims(image, axis=0)
        #result = model.predict(image)
        if similarity>=0.9:
            message = "successfully entered "
            print("good")
        else:
            message = "tresspassing found "
            s3_client.upload_file(targetFile, 'chat-bot-hanzhou2', 'source.jpg')
            print("bad")
    sns = boto3.client('sns')
    response = sns.publish(
    TopicArn='arn:aws:sns:us-east-1:817280606254:FaceTopic',    
    Message=message+url 
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
    
def get_image(key):
    
    local_path = os.path.join('/tmp', key)
    bucket=s3.Bucket(MODEL_BUCKET)
    bucket.download_file(key, local_path)
    return  local_path

