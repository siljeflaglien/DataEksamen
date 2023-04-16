# Simpleperf

This is a tool for measuring network throughput which could open up a TCP connection to transfer data.

To open a connection, you have to run this script in two modes; firstly in server mode, then in client mode. 

---
To invoke the


python3 simpleperf.py -s -p 8889 -f KB
python3 simpleperf.py -c -p 8889 -n 10KB -f KB:
ID              Interval     Transfer          Bandwith  
127.0.0.1:8889  0.0 - 5.0    10.00 KB          211.83 Mbps

Runs with sudo mn --custom portfolio-topology.py --topo topo

