import sys 
import argparse

# CUSTOM FUNCTIONS that need to be defined before the arguments

def check_IP(val):
    

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


parser=argparse.ArgumentParser(description="Portifolio 1", epilog="end of help")

#Adding arguments
# ------ Server -------
parser.add_argument('-s', '--server', action='store_true') 
parser.add_argument('-b', '--bind', type=check_IP) #input IP address
parser.add_argument('-p','--port',type=check_port, default=8088) #input Port number



# ------ Client ------
parser.add_argument('-c', '--client', action='store_true') 



