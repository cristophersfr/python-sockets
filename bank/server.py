'''
Created on Jun 3, 2015

    Simple socket server using threads

@author: cristopher
'''

import socket
import sys
from thread import *
from bank.manager import Manager

HOST = 'localhost'
PORT = 8888
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created.'

manager = Manager()
manager.load()
manager.listClients()
print 'Bank connected.'


#Bind socket to local host ande port
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

print 'Socket bind complete'

#Function for handling connections. This will be used to create threads
def clientThread(conn):
    #Sending message to connected client
    conn.send('Welcome to the bank server. Type your account ID\n') #send only takes string

    #infinite loop so that function do not terminate and thread do not end.
    while True:
        #Listen to the operations from the user
        #Receiving from client
        data = conn.recv(1024)

        if not data or data is '.':
            conn.send('Quiting...\n')
            break

        #Getting client by ID
        client = manager.lookForClientByID(int(data))

        print client

        if client is None:
            conn.send('ID invalid.\n')
            continue
        else:
            info = client.toDict()
            #Responding the connection
            conn.send('Welcome: ' + info['name'] + '\n')
            break

    #Infinite loop to capture client operations.
    while client is not None:
        data = conn.recv(1024)

        if 'PUT' == data[0:3]:
            id = int(data[4:8])
            value = int(data[9:])
            if client.id == id:
                client.deposit(value)
            else:
                client.transfer(manager.lookForClientByID(id), value)
            conn.send('OK\n')

        elif 'TAKE' in data[0:4]:
            value = int(data[5:])
            v = client.withdraw(value)
            conn.send(str(v) + '\n')

        elif data == '.':
            conn.send('Quiting... \n')
            break

        else:
            #TODO: Define invalid operations protocols.
            conn.send('Invalid operation\n')
            continue

    #came out of loop
    conn.close()

#Start listening on socket
s.listen(10)
print 'Socket now listening'

#now keep talking with the client
while 1:
    #wait to accept a connection - blocking call
    conn, addr = s.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])

    #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    start_new_thread(clientThread ,(conn,))

s.close()