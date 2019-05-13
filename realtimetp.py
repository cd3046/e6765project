
"""

    Teammembers:
    Lu Liu (ll3252)
    Hanzhou Gu(hg2498)
    Chengqi Dai(cd3046)

    Group code: COCO

"""

# *********************************************************************************************
# Program to update dynamodb with latest data from mta feed. It also cleans up stale entried from db
# Usage python dynamodata.py
# *********************************************************************************************
#!/usr/bin/python

import threading
import json,time,sys
from collections import OrderedDict
from threading import Thread
import urllib3
from decimal import Decimal
urllib3.disable_warnings(urllib3.exceptions.SNIMissingWarning)
import boto3
from boto3.dynamodb.conditions import Key,Attr
import aws
#sys.path.append('../utils')
from time import sleep
DYNAMO_TABLE_NAME = 'realtimedata'
dynamodb = aws.getResource('dynamodb', 'us-east-1')
APIKEY = '19bd06b92a72a0af7ebf0a9cb0b5c58c'

from datetime import datetime
import sys
import mraa
import math
import time
from lightsensor import lightsensor
from gassensor import gassensor
from airqualitysensor import airqualitysensor


import datetime
import sys
import math
import time
B = 4275         # B value of the thermistor
R0 = 100000         # R0 = 100k

def first_task():

    while True:
        now = datetime.datetime.now()
        #print now
        ts = int(time.time())
        #print(ts)
        if now.minute % 2 == 0:
            print str(now.hour) + ":" + str(now.minute) + " upload the data"
            lightval = light.readvalue_average()
            gasval = gas.readratio()
            aqval = aq.readvalue_average()

            table_dynamo.put_item(Item={
                            'timestamp' : ts,
                            'Lightvalue':  Decimal(lightval),
                            'gasvalue': Decimal(gasval),
                            'airqualityvalue': Decimal(aqval),
            })
            print "Update successful"
        else:
            print "sleep 1 minS at"+ str(now.minute)
        time.sleep(60)






try:
    # exam if the table exits.
    try:
    #1. create new table
        table_dynamo = dynamodb.create_table(
            TableName = DYNAMO_TABLE_NAME,
            KeySchema=[
            {
                'AttributeName': 'timestamp',
                'KeyType': 'HASH'  #Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'timestamp',
                'AttributeType': 'N'
            },

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
        )
        time.sleep(15)
        print("Setup:New Table Created")
    except:
        table_dynamo = dynamodb.Table(DYNAMO_TABLE_NAME)
        print("Setup:Table Already Exists")
	while (1):
		tempSensor = mraa.Aio(3)
		#convert the temperature
		a = tempSensor.read()
		R = 1023.0/a-1.0;
		R = R0*R
		temperature = 1.0/(math.log(R/R0)/B+1/298.15)-273.15 
		temperature = round(temperature, 2)
		ts = int(time.time())
		table_dynamo.put_item(Item={
						'timestamp' : ts,
						'temperature':  Decimal(str(temperature)),

		})
		print "Update successful"

		time.sleep(2)


except KeyboardInterrupt:
    exit
