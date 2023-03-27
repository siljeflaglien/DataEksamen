import sys 
import argparse
import re
from socket import *
import _thread as thread
import time
from sys import getsizeof


"""________________________________________________________________________________________________
                                         CUSTOM FUNCTIONS
    ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""
# CUSTOM FUNCTIONS that need to be defined before the arguments

#Checking Ip address inn in --bind and --serverip argument
def check_IP(val):
    #Checking that the string is in the right format
    value = re.match('^[0-9]{1,3}[.][0-9]{1,3}[.][0-9]{1,3}[.][0-9]{1,3}', val)
    if not value:
        print("Not a valid IP address. I nedd to be in the format of: \n X.X.X.X \n Where X is a number between 0-127.")
        sys.exit
    return val

#Checking port in --port argument
def check_port(val):
    #check if the port is a number.
    try:
        value = int(val)
    except ValueError:
        raise argparse.ArgumentTypeError('expected an integer but you entered a string')
        #if not a number, sends error.
    
    if (value<1024 or value>65535):
        print ("It is not a valid port")
        sys.exit
        #Only valid port between [1204-65535]. 

    return value

#Checking format in --format argument
def check_format(val):
    #Hvis det kommer inn i et Spesielt format, skal jeg konvertere det?
    print

#Checking seconds in --time argument
def check_time(val):
    if (val<=0):
        print('The time need to be greater than 0')
        sys.exit
    
    return val


def check_num_conn(val):
    try:
        value = int(val)
    except ValueError:
        raise argparse.ArgumentTypeError('expected an integer but you entered a string')
        #if not a number, sends error.
    
    if (value<1 or value >5):
        print('Number of connections needs to be between 1-5')
        sys.exit
    
    return value
        
"""________________________________________________________________________________________________
                                         HANDLE SERVER
    ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""
def handleServer(port, IP):
    serverSocket = socket(AF_INET, SOCK_STREAM) 
    serverPort = port
    datareceived=1000
    rate = 10

    try:
        #Binding socket to a IP adress and port
        serverSocket.bind((IP, serverPort)) 
    except:
        print("Bind failed. Error : ")
    
    #only one can connect
    serverSocket.listen(1) 
    print('Ready to receive... ')

    #sys.exit()

    while True:
        #Establish the connection print('Ready to serve...') connectionSocket, addr =
        try:
            connectionSocket, addr = serverSocket.accept() 
            print('Ready to serve ' , addr)
            print('A simpleperf client with IP address:' + str(addr) +' is connected with server IP: '+ str(serverPort))

        except IOError:
            #Send response message for file not found
            feil = "404 File Not Found"
            connectionSocket.send(feil.encode()) 
        
        #Close client socket
        #connectionSocket.close()
        #serverSocket.close()
        #sys.exit()#Terminate the program after sending the corresponding data
    


    #Printig out IP, Interval, Received and Rate table
    print()
    d = {str(IP)+":"+ str(port):["0.0 - 25.0", str(datareceived)+' Mbps' , str(rate)+' Mbps']}
    print ("{:<15} {:<12} {:<10} {:<10}".format('ID','Interval','Received','Rate'))
    for k, v in d.items():
        lang, perc, change = v
        print ("{:<15} {:<12} {:<10} {:<10}".format(k, lang, perc, change))
    print()
    #End of printing table
    serverSocket.close()
    sys.exit()#Terminate the program after sending the corresponding data

"""________________________________________________________________________________________________
                                         HANDLE CLIENT
    ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""
def handleClient(serverIP,port):
    socketClient = socket(AF_INET, SOCK_STREAM) #Creating socket for client
    clientPort = port
    host = serverIP

    #Making a data packet with 1000bytes
    data='0'*951 #the byte size will be 1000 bytes with 951
   
    print(str(getsizeof(data))+' bytes') #prints 1000 bytes
    #print(data)
    
    #Connecting to Server
    try:
        socketClient.connect((host,clientPort))

    except:
        #If not able to connect, exit system.
        print ("Connection error")
        sys.exit()

    #Printing confirmation to a connected server.
    print('Client connected with '+str(host)+' port '+str(clientPort))

    #Taking the time, and sending data for the specified amout of time 
    t= time.time()
    while (time.time() < t+5):
        socketClient.send(data.encode())
    print('5 sekunder har gått')

    print('Avslutter...')
    socketClient.close()
    exit(1)





"""________________________________________________________________________________________________
                                         ADDING ARGUMENTS
    ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""

parser=argparse.ArgumentParser(description="Portifolio 1", epilog="end of help")


# ----------------------- Server --------------------------
parser.add_argument('-s', '--server', action='store_true') 
parser.add_argument('-b','--bind',type=check_IP, default='127.0.0.1') #input IP address



# ----------------------- Client --------------------------
parser.add_argument('-c', '--client', action='store_true')
parser.add_argument('-I','--serverip',type=check_IP, default='127.0.0.1') #input IP address
parser.add_argument('-t', '--time',type=check_time, default=25)
parser.add_argument('-i','--interval',type=int)
parser.add_argument('-p','--parallel',type=check_num_conn, default=1)
parser.add_argument('-n','--num',type=str, choices=('B','KB','MB'), default='MB')


# ------------------------ Both ---------------------------
parser.add_argument('-P','--port',type=check_port, default=8088) #input Port number
parser.add_argument('-f','--format', type=str, choices=('B','KB','MB'), default='MB')



"""________________________________________________________________________________________________
                                         HANDLE THE ARGUMENTS
    ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""
args = parser.parse_args()


    

#If -s and -c is not specified
if (not args.server and not args.client):
    print('Error: you must run either in server or client mode')
    sys.exit

#If both -c and -s is specified
elif (args.server and args.client):
    print('Error: you can only run server OR client, not both.')
    sys.exit

elif args.server:
    print('------------------------------------------------------------------------------------------')
    print('A simpleperf server is listening on port '+ str(args.port))
    print('------------------------------------------------------------------------------------------')

    print('bind: '+str(args.bind))
    print('port: '+str(args.port))
    handleServer(args.port,args.bind)
    
elif args.client:
    print('------------------------------------------------------------------------------------------')
    print('A simpleperf client connecting to server '+str(args.serverip)+', port '+str(args.port))
    print('------------------------------------------------------------------------------------------')
    handleClient(args.serverip,args.port)

sys.exit
