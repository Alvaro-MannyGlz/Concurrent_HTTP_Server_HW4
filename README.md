# Concurrent HTTP Server with Resource Limits

This project will build on a previous project, a sequential Python HTTP server, to now handle multiple client connections **concurrently** using multi-threading. A key focus is on implementing strict resource management to prevent server overload.
- accept multiple connections from clients (e.g., 12)
- limit the total number of connections a server is allowed to open (e.g., 60)

## 🚀 Execution and Usage

### Prerequisites
...

### Launching the Server
The server requires three specific command-line arguments to set the resource limits.

```bash
./http_server_conc.py -p <port> -maxclient <numconn> -maxtotal <numconn>
