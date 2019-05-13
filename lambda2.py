import setup
import json
import boto3
import os
import numpy as np
import keras
import PIL
from PIL import Image
from keras.applications import MobileNet
from keras.layers import Conv2D, Dense, Dropout, Flatten, MaxPooling2D
from keras.models import Sequential
from keras import optimizers

MODEL_BUCKET = 'e6765'
cache = {}
s3 = boto3.resource('s3')

def lambda_handler(event, context):
    # TODO implement
    #print(os.listdir("/tmp/"))
    filename = event["Records"][0]["s3"]["object"]["key"];
    model = get_model("model.h5")
    
    data = np.load("sensor.npy")
    data = np.expand_dims(data, axis=0)
    result = model.predict(data)\
    Threshold = 0.1
    loss = calculateMSE(data, result)
    sns = boto3.client('sns')
    message = ""
    if loss >= Threshold:
        message = "anomaly detected"
        print("bad")
    response = sns.publish(
    TopicArn='arn:aws:sns:us-east-1:817280606254:FaceTopic',    
    Message=message 
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
    
def get_model(key):
    if key in cache:
        return cache[key]
    local_path = os.path.join('/tmp', key)

    # download from S3
    if not os.path.isfile(local_path):
        bucket=s3.Bucket(MODEL_BUCKET)
        bucket.download_file(key, local_path)
    
    inc_model = Sequential()
    inc_model.add(Conv2D(32, (3, 3), activation='relu',
                            input_shape=(150, 150, 3)))
    inc_model.add(MaxPooling2D((2, 2)))
    inc_model.add(Conv2D(64, (3, 3), activation='relu'))
    inc_model.add(MaxPooling2D((2, 2)))
    inc_model.add(Conv2D(128, (3, 3), activation='relu'))
    inc_model.add(MaxPooling2D((2, 2)))
    inc_model.add(Conv2D(128, (3, 3), activation='relu'))
    inc_model.add(MaxPooling2D((2, 2)))
    inc_model.add(Flatten())
    inc_model.add(Dense(512, activation='relu'))
    inc_model.add(Dense(1, activation='sigmoid'))   
    inc_model.load_weights(local_path)
    cache[key] = inc_model
    return cache[key]
    
def get_image(key):
    
    local_path = os.path.join('/tmp', key)
    bucket=s3.Bucket(MODEL_BUCKET)
    bucket.download_file(key, local_path)
    img = Image.open(local_path)
    img = img.resize((150,150), PIL.Image.ANTIALIAS)
    image = np.asarray(img)
    return  image
