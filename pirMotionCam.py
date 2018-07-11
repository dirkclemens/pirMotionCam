#!/usr/bin/env python

'''
ideas taken from:
https://picamera.readthedocs.io/en/release-1.13/
https://projects.raspberrypi.org/en/projects/parent-detector/
https://github.com/jbeale1/PiCam1/blob/master/stest2.py
'''


import time
import datetime as dt
from picamera import PiCamera # sudo apt-get install python-picamera python3-picamera
from fractions import Fraction

debug		= True
#video resolutions		http://picamera.readthedocs.io/en/release-1.12/fov.html
cXRes 		= 1920   	# camera capture X resolution (video file res)
cYRes 		= 1080    	# camera capture Y resolution
cXRes 		= 1640   	# camera capture X resolution (video file res)
cYRes 		= 1232    	# camera capture Y resolution
BPS 		= 9000000  	# bits per second from H.264 video encoder
imageDir 	= '/media/still/'
imagePrefix = 'still_'
videoDir 	= '/media/video/'
videoPrefix = 'video_'

def log(message):
	if debug:
		print('%s %s') % (dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message)

def createFileDate():
	segTime = time.time()  # current time in seconds since Jan 1 1970
	segDate = time.strftime("%y%m%d_%H%M%S.%f", time.localtime(segTime))
	segDate = segDate[:-3] # loose the microseconds, leave milliseconds
	return segDate

# https://picamera.readthedocs.io/en/release-1.13/recipes1.html
def takeStill(withPush = False):
	log("take still")
	fDate = createFileDate()
	filename = ("%s%s%s.jpg") % (imageDir, imagePrefix, fDate )
	camera.resolution = (cXRes, cYRes)
	# camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	# camera.annotate_text_size = 50
	try:
		camera.start_preview()
		time.sleep(2)
		camera.capture(filename)
		camera.stop_preview()
		# if withPush:
			# pushoverImage("picture taken: ", filename)
		pass
	except Exception as e:
		logger.error(e)
		raise e	
	log("still photo taken")
	return filename


# https://picamera.readthedocs.io/en/release-1.13/recipes1.html#capturing-timelapse-sequences
def takeStillSeries(cnt):
	log("take still series")
	fDate = createFileDate()
	camera.resolution = (cXRes, cYRes)
	# camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	# camera.annotate_text_size = 50
	try:
		camera.start_preview()
		for i in range(cnt):
			time.sleep(2)
			filename = ("%s%s%s_%s.jpg") % (imageDir, imagePrefix, fDate, i )
			camera.capture(filename)
			log('%s taken' % (filename, ))
		camera.stop_preview()
		pass
	except Exception as e:
		logger.error(e)
		raise e
	log("series of stills taken")
	return filename ## the last one only
	
def cameraSettingsVideo():
	log("cameraSettingsVideo")
	camera.resolution 	= (cXRes, cYRes)
	camera.framerate	= 25 #30

	camera.shutter_speed = camera.exposure_speed
	camera.exposure_mode = 'off'
	return 

# to play video: omxplayer filename.h264
# https://picamera.readthedocs.io/en/release-1.13/recipes1.html#capturing-in-low-light
def takeVideo(duration):
	log("take video")
	fDate = createFileDate()
	filename = ("%s%s%s.h264") % (videoDir, videoPrefix, fDate )
	# cameraSettingsVideo()
	log("start_preview")
	try:
		camera.start_preview()
		# camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		# camera.annotate_text_size = 50
		log("start_recording")
		camera.start_recording(filename)
		# time.sleep(5)
		camera.wait_recording(duration) # same as sleep(5)
		log("stop_recording")
		camera.stop_recording()
		log("stop_preview")
		camera.stop_preview()
		pass
	except Exception as e:
		logging.error(e)
		raise e
	log("video taken")

# https://pushover.net/api
# https://pushover.net/faq#library-python
def pushover(message, image):
	import httplib, urllib			# python2
	import requests					    # apt-get install python-requests
	
	files = {'attachment': open(image, 'rb')   }
	r = requests.post("https://api.pushover.net:443/1/messages.json", data = {
		"token": "......",
		"user": "......",
		"message": message,
	}, files = files, verify=False)
	print(r.text)


import RPi.GPIO as GPIO
SENSOR_PIN = 23 
GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PIN, GPIO.IN)
 
def pirCallback(channel):
	try:
		image = takeStill()
		pushover("taking a picture ...", image)
		takeVideo(10)
		pass
	except Exception as e:
		log(e)
		raise e


import logging
logger=None

camera = PiCamera(resolution=(1640,1232), framerate=25)
# camera = PiCamera(resolution=(1280, 720), framerate=30)
# camera.rotation = 180
# camera.vflip =  True

def main():                
	logging.basicConfig(filename='./pirMotionCam.log')
	logger = logging.getLogger('pirMotionCam')
	logger.setLevel(logging.DEBUG)
	formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
	handler = logging.StreamHandler()
	handler.setFormatter(formatter)
	logger.addHandler(handler)

	logger.info("initialize camera ...")

	try:
		logger.info("starting ...")
		GPIO.add_event_detect(SENSOR_PIN , GPIO.RISING, callback=pirCallback)
		while True:
			time.sleep(100)
	except KeyboardInterrupt:
		logger.info("stopping caused by keybord interrupt...")
	GPIO.cleanup()

	# pushoverImage("picture taken: ", 'filename')

	#pushover("taking a picture ...")
	#takeStill(True)
	#takeVideo(3)
	#takeStillSeries(5)

	logger.info("camera.close()")
	camera.close()	

if __name__ == "__main__":
	main()


