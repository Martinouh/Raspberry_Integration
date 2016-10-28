#Bibliothèque permettantr d'utiliser plus facilement la caméra du RPI
from picamera.array import PiRGBArray
from picamera import PiCamera
#Permet de redimensionner l'image
import imutils
import time
#Open CV Python - Bibliothèque permettant le traitement d'images
import cv2

#Préparer la caméra
camera = PiCamera()
camera.resolution = (1280,720)
camera.framerate = 25
#Permet d'obtenir un tableau RGB Ã 3 dimensions (ligne, colonne, couleurs) sur base d'une image RGB 
rawCapture = PiRGBArray(camera,size=(1280,720))

#Laisser le temps à la caméra de démarrer
print "Start camera .."
time.sleep(2)
#Initialisation de la moyenne des frames analysées
avg = None

#Démarrage de la détection
print "Start motion detection"
for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	#On récupère une frame
	frame = f.array
	#On la redimentionne par soucie d'affichage 
	frame = imutils.resize(frame,width=500)
	#On convertie la frame couleur en noir & blanc 
	gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
	#On enlève les parasites (poivre & sel)
	gray = cv2.GaussianBlur(gray, (21,21), 0)

	#Si première frame analysée
	if avg is None:
		#On copie la frame, on vide le buffer et on recommence l'itération
		avg = gray.copy().astype("float")
		rawCapture.truncate(0)
		continue

	#On calcul les différences entre la moyenne des frames déjà nalysées et la frame actuelle
	cv2.accumulateWeighted(gray, avg, 0.5)
	frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
	#On binarise le résultat (avec un faible seuil !)
	thresh = cv2.threshold(frameDelta,5,255,cv2.THRESH_BINARY)[1]
	#On dilate la frame au cas ou un objet aurait été coupé en plusieurs morceaux lors de la binarisation
	thresh = cv2.dilate(thresh,None,iterations=2)
	#On récupère les coutours des objets dans un tableau
	contours,_ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	#On parcours le tableau de contours
	for c in contours:
		#Si la surface de l'objet est trop petite il n'est pas détecté
		if cv2.contourArea(c) < 3000:
			continue
		#Si la surface de l'objet est suffisament grande, on récupère les coordonnés et on déssine un rectangle autour
		(x,y,w,h) = cv2.boundingRect(c)
		cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
		#alternative à cv2.rectangle()
		#cv2.drawContours(frame,contours,-1,(0,255,0),2)

	#Pour plus tard ..
		#h,w,c = frame.shape
		#cv2.rectangle(frame,(0,0),(50,h),(0,0,255),2)
		#cv2.rectangle(frame,(w-50,0),(w,h),(0,0,255),2)

	#On affiche le résultat
	cv2.imshow('frame',frame)
	#décommenter pour afficher la frame delta et la binarisation (les 2 lignes en dessous) 
	#cv2.imshow('frameDelta',frameDelta)
	#cv2.imshow('thresh',thresh)

	#quitte le programme si on click sur 'q'
	key = cv2.waitKey(1) & 0xFF
	if key == ord('q'):
		break

	#On vide le buffer pour la prochaine frame
	rawCapture.truncate(0)	
