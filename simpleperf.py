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
    return val #Returning the val that was in the right format, so that it can be used

#Checking port in --port argument
def check_port(val):
    #check if the port is a number.
    print('Val: '+ val)
    try:
        value = int(val)
    except ValueError:
        raise argparse.ArgumentTypeError('expected an integer but you entered a string')
        #if not a number, sends error.
    
    if (value<1024 or value>65535):
        print ("It is not a valid port")
        sys.exit
        #Only valid port between [1204-65535]. 
    
    print('Port Value: '+str(value))

    return value #Returning the vallue because it was valid and so that it can be used

#Checking format in --format argument
def check_format(val, format):
    #Hvis det kommer inn i et Spesielt format, skal jeg konvertere det?
    if val == 0 or format == 'B':
        return val
    elif format == 'MB':
        return val/1000000
    elif format == 'KB':
        return val/1000


#Checking seconds in --time argument
def check_time(val):
    try:
        value = int(val)
    except ValueError:
        raise argparse.ArgumentTypeError('expected an integer but you entered a string')
        #if not a number, sends error.

    if (value<=0):
        print('The time need to be greater than 0')
        sys.exit
    
    return value #return the time because til was positive, and so that it can be used


def check_num_conn(val):
    try:
        value = int(val)
    except ValueError:
        raise argparse.ArgumentTypeError('expected an integer but you entered a string')
        #if not a number, sends error.
    
    if (value<1 or value >5):
        print('Number of connections needs to be between 1-5')
        sys.exit
    
    return value #returns value beacuse it was valid and so that it can be used. 
        

def print_table(ID, from_time , to_time, lastsize, sizesent, lasttime, nowtime,format):
    
    #Size of the interval
    size=sizesent-lastsize #how much sent in the past interval
    transferformat=check_format(size,format) #Changing the format

    #time of the interval
    interval_time = nowtime-lasttime #How much time has past, need for calculating bandwidth

    #Bandwidth of the interval
    sizeMB = check_format(size,'MB') # changing into MB to calculate bandwidth
    bandwidth=float(sizeMB)/float(interval_time) # Bandwidth
   
    #sets them to only 2 decimals
    bandwidth = '{0:.2f}'.format(bandwidth)
    transferformat = '{0:.2f}'.format(transferformat)

    #Printing out a new row in the table
    d = {ID:[str(from_time)+".0 - "+str(to_time)+'.0', str(transferformat)+' '+format , str(bandwidth)+' Mbps']}
    for k, v in d.items():
        lang, perc, change = v
        print ("{:<15} {:<12} {:<17} {:<10}".format(k, lang, perc, change))
    print()
    

"""________________________________________________________________________________________________
                                         HANDLE SERVER
    ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""
def handleServer(port, IP, format):
    serverSocket = socket(AF_INET, SOCK_STREAM) 
    serverPort = port #port number of the server
    datareceived=0  #will get updated each time i receive data
    rate = 0 #just declaring it

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
        try:
            connectionSocket, addr = serverSocket.accept() #Establish the connection
            print('Ready to serve ' , addr) #connected and ready
            print('A simpleperf client with IP address:' + str(addr) +' is connected with server IP: '+ str(serverPort))
            
            start = time.time() #Start time
            end = 0 #declaring the variable
            rectime = 0

            while True:
                message = connectionSocket.recv(1100).decode() #recieving the packets
                print('Message: '+message+ '\n\n')
                #If messange is BYE, connection is closing and we send back a BYE ACK
                if(message == 'BYE'): 
                    print('got BYE')
                    rectime = connectionSocket.recv(1100).decode() #recieving the packets
                    rectime= int(rectime)
                    print("RECEIVED TIME: "+ str(rectime))
                    bye = 'BYE ACK'
                    connectionSocket.send(bye.encode())
                    #Close client socket
                    connectionSocket.close()
                    
                    #end = seconds passed until receiving BYE
                    end = time.time() - start
                    break
                    
                else:
                    #If not BYE, we add it to how much data we have received
                    datareceived+=getsizeof(message)
            
             # ----------------------- PRINTING RESULTS ----------------------------
            receivedMB = check_format(datareceived, 'MB') # from B -> MB
            print('received B: '+str(datareceived))
            print('received MB: '+str(receivedMB))
            print('end: '+str(end))
            rate = receivedMB/end #calculating the rate

            transferformat=check_format(datareceived,format) #Changing to the chosen format from --format

            #sets them to only 2 decimals
            rate = '{0:.2f}'.format(rate)
            transferformat = '{0:.2f}'.format(transferformat)
           
            #Printig out "IP, Interval, Received and Rate" table
            print()
            d = {str(IP)+":"+ str(port):["0.0 - "+str(rectime)+'.0', str(transferformat)+' '+format , str(rate)+' Mbps']}
            print ("{:<15} {:<12} {:<17} {:<10}".format('ID','Interval','Received','Rate'))
            for k, v in d.items():
                lang, perc, change = v
                print ("{:<15} {:<12} {:<17} {:<10}".format(k, lang, perc, change))
            print()
            #End of printing table

        except IOError:
            #Send response message for file not found
            feil = "404 File Not Found"
            connectionSocket.send(feil.encode()) 
        
        #Closes socket, bye message has been receieved 
        serverSocket.close()
        sys.exit()#Terminate the program after sending the corresponding data
    


"""________________________________________________________________________________________________
                                         HANDLE CLIENT
    ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""
def handleClient(serverIP,port, sendtime, format, interval):
    socketClient = socket(AF_INET, SOCK_STREAM) #Creating socket for client
    clientPort = port #Port number of the server
    host = serverIP #IP address of the server
    bye = 'BYE' #for when we send the bye message
    sizesent=0 #sizesent

    #Making a data packet with 1000bytes
    data='0'*1000 #the byte size will be 1000 bytes with 951
   
    print(str(getsizeof(data))+' bytes') #prints 1000 bytes (how many bytes the data packet is)
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

    #Printing header for interval printing. --interval
    

    #Marking the time (it is in seconds)
    t= time.time()

    #If --interval not is specified
    if interval is None:
        #Sending data normal
        while (time.time() < t+sendtime): #sending it for "sendtime"-amount of seonds
            socketClient.send(data.encode()) #Sending the data to the server
            sizesent+=getsizeof(data)
        
    #If --interval is specified with seconds
    else:
        #Printing out the header row
        print('\n')
        print ("{:<15} {:<12} {:<17} {:<10}".format('ID','Interval','Transfer','Bandwith'))

        #Variables used i printing results in case of --interval
        from_time=0 #starting the intervals
        to_time=interval #how long the interval lasted
        ID=str(serverIP)+":"+ str(port) #ID used in the table
        lasttime=t #What time the last interval ended at
        lastsize=0 #How many bytes was sent in total last interval

        #A while who sends data and sends prints results at the right interval
        while (time.time() < t+sendtime): #sending it for "sendtime"-amount of seonds

            socketClient.send(data.encode()) #Sending the data to the server
            sizesent+=getsizeof(data) #adding to bytes sent

            #If it has n seconds (interval) then we print out the results
            if(time.time()>=t+to_time):
                #Method that print one and one row of data results
                print_table(ID,from_time,to_time,lastsize,sizesent,lasttime,time.time(),format)
                
                #Updating variables used in print table
                to_time+=interval #from what seconds the interval begins 2.0 - 4.0, this is 2.0
                from_time+=interval #this was 2.0, but got now updated to 4.0 (if interval is 2 seconds)
                lasttime=time.time()
                lastsize=sizesent
        
        
    end=time.time() #time finished sending packets

    print('---------------------------------------------------------------------------')
    sendtime=str(sendtime) #changing the seconds to a String to make it easier further down
    print(sendtime+' seconds has passed')
    
    time.sleep(0.3) #To separate BYE and datapackets so they dont get sendt in the same message

    socketClient.send(bye.encode()) #Sends BYE message
    #print('Sendt bye')
    socketClient.send(sendtime.encode()) #Sends timeinterval, seconds packets got sendt.
    message = socketClient.recv(1024).decode() #Recieving ACK message.

    if(message == 'BYE ACK'):
        print('Exits...')

        #Closing and exiing 
        socketClient.close() 
    

    # --------------------------------------- PRINTING RESULTS --------------------------------------------------
    #Calculating bandwidth
    totaltduration=end-t #gives totalt duration of sending
    sizeMB=check_format(sizesent,'MB') #Gives the size sent in MB instead of B
    bandwidth=sizeMB/totaltduration #The bandwith calculated in Mbps
    #print('Sizesendt: '+ str(sizesent)+' B\nSize MB: '+str(sizeMB)+' MB') # REMOVE

    transferformat=check_format(sizesent,format) #Changing to the chosen format from --format
    #print('Sizesendt: '+ str(sizesent)+' B\nSize MB: '+str(sizeMB)+' MB\nSize KB: '+str(transferformat)) #REMOVE

    #sets them to only 2 decimals
    bandwidth = '{0:.2f}'.format(bandwidth)
    transferformat = '{0:.2f}'.format(transferformat)

    #Printig out "IP, Interval, Transfer and Bandwisth" table
    print()
    d = {str(serverIP)+":"+ str(port):["0.0 - "+str(sendtime)+'.0', str(transferformat)+' '+format , str(bandwidth)+' Mbps']}
    print ("{:<15} {:<12} {:<17} {:<10}".format('ID','Interval','Transfer','Bandwith'))
    for k, v in d.items():
        lang, perc, change = v
        print ("{:<15} {:<12} {:<17} {:<10}".format(k, lang, perc, change))
    print()
    #End of printing table

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
parser.add_argument('-P','--parallel',type=check_num_conn, default=1)
parser.add_argument('-n','--num',type=str, choices=('B','KB','MB'), default='MB')


# ------------------------ Both ---------------------------
parser.add_argument('-p','--port',type=check_port, default=8088) #input Port number
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
    handleServer(args.port,args.bind,args.format)
    
elif args.client:
    print('------------------------------------------------------------------------------------------')
    print('A simpleperf client connecting to server '+str(args.serverip)+', port '+str(args.port))
    print('------------------------------------------------------------------------------------------')
    handleClient(args.serverip,args.port, int(args.time), args.format, args.interval)

sys.exit
