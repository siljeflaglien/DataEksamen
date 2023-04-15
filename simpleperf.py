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
    try:
        value = int(val)
    except ValueError:
        raise argparse.ArgumentTypeError('expected an integer but you entered a string')
        #if not a number, sends error.
    
    if (value<1024 or value>65535):
        print ("It is not a valid port")
        sys.exit
        #Only valid port between [1204-65535]. 
    

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
    size=len(val) #Size of the string writen in

    #Getting the format 'MB' or 'B' og 'KB'
    format = val[size-2]+val[size-1]

    #Getting the numbers out of 
    number=""
    for i in range(size-2): 
        number+=val[i]
    
    
    try:
        number=int(number)
    except ValueError:
        raise argparse.ArgumentTypeError('You did not only get numbers from the string --num')
        #if not a number, sends error.

    if(format=='KB'):
        number=number*1000
    elif(format=='MB'):
        number=number*1000000

    return number

def check_interval(val):
    try:
        value = int(val)
    except ValueError:
        raise argparse.ArgumentTypeError('expected an integer but you entered a string')
        #if not a number, sends error.
    
    if not value>0:
        print('The interval must be > 0')
        sys.exit
        exit(1)
    
    return value #returns value beacuse it was valid and so that it can be used. 
#Printing one and one row of results in --interval
def print_table(ID, from_time , to_time, lastsize, sizesent, lasttime, nowtime,format):
    
    #Size of the interval
    size=sizesent-lastsize #how much sent in the past interval
    transferformat=check_format(size,format) #Changing the format

    #time of the interval
    interval_time = nowtime-lasttime #How much time has past, need for calculating bandwidth

    #Bandwidth of the interval
    sizeMB = check_format(size,'MB') # changing into MB to calculate bandwidth
    sizeMB= sizeMB*8 #Changing from byte to bit
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
    
"""_________________________________________________________________________________________________________________________
                                            THREAD SERVER
    ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""
#Each thread will do this function.
def handle_thread_server(connectionSocket, addr, IP, port,format):
    while True:
        try:
            start = time.time() #Start time
            end = 0 #declaring the variable
            datareceived=0

            while True:
               
                message = connectionSocket.recv(1000).decode() #recieving the packets
                
                #If messange is BYE, connection is closing and we send back a BYE ACK
                if('BYE' in message):  
                    #end = seconds passed until receiving BYE
                    end = time.time() - start
                    datareceived= datareceived+getsizeof(message)

                    #Sending ack message
                    bye = 'BYE:ACK' #Making the ack message
                    connectionSocket.send(bye.encode()) #Sending the ack

                    #Closing the client socket
                    connectionSocket.close()
                    
                    break #Go out of the while
                    
                else:
                    #If not BYE, we got a normal package and add the bytes to how much data we have received
                    datareceived=datareceived + getsizeof(message)
                    
            

             # ----------------------- PRINTING RESULTS ----------------------------
            

            receivedMB = check_format(datareceived, 'MB') # from B -> MB
            rate = receivedMB/end #calculating the rate in mega byte per second
            rate = rate*8 #The rate in mega bite per second 

            transferformat=check_format(datareceived,format) #Changing to the chosen format from --format
            
            #Making them into whole integers
            transferformat=int(transferformat)
            if end>1:
                end=int(end)
            else:
                end=1

            #sets them to only 2 decimals
            rate = '{0:.2f}'.format(rate)
            transferformat = '{0:.2f}'.format(transferformat)
            
            #Printig out "IP, Interval, Received and Rate" table
            print()
            if receivedMB > 0:
                print ("{:<15} {:<12} {:<17} {:<10}".format('ID','Interval','Received','Rate'))
            d = {str(IP)+":"+ str(port):["0.0 - "+str(end)+'.0', str(transferformat)+' '+format , str(rate)+' Mbps']}
            for k, v in d.items():
                lang, perc, change = v
                print ("{:<15} {:<12} {:<17} {:<10}".format(k, lang, perc, change))
            print()
            #End of printing table

        #If the sockets listened to more connections, but no connections came, it goes in this except
        except IOError:
            
            
            sys.exit()# And we terminate the listening for this connection. 


"""________________________________________________________________________________________________
                                         HANDLE SERVER
    ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""
#A server that can handle multiple clients
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
        sys.exit()
    
    serverSocket.listen(5) 
    print('\nSocket is listening and ready to receive\n')
    print('------------------------------------------------------------------------------------------')
   

    conn=1
    while True:
        print()
        conn+=1
        #Establish the connection print('Ready to serve...') connectionSocket, addr =
        connectionSocket, addr = serverSocket.accept() #Establish the connection
        print('A simpleperf client with IP address:' + str(addr) +' is connected with server IP: '+ str(serverPort))#connected and ready

        thread.start_new_thread(handle_thread_server, (connectionSocket, addr, IP,serverPort,format))
    

    
    

"""________________________________________________________________________________________________
                                         NORMAL CLIENT
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

    
    #Connecting to Server
    try:
        socketClient.connect((host,clientPort))
    except:
        #If not able to connect, exit system.
        print ("Connection error")
        sys.exit()

    #Printing confirmation to a connected server.
    print('Client connected with '+str(host)+' port '+str(clientPort))

    #Marking the starttime (it is in seconds)
    t= time.time()

    
    #Sending data normal, no interval or num
    if interval is None and num is None:
        while(time.time() < t+int(sendtime)): #sending it for "sendtime"-amount of seonds
            socketClient.send(data.encode()) #Sending the data to the server
            sizesent+=getsizeof(data)

        
    #If num is specified with how many bytes to send over. 
    elif num is not None:

        while sizesent+datasize <= num : #sending it as long as it does no exceed the num size.
            socketClient.send(data.encode()) #Sending the data to the server
            sizesent+=datasize

        print(sizesent)    
    
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
        while (time.time() < float(t)+float(sendtime)): #sending it for "sendtime"-amount of seonds

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

        print('---------------------------------------------------------------------------')
        
       
        


        
    end=time.time() #time finished sending packets

    #Method that print one and one row of data results
    

    
    
    
  
    socketClient.send(bye.encode()) #Sends BYE message
    

    message = socketClient.recv(1024).decode() #Recieving ACK message.
    if('BYE:ACK' in message):
        #Closing and exiing 
        socketClient.close() 
    

    # --------------------------------------- PRINTING RESULTS --------------------------------------------------
    #Calculating bandwidth
    totaltduration=end-t #gives totalt duration of sending
    sizeMB=check_format(sizesent,'MB') #Gives the size sent in MB instead of B
    bandwidth=sizeMB/totaltduration #The bandwith calculated in MBps
    bandwidth=bandwidth*8 #The bandwidth in mega bite per second


    transferformat=check_format(sizesent,format) #Changing to the chosen format from --format

    #sets them to only 2 decimals
    bandwidth = '{0:.2f}'.format(bandwidth)
    transferformat = '{0:.2f}'.format(transferformat)
    if totaltduration>1:
        totaltduration=int(totaltduration)
    else:
        totaltduration=1

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





#------------------------------------------------------------------------------------------------




"""__________________________________________________________________________________________________________________________
                                            THREAD CLIENT
    ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""
    
def handle_thread_client(serverIP, port, sendtime, format):
    
    socketClient = socket(AF_INET, SOCK_STREAM) #Creating socket for client
    clientPort = port #Port number of the server
    host = serverIP #IP address of the server
    bye = 'BYE' #for when we send the bye message
    sizesent=0 #sizesent
    sendtime=str(sendtime) #changing the seconds to a String to make it easier further down

    #Making a data packet with 1000bytes
    data='0'*1000 #the byte size will be 1000 bytes with 951

    #Connecting to Server
    try:
        socketClient.connect((host,clientPort))
    except:
        #If not able to connect, exit system.
        print ("Connection error")
        sys.exit()

    
    #Marking the time (it is in seconds)
    t= time.time()

    #A while who sends data
    while (time.time() < t+int(sendtime)): #sending it for "sendtime"-amount of seonds
        #print('Inne i whilen')
        socketClient.send(data.encode()) #Sending the data to the server
        sizesent+=getsizeof(data) #adding to bytes sent


        
    end=time.time() #time finished sending packets



    socketClient.send(bye.encode()) #Sends BYE message

    message = socketClient.recv(1024).decode() #Recieving ACK message.

    if(message == 'BYE ACK'):
        #Closing and exiing 
        socketClient.close() 
    

    # --------------------------------------- PRINTING RESULTS --------------------------------------------------
    #Calculating bandwidth
    totaltduration=end-t #gives totalt duration of sending
    sizeMB=check_format(sizesent,'MB') #Gives the size sent in MB instead of B
    bandwidth=sizeMB/totaltduration #The bandwith calculated in MBps
    bandwidth=bandwidth*8 #The bandwidth in mega bite per second

    transferformat=check_format(sizesent,format) #Changing to the chosen format from --format

    #sets them to only 2 decimals
    bandwidth = '{0:.2f}'.format(bandwidth)
    transferformat = '{0:.2f}'.format(transferformat)


    #Printig out "IP, Interval, Transfer and Bandwidth" table

    d = {str(serverIP)+":"+ str(port):["0.0 - "+str(sendtime)+'.0', str(transferformat)+' '+format , str(bandwidth)+' Mbps']}
    for k, v in d.items():
        lang, perc, change = v
        print("{:<15} {:<12} {:<17} {:<10}".format(k, lang, perc, change))
    
    #End of printing table


#_________________________________________________________________________________________________________    


def thread_conn(serverIP, port, sendtime, format, interval, num_connections):
    print('\n')
    for i in range(num_connections):
        i+=1 #to make it start at 1,2,3,4,5 and not 0,1,2,3,4 while printing

        #Connecting to Server
        print('Client nr '+str(i)+' : '+str(serverIP)+":"+ str(port)+' connected with '+str(serverIP)+' port '+str(port))
        try:
            client_thread=threading.Thread(target=handle_thread_client, args=(serverIP, port, sendtime, format))
            client_thread.start()
    
            
            
        except:
            #If not able to connect, exit system.
            print ("Connection error on connection nr: "+str(i))
            sys.exit()
        
    #Printing out the header row
    print('\n')
    print ("{:<15} {:<12} {:<17} {:<10}".format('ID','Interval','Transfer','Bandwith'))

    exit(1) 
    

    
    

   
        

"""________________________________________________________________________________________________
                                         ADDING ARGUMENTS
    ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""

parser=argparse.ArgumentParser(description="Portfolio 1", epilog="end of help")


# ----------------------- Server --------------------------
parser.add_argument('-s', '--server', action='store_true', help= 'If you run with -s you are running the server side') 
parser.add_argument('-b','--bind',type=check_IP, default='127.0.0.1', help='IP address of the server') #input IP address
parser.add_argument('-T','--thread',action='store_true',help='Add -T if you want to run a multithreading server')



# ----------------------- Client --------------------------
parser.add_argument('-c', '--client', action='store_true',  help= 'If you run with -c you are running the client side ')
parser.add_argument('-I','--serverip',type=check_IP, default='127.0.0.1', help='IP address of the server') #input IP address
parser.add_argument('-t', '--time',type=check_time, default=25, help='How many seconds you would like to send packets for')
parser.add_argument('-i','--interval',type=check_interval, help='Time intervall in seconds you want updated information printet.')
parser.add_argument('-P','--parallel',type=check_num_conn, default=1, help='How many connections you want with server. Note: You have to run a multithread server with -T.')
parser.add_argument('-n','--num',type=check_num, default=None, help='How much data do you wanna send over? Has to be a number followed by B, KB or MB, e.g. 100KB')


# ------------------------ Both ---------------------------
parser.add_argument('-p','--port',type=check_port, default=8088, help='Port number of either the server or the client. the port must be an integer and in the range [1024,65535]') #input Port number
parser.add_argument('-f','--format', type=str, choices=('B','KB','MB'), default='MB', help='What format the results should be printet in. Options: B, KB, MB')



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


elif(int(args.parallel) > 1 and args.client):
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
