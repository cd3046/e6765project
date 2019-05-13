
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


class lightsensor(object):
        def __init__(self):
                self.lightSensor = mraa.Aio(0)

        def readvalue(self):
                #value is from 0 to 255
                a = self.lightSensor.read()
                print "Lightvalue:" +str(a)
                return a

        def readvalue_average(self):
                #calculate the average value in 30s
                total = 0
                for x in range(10):
                        total += self.readvalue()
                    

                average = total/10
                print "Average Lightvalue:" +str(average)
                return average
