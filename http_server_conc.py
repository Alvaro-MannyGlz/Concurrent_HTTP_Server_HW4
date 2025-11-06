# This code right here is the exact one I used for the previous project
# First Change to section 1 and section 4 to adapt the threading into the code

# --- Import Necessary Modules ---                                                                                         <- Section 1
import sys
import socket
import os
import threading

MAX_PER_CLIENT = 0
MAX_TOTAL_CONNECTIONS = 0

# Thread-safe counter for total active connections
activeConnections = 0

# Dictionary to track connections per client: {('IP', port): count}
client_connection_counts = {}

# Lock to synchronize access to the global counters
RESOURCE_LOCK = threading.Lock()

# --- Define Helper Functions ---                                                                                          <- Section 2

# Take raw request data and extracts the essential parts, specifically:
#          The requested file path
#          The HTTP method
#          The 'User-Agent' header
def parse_request(request_data):
    lines = request_data.splitlines()
    if not lines:
        return None, None, None

    # Parse the request line: e.g., "GET /index.html HTTP/1.0"
    parts = lines[0].split()
    if len(parts) < 2:
        return None, None, None

    method = parts[0]
    path = parts[1]

    # Extract User-Agent header if available
    user_agent = None
    for line in lines:
        if line.lower().startswith("user-agent:"):
            user_agent = line.split(":", 1)[1].strip()
            break

    return method, path, user_agent

# Based on the file extension (e.g., .html, .png, .pdf), determine the correct
# Content-Type string for the HTTP response header. (Q2 in README)
def get_content_type(file_path):
    extension_map = {
        ".html": "text/html",
        ".htm": "text/html",
        ".txt": "text/plain",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".css": "text/css",
        ".js": "application/javascript",
        ".pdf": "application/pdf",
    }

    for ext, content_type in extension_map.items():
        if file_path.endswith(ext):
            return content_type
    return "application/octet-stream"

# Construct the complete HTTP response message, including headers and the body.
#          Handles Success and Failure cases
def build_response(status_code, content_type=None, body=None):
    reasons = {
        200: "OK",
        403: "Forbidden",
        404: "Not Found",
    }

    reason = reasons.get(status_code, "Unknown")
    response = f"HTTP/1.0 {status_code} {reason}\r\n"

    if content_type:
        response += f"Content-Type: {content_type}\r\n"

    response += "\r\n"  # End of headers

    if body:
        if isinstance(body, str):
            body = body.encode()
        return response.encode() + body
    else:
        return response.encode()


# --- Client Connection Handler ---                                                                                        <- Section 3

def handle_client(client_socket):
    try:
        # Read Request: Read all incoming data from the 'client_socket'.
        request_data = client_socket.recv(1024).decode()
        if not request_data:
            return
        
        # Print Debug Info: Print the inbound request message.
        print("----- Incoming Request -----")
        print(request_data)

        # Parse Request: Call 'parse_request' to get the requested file path and User-Agent.
        method, path, user_agent = parse_request(request_data)
        if not method or not path:
            return
        
        # Security Check: If the browser is not allowed, send a 403 response
        if user_agent and "curl" in user_agent.lower():
            body = "<html><body><h1>403 Forbidden</h1></body></html>"
            response = build_response(403, "text/html", body)
            client_socket.sendall(response)
            return
        
        # File Handling:
        #   a. Check if the file exists on the server's file system
        #   b. If the file doesn't exist, build and send a 404 Not Found response.
        #   c. If the file exist, read its binary content.
        if path == "/":
            path = "/index.html"
        file_path = "." + path  

        # Builds and sends response
        if not os.path.isfile(file_path):
            body = "<html><body><h1>404 Not Found</h1></body></html>"
            response = build_response(404, "text/html", body)
            client_socket.sendall(response)
            return

        # File exists
        with open(file_path, "rb") as f:
            content = f.read()

        content_type = get_content_type(file_path)
        response = build_response(200, content_type, content)
        client_socket.sendall(response)

    except Exception as e:
        print(f"Error handling client: {e}")

    finally:
        # Close Connection
        client_socket.close()

# --- New Helper Function for Thread Cleanup ---
def handle_client_wrapper(client_socket, client_id):
    global active_connections, client_connection_counts, RESOURCE_LOCK
    
    try:
        # Call your original client handler
        handle_client(client_socket)
        
    finally:
        # --- RESOURCE DECREMENT LOGIC (CRITICAL CLEANUP) ---
        with RESOURCE_LOCK:
            # Decrement the total counter
            active_connections -= 1
            
            # Decrement the per-client counter
            client_connection_counts[client_id] -= 1
            
            # Optional: Clean up the dictionary entry if the count hits zero
            if client_connection_counts[client_id] == 0:
                del client_connection_counts[client_id]

            print(f"Connection closed for {client_id}. Total active: {active_connections}")

# --- Main Server Loop ---                                                                                                <- Section 4
# Initialize the server and keeps it running indefinitely.
def main():
    global MAX_PER_CLIENT, MAX_TOTAL_CONNECTIONS, RESOURCE_LOCK, active_connections, client_connection_counts
    
    # Argument Check: Update to accept 7 arguments
    if len(sys.argv) != 7 or sys.argv[1] != "-p" or sys.argv[3] != "-maxclient" or sys.argv[5] != "-maxtotal":
        print(f"Usage: {sys.argv[0]} -p <port> -maxclient <numconn> -maxtotal <numconn>")
        sys.exit(1)

    # Parse and set limits
    try:
        port = int(sys.argv[2])
        # Assign global limits from command line
        MAX_PER_CLIENT = int(sys.argv[4])
        MAX_TOTAL_CONNECTIONS = int(sys.argv[6])
    except ValueError:
        print("Error: Port and limits must be integers.")
        sys.exit(1)

    # Socket Creation: Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind and Listen
    server_socket.bind(("", port))
    server_socket.listen(5)
    print(f"HTTP Server running on http://localhost:{port}/")

    # 4. Infinite Loop: Handle connections concurrently
    try:
        while True:
            client_socket, client_addr = server_socket.accept()
            # client_addr is a tuple: (IP_ADDRESS, PORT)
            
            # --- RESOURCE CHECK AND INCREMENT LOGIC ---
            with RESOURCE_LOCK:
                client_id = client_addr # Use the (IP, Port) tuple as the unique identifier
                client_count = client_connection_counts.get(client_id, 0)

                # System-wide limit
                if active_connections >= MAX_TOTAL_CONNECTIONS:
                    print(f"Connection REJECTED: System-wide limit ({MAX_TOTAL_CONNECTIONS}) reached.")
                    client_socket.close()
                    continue 

                # Per-client limit
                if client_count >= MAX_PER_CLIENT:
                    print(f"Connection REJECTED: Client limit ({MAX_PER_CLIENT}) reached for {client_id}.")
                    client_socket.close()
                    continue

                # --- IF ACCEPTED: INCREMENT COUNTERS ---
                active_connections += 1
                client_connection_counts[client_id] = client_count + 1
                
                print(f"Connection ACCEPTED from {client_id}. Total active: {active_connections}")
            
            # Spawn Thread (Uses the wrapper for automatic resource cleanup)
            client_thread = threading.Thread(
                target=handle_client_wrapper,
                args=(client_socket, client_id)
            )
            client_thread.daemon = True
            client_thread.start()

    except KeyboardInterrupt:
        print("\nShutting down server...")

    finally:
        server_socket.close()

# --- Execution Block ---                                                                                                  <- Section 5
if __name__ == "__main__":
    main()