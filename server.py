import socket
import mysql.connector
from ast import literal_eval as make_tuple

conn = mysql.connector.connect(host="localhost",user="rcharlier",password="qe9hm2kx",database="db7")
cursor = conn.cursor()

hote = ''
port = 8080

Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
Socket.bind((hote,port))
Socket.listen(5)
client, address = Socket.accept()

while True:
	data = client.recv(255)
	if data != '':
		if data == "connect":
			print 'client connected'
			data = ''
		else:
			data = make_tuple(data)
			print data
			#Connect DB && MAJ du compteur
        		print 'MAJ du compteur -> compteur : ',data
			cursor.execute("UPDATE professionnels SET nbre_pers = %s WHERE numSerie = %s",(data[0],data[1]))
			conn.commit()
			data = ''

print 'close'
client.close()
Socket.close()
conn.close()
