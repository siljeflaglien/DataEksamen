# Simpleperf

This is a tool for measuring network throughput which could open up a TCP connection to transfer data.

To open a connection, you have to run this script in two modes; firstly in server mode, then in client mode. 

---
### Server
To invoke the server side, these are the available options:
| flag | long flag | input | type | Description |
| ----- | ------------- | -------- | -------- | -------- |
| -s |     --server       |   | (boolean) | enable the server mode |
| -b | --bind | ip address | string | Allows to select the ip address of the server’s interface where the client should connect. It must be in the dotted decimal notation format, e.g. 10.0.0.2. Default: 127.0.0.1 |
| -p | --port | port number | integer | llows to use select port number on which the server should listen; the port must be an integer and in the range [1024, 65535], default: 8088 |
| -f | --format | MB | string | Allows you to choose the format of the summary of results - it should be either in B, KB or MB, default=MB  |


---
### Client

To invoke the client side, these are the available options:

| flag | long flag | input | type | Description |
| ----- | ------------- | -------- | -------- | --------|
|-c |--client||(boolean)|Enable the client mode|
|-I|--serverip |ip address|string|Selects the ip address of the server. It must be in the dotted decimal notation format, e.g. 10.0.0.2. default: 127.0.0.1|
| -p | --port | port number | integer | llows to use select port number on which the server should listen; the port must be an integer and in the range [1024, 65535], default: 8088 |
|-t|--time|seconds|integer|The total duration in seconds for which data should be generated, also sent to the server (if it is set with -t flag at the client side) and must be > 0. Default: 25 seconds|
|-f|--format|MB|string|Allows you to choose the format of the summary of results - it should be either in B, KB or MB, default=MB )|
|-i|--interval|z|integer|Print statistics per z second|
|-P|   --parallel  |no_of_conn|integer|Creates parallel connections to connect to the server and send data - it must be 1 and the max value should be 5 - default:1|
|-n|--num|no_of_bytes|string|Transfer number of bytes specfied by -n flag, it should be either in B, KB or MB|

---

## Tests to generate data
python3 simpleperf.py -s -p 8889 -f KB
python3 simpleperf.py -c -p 8889 -n 10KB -f KB:
ID              Interval     Transfer          Bandwith  
127.0.0.1:8889  0.0 - 5.0    10.00 KB          211.83 Mbps

Runs with sudo mn --custom portfolio-topology.py --topo topo

