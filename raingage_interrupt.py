#!/usr/bin/env python
#
# Aailable device: Tipping-bucket Rain gauge
# Product number: SMR29-C
# Serial communication protocol: Pulse(interrupt function)
# Purpose:
# Measure rainfall intensity every 10 mins (Unit in mm/hr)
# Address of slave: N/A

import time
import RPi.GPIO as GPIO
import urllib3
#from urllib.request import urlopen

BUTTON_PIN = 14   # Use GPIO 14 as a interrupt pin
rg_id_No = "8001" # Songde North: 8001

bucketNum = 0
timeIntval = 600  # Unit in second
bucketVal = 0.2  # Unit in mm
rfInts    = 0    # Unit in mm/hr
rfDep     = 0    # Unit in mm

rebootFlag = True

def my_callback(channel):
    global bucketNum
    bucketNum += 1
    print("Bucket dectected")
    print("Bucket Number: {}".format(bucketNum))
    #print("Time: {}".format(time.strftime("%Y%m%d%H%M%s")))
    print("------------------------------")
    time.sleep(0.1)

def httpPOST(String0, String1, String2, String3):    
    try:
        global timeStamp
        timeStamp = time.strftime("%Y%m%d%H%M%S")
        url = 'http://ec2-54-175-179-28.compute-1.amazonaws.com/update_general.php?' + \
              'site=Demo&' + \
              'time='+ str(timeStamp)+ \
              '&weather=0' + \
              '&id='+ str(String0) + \
              '&air=0' + \
              '&acceleration=0' + \
              '&cleavage=0' + \
              '&incline=0' + \
              '&field1='+str(String1)+ \
              '&field2='+str(String2)+ \
              '&field3='+repr(String3)
       
        url_TT ='http://data.thinktronltd.com/TCGEMSIS/GETMTDATA.aspx?' + \
              'site=Demo&' + \
              'time='+ str(timeStamp)+ \
              '&weather=0' + \
              '&id='+ str(String0) + \
              '&air=0' + \
              '&acceleration=0' + \
              '&cleavage=0' + \
              '&incline=0' + \
              '&field1='+str(String1)+ \
              '&field2='+str(String2)+ \
              '&field3='+repr(String3) 
        
        #resp = urlopen(url).read()
        #resp_TT = urlopen(url_TT).read()
	#print("URL: {}".format(url))
	
        http = urllib3.PoolManager()
        resp = http.request('POST', url)
        resp_TT = http.request('POST', url_TT)

        print("AWS Statue: {}".format(resp.status))
        print("TT  Statue: {}".format(resp_TT.status))
        print('------------------------')
    except:
        print('We have an error!')
        time.sleep(5) # Wait for 30 sec
        #resp = urlopen(url).read()
        #print(resp)
        http = urllib3.PoolManager()
        resp = http.request('POST', url)
        resp_TT = http.request('POST', url_TT)

        print("AWS Statue: {}".format(resp.status))
        print("TT  Statue: {}".format(resp_TT.status))
        print('------------------------')


GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING, callback = my_callback, bouncetime = 500)

startTime = time.time()
endTime   = time.time()

try:
    while rebootFlag:
        data1 = 0 
        data2 = 0
        httpPOST(rg_id_No, data1, data2, 'Reboot')
        rebootFlag = False

    while True:
      if ( endTime - startTime > timeIntval ):
        print("Send mesg.")
        rfDep  = bucketNum * bucketVal
        rfInts = rfDep/0.1666667 # Unit in mm/hr every 10 mins
        
        data1 = round(rfInts,3) 
        data2 = 0
        httpPOST(rg_id_No, data1, data2, 0)

        bucketNum = 0
        startTime = endTime
        time.sleep(0.1)

      endTime = time.time()
      # print("Time interval: {} ".format(endTime - startTime))
      time.sleep(0.5)
except KeyboardInterrupt:
    print("Shut down!")
finally:
    GPIO.cleanup()
