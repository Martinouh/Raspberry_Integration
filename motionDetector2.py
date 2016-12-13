from picamera.array import PiRGBArray
from picamera import PiCamera
import imutils
import time
import cv2
import os
import socket

#Init camera
camera = PiCamera()
camera.resolution = (1280,720)
camera.framerate = 20
rawCapture = PiRGBArray(camera,size=(1280,720))

#Init the counter
counter = 0
#Init the two part of the frame
IN = 0
OUT = 0
#Object detected
object = False

#TCP connection to server
hote = 'vps321502.ovh.net'
port = 8080
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((hote,port))
s.send('connect')

#Get serial of the Raspberry Pi
f=open('/proc/cpuinfo','r')
for line in f:
	if line[0:6]=='Serial':
		serial = line[10:26]
f.close()

#Let the camera started
print "Start Camera"
time.sleep(1)
#Init the average
avg = None

print "Start Process"
for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	#Get frame
	frame = f.array
	#Resize frame
	frame = imutils.resize(frame,width=1000)

	#Get size of the frame
	H,W,C = frame.shape
	
	#Draw limit line between the two part of the frame
	cv2.line(frame,(0,(H/2)),(W,(H/2)),(255,255,0),2)

	#Convert color frame to gray frame
	gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
	#Apply Gaussian filter to remove paper&salte
	gray = cv2.GaussianBlur(gray, (21,21), 0)

	#If first frame
	if avg is None:
		#Add frame to average, empty buffer, and get next frame
		avg = gray.copy().astype("float")
		rawCapture.truncate(0)
		continue

	#Add frame to average
	cv2.accumulateWeighted(gray, avg, 0.5)
	#Get the differences between average and frame
	frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
	#Apply thresholding to the frame display object detected
	thresh = cv2.threshold(frameDelta,5,255,cv2.THRESH_BINARY)[1]
	#Dilate the frame to reconnect object cut by thresholding
	thresh = cv2.dilate(thresh,None,iterations=2)
	#Put all contours of all object in a table
	_,contours,_ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	#Help to know when object leave the frame
	passed = False

	for c in contours:
		#If object too small -> do nothing
		if cv2.contourArea(c) > 10000:
			
			passed = True
			#New object detected
			if object is False:
				object = True

			#Get size of object
			x,y,w,h = cv2.boundingRect(c)
			#Get the centroide position of object
			x1=w/2
			y1=h/2
			cx=x+x1
			cy=y+y1
			#Draw centroïde on the frame
			cv2.circle(frame,(int(cx),int(cy)),3,(0,255,255),-1)
	
			#If object is detected in the first part of the frame
			if (int(cy) < (H/2)):
				#Draw rectangle around it
				cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
				IN = 1
				OUT = 0
			#If object is detected in the last part of the frame
			if (int(cy) > (H-(H/2))):
				cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
				OUT = 1
				IN = 0

	#If object leave the frame
	if (object) and (passed is False):
		object = False
		
		#Last position of object was in the first part of the frame
		if (IN==1):
			#If counter = 0 -> do nothing
			if (counter > 0):
				#Decrease counter
				counter = counter - 1
				packet = (counter,serial)
				#Send serial and counter to server
				s.send(str(packet))
		#Last position of object was in the last part of the frame
		else:
			#Increase counter
			counter = counter + 1
			packet = (counter,serial)
			#Send serial and counter to server
			s.send(str(packet))
	
	#Edit counter field on frame
	counterTxt = 'counter : '+str(counter)
	#Write counter on frame
	cv2.putText(frame, counterTxt, (10,100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
		
	#Display frame, frameDelta and thresholding
	#cv2.imshow('frame',frame)
	#cv2.imshow('frameDelta',frameDelta)
	#cv2.imshow('thresh',thresh)
	
	#Press 'q' to stop process
	key = cv2.waitKey(1) & 0xFF
	if key == ord('q'):
		break

	#empty buffer and get next frame
	rawCapture.truncate(0)	
#Delete all windows displayed
cv2.destroyAllWindows()
#Close connection to server
s.close()
