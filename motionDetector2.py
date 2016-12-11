from picamera.array import PiRGBArray
from picamera import PiCamera
import imutils
import time
import cv2
import os
import socket

camera = PiCamera()
camera.resolution = (1280,720)
camera.framerate = 20
rawCapture = PiRGBArray(camera,size=(1280,720))

counter = 0
IN = 0
OUT = 0
object = False

hote = 'vps321502.ovh.net'
port = 8080
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((hote,port))
s.send('connect')

f=open('/proc/cpuinfo','r')
for line in f:
	if line[0:6]=='Serial':
		serial = line[10:26]
f.close()

print "Start Camera"
time.sleep(1)
avg = None

print "Start Process"
for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	
	frame = f.array
	frame = imutils.resize(frame,width=1000)

	H,W,C = frame.shape
	
	cv2.line(frame,(0,(H/2)),(W,(H/2)),(255,255,0),2)

	gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21,21), 0)

	if avg is None:
		avg = gray.copy().astype("float")
		rawCapture.truncate(0)
		continue

	cv2.accumulateWeighted(gray, avg, 0.5)
	frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
	thresh = cv2.threshold(frameDelta,5,255,cv2.THRESH_BINARY)[1]
	thresh = cv2.dilate(thresh,None,iterations=2)
	_,contours,_ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	passed = False

	for c in contours:
		
		if cv2.contourArea(c) > 10000:
			
			passed = True

			if object is False:
				object = True

			x,y,w,h = cv2.boundingRect(c)
			#Centroide
			x1=w/2
			y1=h/2
			cx=x+x1
			cy=y+y1
			cv2.circle(frame,(int(cx),int(cy)),3,(0,255,255),-1)
	
			#1e rectangle
			if (int(cy) < (H/2)):
				cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
				IN = 1
				OUT = 0
			#2e rectangle
			if (int(cy) > (H-(H/2))):
				cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
				OUT = 1
				IN = 0

	if (object) and (passed is False):
		object = False
		
		if (IN==1):
			if (counter > 0):
				counter = counter - 1
				packet = (counter,serial)
				s.send(str(packet))
		else:
			counter = counter + 1
			packet = (counter,serial)
			s.send(str(packet))
	
	counterTxt = 'counter : '+str(counter)
	cv2.putText(frame, counterTxt, (10,100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
		
	
	#cv2.imshow('frame',frame)
	#cv2.imshow('frameDelta',frameDelta)
	#cv2.imshow('thresh',thresh)
	key = cv2.waitKey(1) & 0xFF
	if key == ord('q'):
		break

	rawCapture.truncate(0)	

cv2.destroyAllWindows()
s.close()
