from flask import Flask
from flask import request
from flask import Response
from flask import render_template
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import csv
import time
import json
import random
import os
from datetime import datetime

import threading
import sys


from collections import OrderedDict
from threading import Thread
import urllib3
urllib3.disable_warnings(urllib3.exceptions.SNIMissingWarning)
import boto3
import aws
from boto3.dynamodb.conditions import Key,Attr
from time import sleep
import datetime
DYNAMO_TABLE_NAME1 = 'project'
DYNAMO_TABLE_NAME2 = "temperature"
REALTIME_TABLE = "realtime"
dynamodb = aws.getResource('dynamodb', '*****')
APIKEY = '***********'

table_dynamo1 = dynamodb.Table(DYNAMO_TABLE_NAME1)
table_dynamo2 = dynamodb.Table(DYNAMO_TABLE_NAME2)
real_table = dynamodb.Table(REALTIME_TABLE)


app = Flask(__name__)

_default_directory = os.path.abspath('static/')

def transfer_to_json():
    now = datetime.datetime.now()
    d = datetime.datetime.strptime(str(now), "%Y-%m-%d %H:%M:%S.%f")
    now_ts = int(time.mktime(d.timetuple()))
    project_items = table_dynamo1.scan(FilterExpression=Attr('timestamp').lt(now_ts) & Attr('timestamp').gt(now_ts - 24*3600))
    temp_items = table_dynamo2.scan(FilterExpression=Attr('timestamp').lt(now_ts) & Attr('timestamp').gt(now_ts - 24*3600))
    light = {}
    air = {}
    gas = {}
    humi = {}
    temper = {}

    for item in project_items['Items']:
        light[int(item['timestamp'])] = str(item['Lightvalue'])
        air[int(item['timestamp'])] = str(item['airqualityvalue'])
        gas[int(item['timestamp'])] = str(item['gasvalue'])

    light_gra = {"categories": [], 'data': []}
    key_climb1 = sorted(light.keys())
    for i in key_climb1:
        light_gra["categories"].append(i)
        light_gra['data'].append(light[i])
    light = json.dumps(light_gra, indent=2)

    air_gra = {"categories": [], 'data': []}
    key_climb2 = sorted(air.keys())
    for i in key_climb2:
        air_gra["categories"].append(i)
        air_gra['data'].append(air[i])
    air = json.dumps(air_gra, indent=2)

    gas_gra = {"categories": [], 'data': []}
    key_climb3 = sorted(gas.keys())
    for i in key_climb3:
        gas_gra["categories"].append(i)
        gas_gra['data'].append(gas[i])
    gas = json.dumps(gas_gra, indent=2)


    for item in temp_items['Items']:
        humi[int(item['timestamp'])] = str(item['humidity'])
        temper[int(item['timestamp'])] = str(item['temperature'])

    humi_gra = {"categories": [], 'data': []}
    key_climb4 = sorted(humi.keys())
    for i in key_climb4:
        humi_gra["categories"].append(i)
        humi_gra['data'].append(humi[i])
    humi = json.dumps(humi_gra, indent=2)

    temper_gra = {"categories": [], 'data': []}
    key_climb5 = sorted(temper.keys())
    for i in key_climb5:
        temper_gra["categories"].append(i)
        temper_gra['data'].append(temper[i])
    temper = json.dumps(temper_gra, indent=2)


    data = [light, air, gas, humi, temper]
    return data


@app.route('/')
def main():
    return render_template('final.html')


@app.route('/newdata', methods=['GET'])
def create_data():
    now = datetime.datetime.now()
    d = datetime.datetime.strptime(str(now), "%Y-%m-%d %H:%M:%S.%f")
    now_ts = int(time.mktime(d.timetuple()))
    temper = real_table.scan(FilterExpression=Attr('timestamp').lt(now_ts) & Attr('timestamp').gt(now_ts - 24 * 3600))
    temp_new = {}
    for item in temper['Items']:
        temp_new[int(item['timestamp'])] = str(item['temperature'])
    key_climb1 = sorted(temp_new.keys())

    d = datetime.datetime.fromtimestamp(int(key_climb1[-1]))
    str_time = str(d.hour) + ":" + str(d.minute) + ':' + str(d.second) + ' AM'
    result = {"new": temp_new[key_climb1[-1]], "time": str_time}
    result = json.dumps(result, indent=2)
    response = Response(result, status=200, mimetype="text/plain")

    return response

@app.route('/getdata', methods=['GET'])
def getdata():

    data = transfer_to_json()
    light = data[0]
    light = json.loads(light)

    light_time = {'categories': [], 'data': []}
    for cate in light['categories']:
        d = datetime.datetime.fromtimestamp(int(cate))
        str_time = str(d.hour) + ":" + str(d.minute) + ':' + str(d.second)
        light_time['categories'].append(str_time)
    for da in light['data']:
        light_time['data'].append(da)
    light = light_time


    light = json.dumps(light, indent=2)
    response = Response(light, status=200, mimetype="text/plain")
    return response

@app.route('/gethumi', methods=['GET'])
def gethumi():
    data = transfer_to_json()
    humidity = data[3]
    response = Response(humidity, status=200, mimetype="text/plain")
    return response

@app.route('/gethumi&gas', methods=['GET'])
def gethumi_and_gas():
    data = transfer_to_json()
    humidity = data[3]
    gas = data[2]
    humidity = json.loads(humidity)
    gas = json.loads(gas)

    humidity_time = {'categories': [], 'data': []}
    for cate in humidity['categories']:
        d = datetime.datetime.fromtimestamp(int(cate))
        str_time = str(d.hour) + ":" + str(d.minute) + ':' + str(d.second)
        humidity_time['categories'].append(str_time)
    for da in humidity['data']:
        humidity_time['data'].append(da)

    tt = []
    length = len(humidity_time['categories'])
    for i in range(length):
        if humidity_time['data'][i] == '0':
            tt.append(i)
    ttt = 0
    for i in tt:
        humidity_time['categories'].remove(humidity_time['categories'][i-ttt])
        humidity_time['data'].remove(humidity_time['data'][i-ttt])
        ttt = ttt + 1
    humidity = humidity_time

    gas_time = {'categories': [], 'data': []}
    for cate in gas['categories']:
        d = datetime.datetime.fromtimestamp(int(cate))
        str_time = str(d.hour) + ":" + str(d.minute) + ':' + str(d.second)
        gas_time['categories'].append(str_time)
    for da in gas['data']:
        gas_time['data'].append(da)
    gas = gas_time


    data = {'humi_categories': [], 'humi_data': [], 'gas_categories': [], 'gas_data': []}
    data['humi_categories'] = humidity['categories']
    data['humi_data'] = humidity['data']
    data['gas_categories'] = gas['categories']
    data['gas_data'] = gas['data']
    data = json.dumps(data, indent=2)

    response = Response(data, status=200, mimetype="text/plain")
    return response

@app.route('/getair', methods=['GET'])
def getair():
    data = transfer_to_json()
    air = data[1]
    air = json.loads(air)

    air_time = {'categories': [], 'data': []}
    for cate in air['categories']:
        d = datetime.datetime.fromtimestamp(int(cate))
        str_time = str(d.hour) + ":" + str(d.minute) + ':' + str(d.second)
        air_time['categories'].append(str_time)
    for da in air['data']:
        air_time['data'].append(da)
    air = air_time

    air = json.dumps(air, indent=2)
    response = Response(air, status=200, mimetype="text/plain")
    return response

@app.route('/getgas', methods=['GET'])
def getgas():
    data = transfer_to_json()
    gas = data[2]
    response = Response(gas, status=200, mimetype="text/plain")
    return response

@app.route('/gettemper', methods=['GET'])
def gettemper():
    data = transfer_to_json()
    temper = data[4]
    response = Response(temper, status=200, mimetype="text/plain")
    return response

@app.route('/gettemp', methods=['GET'])
def gettemp():
    now = datetime.datetime.now()
    d = datetime.datetime.strptime(str(now), "%Y-%m-%d %H:%M:%S.%f")
    now_ts = int(time.mktime(d.timetuple()))
    temper = real_table.scan(FilterExpression=Attr('timestamp').lt(now_ts) & Attr('timestamp').gt(now_ts - 5*60))
    temp_new = {}
    for item in temper['Items']:
        temp_new[int(item['timestamp'])] = str(item['temperature'])
    key_climb1 = sorted(temp_new.keys())

    result = {"categories": [], 'data': []}
    if len(key_climb1) >= 10:
        length = 10
    else:
        length = len(key_climb1)
    for i in range(length):
        d = datetime.datetime.fromtimestamp(int(key_climb1[-length]))
        str_time = str(d.hour) + ":" + str(d.minute) + ':' + str(d.second)
        result['categories'].append(str_time)
        result['data'].append(temp_new[key_climb1[-length]])


    result = json.dumps(result, indent=2)
    response = Response(result, status=200, mimetype="text/plain")
    return response

def loadData(csvFile):
    data = []
    with open(csvFile, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            data.append(row)
    return data


if __name__ == '__main__':
    app.run(port=7000)


