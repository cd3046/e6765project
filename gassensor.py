
"""

    Teammembers:
    Lu Liu (ll3252)
    Hanzhou Gu(hg2498)
    Chengqi Dai(cd3046)

    Group code: COCO
"""

import boto3
import mraa
import math
import time
# Create an SNS client
client = boto3.client(
    "sns",
    aws_access_key_id="AKIAJC2FF4COUAWBUPVA",
    aws_secret_access_key="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",
    region_name="us-east-1"
)
topic = client.create_topic(Name="GasWARNING")
topic_arn = topic['TopicArn']  # get its Amazon Resource Name
client.subscribe(
    TopicArn=topic_arn,
    Protocol='sms',
    Endpoint="+1-612-309-9231"  # <-- number who'll receive an SMS message.
)


class gassensor(object):
        def __init__(self):
                self.gasSensor = mraa.Aio(1)
                self.refval = 0.00
        def setup(self):
                print "Please keep the Gas Sensor in clean air environment\n"
                total = 0
                for i in range(100):
                        total += self.gasSensor.read()
                average = float(total)/100
                averageval = average/1024*5.0
                print "Reference Value:" +str(round(averageval,2))
                self.refval = averageval
                return


        def readratio(self):
                #value is from 0 to 255
                a = self.gasSensor.read()
                b = float(a)/1024*5.0
                difference = b - self.refval
                if (difference > 0):
                        print "\nIncreasae in gas concentration \nGasvalue:" +str(round(b,2)) + "              difference:"+ str(round(difference,2))
                        if difference > 0.12:
                                print "Increase too much, will send an Alert"
                                client.publish(
                                    Message="# WARNING: Gas concentration increases too much", TopicArn=topic_arn
                                )

                else:
                        print "\nDecrease in gas concentration \nGasvalue:" +str(round(b,2)) + "              difference:"+ str(-1*round(difference,2))
                return b
