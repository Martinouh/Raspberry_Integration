import socket
import mysql.connector
from ast import literal_eval as make_tuple

#Connection to DB
conn = mysql.connector.connect(host="localhost",user="rcharlier",password="qe9hm2kx",database="db7")
cursor = conn.cursor()

#Socket listen localhost:8080
hote = ''
port = 8080

#Init Socket
Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
Socket.bind((hote,port))
Socket.listen(5)
client, address = Socket.accept()

while True:
	#Receive data from client
	data = client.recv(255)
	if data != '':
		#Client connect
		if data == "connect":
			print 'client connected'
			data = ''
		else:
			#Convert string to object
			data = make_tuple(data)
			print data
			#Update DB
        		print 'MAJ du compteur -> compteur : ',data
			cursor.execute("UPDATE professionnels SET nbre_pers = %s WHERE numSerie = %s",(data[0],data[1]))
			conn.commit()
			data = ''

print 'close'
#Close socket
client.close()
Socket.close()
#Close connexion
conn.close()
