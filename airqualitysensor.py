
"""

    Teammembers:
    Lu Liu (ll3252)
    Hanzhou Gu(hg2498)
    Chengqi Dai(cd3046)

    Group code: COCO
"""


import mraa
import math
import time


class airqualitysensor(object):
        def __init__(self):
                self.airqualitySensor = mraa.Aio(2)

        def readvalue(self):
                #value is from 0 to 255
                a = self.airqualitySensor.read()
                #print "airqualityvalue:" +str(a)
                return a

        def readvalue_average(self):
                #calculate the average value in 30s
                total = 0
                for x in range(10):
                        total += self.readvalue()
                        #time.sleep(3)
                average = total/10
                print "Average airquality value:" +str(average)
                self.process(average)
                return average
        def process(self,sensor_value):
                if sensor_value > 150:
                        print "High pollution"
                elif sensor_value > 50:
                        print "Low pollution"
                else:
                        print "Air fresh"
                return
