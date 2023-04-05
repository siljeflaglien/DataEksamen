import sys 
import argparse
import re
from socket import *
import _thread as thread
import threading
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
    #print('Val: '+ val) #REMOVE
    try:
        value = int(val)
    except ValueError:
        raise argparse.ArgumentTypeError('expected an integer but you entered a string')
        #if not a number, sends error.
    
    if (value<1024 or value>65535):
        print ("It is not a valid port")
        sys.exit
        #Only valid port between [1204-65535]. 
    
    #print('Port Value: '+str(value)) #REMOVE

    return value #Returning the vallue because it was valid and so that it can be used

#Checking format in --format argument
def check_format(val, format):
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

#Checking number og connections in --parallel
def check_num_conn(val):
    try:
        value = int(val)
    except ValueError:
        raise argparse.ArgumentTypeError('expected an integer but you entered a string')
        #if not a number, sends error.
    
    if (value<1 or value >5):
        print('Number of connections needs to be between 1-5')
        sys.exit
        exit(1)
    
    return value #returns value beacuse it was valid and so that it can be used. 

def check_num(val):
    #print('inne i check num') #REMOVE
    size=len(val) #Size of the string writen in
    #print('Size: '+str(size)) #REMOVE
    format = val[size-2]+val[size-1]

    #Geeting the numbers out of 
    number=""
    for i in range(size-2): 
        number+=val[i]
    
    print('Number: '+number)
    
    try:
        number=int(number)
    except ValueError:
        raise argparse.ArgumentTypeError('You did not only get numbers from the string --num')
        #if not a number, sends error.

    format = format*8 #From Byte to Bit
    if(format=='KB'):
        number=number*1000
    elif(format=='MB'):
        number=number*1000000

    print('Value inne i check_num: '+str(number))
    return number

#Printing one and one row of results in --interval
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
               
                message = connectionSocket.recv(1000).decode() #recieving the packets
                
            
                #If messange is BYE, connection is closing and we send back a BYE ACK
                if "BYE" in message: 
                    #end = seconds passed until receiving BYE
                    end = time.time() - start

                    #If endtime is less than 1, it get set to 1
                    if end<1:
                        end=1
                
                    #recieving --time the data sent, so that i can have the right interval in the results #REMOVE
                    #rectime = connectionSocket.recv(1100).decode()  #REMOVE
                    
                    #Sending ack message
                    bye = 'BYE:ACK' #Making the ack message
                    connectionSocket.send(bye.encode()) #Sending the ack

                    #Closing the client socket
                    connectionSocket.close()
                    
                    
                    
                    break
                    
                else:
                    #If not BYE, we got a normal package and add the bytes to how much data we have received
                    datareceived+=getsizeof(message)
            

             # ----------------------- PRINTING RESULTS ----------------------------
            
            receivedMB = check_format(datareceived, 'MB') # from B -> MB
            #print('received B: '+str(datareceived)) #Data received in B
            #print('received MB: '+str(receivedMB)) #Data received in MB
            rate = receivedMB/end #calculating the rate in MBps
            rate = rate*8 # in mega bite per second


            transferformat=check_format(datareceived,format) #Changing to the chosen format from --format
    
            #sets them to only 2 decimals
            rate = '{0:.2f}'.format(rate)
            transferformat = '{0:.2f}'.format(transferformat)

            end=int(end) #Making it to an integer without deciamls
           
            #Printig out "IP, Interval, Received and Rate" table
            print()
            d = {str(IP)+":"+ str(port):["0.0 - "+str(end)+'.0', str(transferformat)+' '+format , str(rate)+' Mbps']}
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
def handleClient(serverIP,port, sendtime, format, interval, num):
    socketClient = socket(AF_INET, SOCK_STREAM) #Creating socket for client
    clientPort = port #Port number of the server
    host = serverIP #IP address of the server
    bye = "BYE" #for when we send the bye message
    sizesent=0 #sizesent
    sendtime=str(sendtime) #changing the seconds to a String to make it easier further down

    #Making a data packet with 1000bytes
    data='0'*1000 #the byte size will be 1000 bytes with 951
    datasize=getsizeof(data)
    #print(str(getsizeof(data))+' bytes') #prints 1000 bytes (how many bytes the data packet is) #REMOVE
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
    if interval is None and num is None:
        #Sending data normal
        while(time.time() < t+int(sendtime)): #sending it for "sendtime"-amount of seonds
            socketClient.send(data.encode()) #Sending the data to the server
            sizesent+=getsizeof(data)

       
        print(sendtime+' seconds has passed')
        
    #If num is specified with how many bytes to send over. 
    elif num is not None:
        print('Sending wiht --num')
        while (sizesent+datasize <= num): #sending it for "sendtime"-amount of seonds
            socketClient.send(data.encode()) #Sending the data to the server
            sizesent+=datasize
    
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
        while (time.time() < int(t)+int(sendtime)): #sending it for "sendtime"-amount of seonds

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
        
       
        print(sendtime+' seconds has passed')
        print('---------------------------------------------------------------------------')

        
    end=time.time() #time finished sending packets

    
    
    
    #time.sleep(0.3) #To separate BYE and datapackets so they dont get sendt in the same message #REMOVE
  
    socketClient.send(bye.encode()) #Sends BYE message
    
    #time.sleep(0.3) #To separate BYE and the next message so they dont get sendt in the same message
    #socketClient.send(sendtime.encode()) #Sends timeinterval, seconds packets got sendt.

    message = socketClient.recv(1024).decode() #Recieving ACK message.
    if('BYE:ACK' in message):
        print('Exits...')

        #Closing and exiing 
        socketClient.close() 
    

    # --------------------------------------- PRINTING RESULTS --------------------------------------------------
    #Calculating bandwidth
    totaltduration=end-t #gives totalt duration of sending
    sizeMB=check_format(sizesent,'MB') #Gives the size sent in MB instead of B
    bandwidth=sizeMB/totaltduration #The bandwith calculated in MBps
    bandwidth=bandwidth*8 #The bandwidth in mega bite per second
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
                                            THREAD
    ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""

#Each thread will do this function.
def handle_thread_server(connectionSocket, addr, IP, port,format):
    while True:
        try:
            #print('Prøver med connection: '+str(addr)) #REMOVE
            start = time.time() #Start time
            end = 0 #declaring the variable
            datareceived=0

            while True:
               
                message = connectionSocket.recv(1100).decode() #recieving the packets
                #print('Message: '+message+ '\n\n') #Printing messages/Packets got
                
                #If messange is BYE, connection is closing and we send back a BYE ACK
                if('BYE' in message):  
                    
                    #Sending ack message
                    bye = 'BYE:ACK' #Making the ack message
                    connectionSocket.send(bye.encode()) #Sending the ack

                    #Closing the client socket
                    connectionSocket.close()
                    
                    #end = seconds passed until receiving BYE
                    end = time.time() - start
                    break
                    
                else:
                    #If not BYE, we got a normal package and add the bytes to how much data we have received
                    datareceived+=getsizeof(message)
                    #print( 'Message: '+message+'\n\n') #REMOVE
            

             # ----------------------- PRINTING RESULTS ----------------------------
            
            receivedMB = check_format(datareceived, 'MB') # from B -> MB
            #print('received B: '+str(datareceived)) #Data received in B #REMOVE
            #print('received MB: '+str(receivedMB)) #Data received in MB #REMOVE
            #print('end: '+str(end)) #Printing End time, how long it used #REMOVE
            rate = receivedMB/end #calculating the rate in mega byte per second
            rate = rate*8 #The rate in mega bite per second 

            transferformat=check_format(datareceived,format) #Changing to the chosen format from --format
            
            #Making them into whole integers
            transferformat=int(transferformat)
            end=int(end)

            #sets them to only 2 decimals
            rate = '{0:.2f}'.format(rate)
            transferformat = '{0:.2f}'.format(transferformat)
            
            #Printig out "IP, Interval, Received and Rate" table
            print()
            d = {str(IP)+":"+ str(port):["0.0 - "+str(end)+'.0', str(transferformat)+' '+format , str(rate)+' Mbps']}
            print ("{:<15} {:<12} {:<17} {:<10}".format('ID','Interval','Received','Rate'))
            for k, v in d.items():
                lang, perc, change = v
                print ("{:<15} {:<12} {:<17} {:<10}".format(k, lang, perc, change))
            print()
            #End of printing table

        except IOError:
            #If the sockets listened to more connections, but no connections came, it goes in this except
            sys.exit()# And we terminate the listening for this connection. 


#------------------------------------------------------------------------------------------------


#Making a server that accepts multiple threads
def thread_server(serverIP, serverPort,format):
    #IP address of the server and port get sent in
    
    #Setting up TCP connection
    serverSocket = socket(AF_INET, SOCK_STREAM) 
     

    try:
        #Binder socket til en spesifikk IP-adresse og Port
        serverSocket.bind((serverIP, serverPort)) 
    except:
        print("Bind failed. Error : ")

    serverSocket.listen(5) 
    print('\nSocket is listening and ready to receive\n')
    print('------------------------------------------------------------------------------------------')
   

    conn=1
    while True:
        #print('Prøver på connection nr: '+str(conn))
        print()
        conn+=1
        #Establish the connection print('Ready to serve...') connectionSocket, addr =
        connectionSocket, addr = serverSocket.accept() #Establish the connection
        print('A simpleperf client with IP address:' + str(addr) +' is connected with server IP: '+ str(serverPort))#connected and ready

        thread.start_new_thread(handle_thread_server, (connectionSocket, addr,serverIP,serverPort,format))
    
    
    
def handle_thread_client(serverIP, port, sendtime, format):

    #print('Kobler til neste thread!') #REMOVE
    
    socketClient = socket(AF_INET, SOCK_STREAM) #Creating socket for client
    clientPort = port #Port number of the server
    host = serverIP #IP address of the server
    bye = 'BYE' #for when we send the bye message
    sizesent=0 #sizesent
    sendtime=str(sendtime) #changing the seconds to a String to make it easier further down

    #Making a data packet with 1000bytes
    data='0'*1000 #the byte size will be 1000 bytes with 951
    datasize=getsizeof(data)
    #print(str(getsizeof(data))+' bytes') #prints 1000 bytes (how many bytes the data packet is) #REMOVE
    #print(data)

    #Connecting to Server
    try:
        socketClient.connect((host,clientPort))
    except:
        #If not able to connect, exit system.
        print ("Connection error")
        sys.exit()

    #print('Client'+' : '+str(serverIP)+":"+ str(port)+' connected with '+str(serverIP)+' port '+str(port)) #REMOVE?
    
    #Marking the time (it is in seconds)
    t= time.time()

    #print('Starter whilen') #REMOVE
    #A while who sends data
    while (time.time() < t+int(sendtime)): #sending it for "sendtime"-amount of seonds
        #print('Inne i whilen')
        socketClient.send(data.encode()) #Sending the data to the server
        sizesent+=getsizeof(data) #adding to bytes sent


    
    #print(sendtime+' seconds has passed') #REMOVE
    #print('---------------------------------------------------------------------------') #REMOVE

        
    end=time.time() #time finished sending packets

    
    
    

    socketClient.send(bye.encode()) #Sends BYE message
    #print('Sendt bye')

    message = socketClient.recv(1024).decode() #Recieving ACK message.

    if(message == 'BYE ACK'):
       #print('Exits...')

        #Closing and exiing 
        socketClient.close() 
    #print

     # --------------------------------------- PRINTING RESULTS --------------------------------------------------
    #Calculating bandwidth
    totaltduration=end-t #gives totalt duration of sending
    sizeMB=check_format(sizesent,'MB') #Gives the size sent in MB instead of B
    bandwidth=sizeMB/totaltduration #The bandwith calculated in MBps
    bandwidth=bandwidth*8 #The bandwidth in mega bite per second
    #print('Sizesendt: '+ str(sizesent)+' B\nSize MB: '+str(sizeMB)+' MB') # REMOVE

    transferformat=check_format(sizesent,format) #Changing to the chosen format from --format
    #print('Sizesendt: '+ str(sizesent)+' B\nSize MB: '+str(sizeMB)+' MB\nSize KB: '+str(transferformat)) #REMOVE

    #sets them to only 2 decimals
    bandwidth = '{0:.2f}'.format(bandwidth)
    transferformat = '{0:.2f}'.format(transferformat)


    #Printig out "IP, Interval, Transfer and Bandwisth" table

    d = {str(serverIP)+":"+ str(port):["0.0 - "+str(sendtime)+'.0', str(transferformat)+' '+format , str(bandwidth)+' Mbps']}
    #print ("{:<15} {:<12} {:<17} {:<10}".format('ID','Interval','Transfer','Bandwith')) #REMOVE?
    table=''
    for k, v in d.items():
        lang, perc, change = v
        print("{:<15} {:<12} {:<17} {:<10}".format(k, lang, perc, change))
    #print('Adding the results to printing') #REMOVE
    #utskrift.append(table)
    #print(table)
    #End of printing table


#_________________________________________________________________________________________________________    


def thread_conn(serverIP, port, sendtime, format, interval, num_connections):
    print('\n')
    #client_thread_list=[]
    for i in range(num_connections):
        #Connecting to Server
        #print('Pørver å lage ny connection') #REMOVE
        print('Client nr '+str(i)+' : '+str(serverIP)+":"+ str(port)+' connected with '+str(serverIP)+' port '+str(port))
        try:
            client_thread=threading.Thread(target=handle_thread_client, args=(serverIP, port, sendtime, format))
            client_thread.start()
            #client_thread.join()
            #Printing confirmation to a connected server.
            #print('CLIENT THREAD: \n'+client_thread))
            #printing+=client_thread
            #client_thread_list.append(client_thread)
            
            
            
        except:
            #If not able to connect, exit system.
            print ("Connection error on connection nr: "+str(i))
            sys.exit()
        
    #Printing out the header row
    print('\n')
    print ("{:<15} {:<12} {:<17} {:<10}".format('ID','Interval','Transfer','Bandwith'))
    #for client_thread in client_thread_list:
    #    client_thread.join()

    exit(1) 
    

    
    

   
        

"""________________________________________________________________________________________________
                                         ADDING ARGUMENTS
    ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""

parser=argparse.ArgumentParser(description="Portifolio 1", epilog="end of help")


# ----------------------- Server --------------------------
parser.add_argument('-s', '--server', action='store_true') 
parser.add_argument('-b','--bind',type=check_IP, default='127.0.0.1') #input IP address
parser.add_argument('-T','--thread',action='store_true')



# ----------------------- Client --------------------------
parser.add_argument('-c', '--client', action='store_true')
parser.add_argument('-I','--serverip',type=check_IP, default='127.0.0.1') #input IP address
parser.add_argument('-t', '--time',type=check_time, default=3)
parser.add_argument('-i','--interval',type=int)
parser.add_argument('-P','--parallel',type=check_num_conn, default=1)
parser.add_argument('-n','--num',type=check_num, default=None)


# ------------------------ Both ---------------------------
parser.add_argument('-p','--port',type=check_port, default=8088) #input Port number
parser.add_argument('-f','--format', type=str, choices=('B','KB','MB'), default='MB')



"""________________________________________________________________________________________________
                                         HANDLE THE ARGUMENTS
    ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""
args = parser.parse_args()
#print('NUM: '+ str(args.num)) #REMOVE

    

#If -s and -c is not specified
if (not args.server and not args.client):
    print('Error: you must run either in server or client mode')
    sys.exit

#If both -c and -s is specified
elif (args.server and args.client):
    print('Error: you can only run server OR client, not both.')
    sys.exit

elif(args.thread):
    print('------------------------------------------------------------------------------------------')
    print('A simpleperf server is listening on port '+ str(args.port))
    print('------------------------------------------------------------------------------------------')

    thread_server(args.serverip, args.port,args.format)

elif(int(args.parallel) > 1):
    print('------------------------------------------------------------------------------------------')
    print('A simpleperf client connecting to server '+str(args.serverip)+', port '+str(args.port))
    print('------------------------------------------------------------------------------------------')

    thread_conn(args.serverip,args.port, int(args.time), args.format, args.interval, int(args.parallel))

elif args.server:
    print('------------------------------------------------------------------------------------------')
    print('A simpleperf server is listening on port '+ str(args.port))
    print('------------------------------------------------------------------------------------------')

    handleServer(args.port,args.bind,args.format)
    
elif args.client:
    print('------------------------------------------------------------------------------------------')
    print('A simpleperf client connecting to server '+str(args.serverip)+', port '+str(args.port))
    print('------------------------------------------------------------------------------------------')
    handleClient(args.serverip,args.port, int(args.time), args.format, args.interval, args.num)

sys.exit
