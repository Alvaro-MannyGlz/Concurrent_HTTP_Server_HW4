# Concurrent HTTP Server with Resource Limits

This project will build on a previous project, a sequential Python HTTP server, to now handle multiple client connections **concurrently** using multi-threading. A key focus is on implementing strict resource management to prevent server overload.
- accept multiple connections from clients (e.g., 12)
- limit the total number of connections a server is allowed to open (e.g., 60)

## Execution and Usage

### Execution

**Launch the Server:** Run the script specifying the port, maximum connections per client, and maximum total connections:

    ```bash
    python http_server_conc.py -p <port> -maxclient <numconn> -maxtotal <numconn>
    ```
    **Example:**
    ```bash
    python http_server_conc.py -p 20001 -maxclient 12 -maxtotal 60
    ```

## Resource Management and Concurrency

### Client Identification Strategy
To enforce the per-client connection limit, a client is identified by the unique **(Client IP Address, Client Port Number)** socket tuple. This is necessary because two different applications on the same machine will have the same IP but different ephemeral ports, satisfying the requirement to distinguish clients.

### Concurrency and Limiting
The server uses thread-safe data structures and Python's `threading.Lock` to enforce limits:

1.  **Global Counter:** A shared, synchronized counter tracks the total number of active connections (`MAX_TOTAL_CONNECTIONS`).
2.  **Per-Client Dictionary:** A shared, synchronized dictionary tracks the connection count for each unique client ID (`MAX_PER_CLIENT`).

The server checks these limits **immediately upon accepting a connection**. If either limit is exceeded, the server sends a rejection and **closes the socket** before allocating any further resources or spawning a thread.

### Concurrency Model
The server utilizes multi-threading: the main thread accepts connections, and a dedicated worker thread is spawned to handle the full request and release the resource counts upon completion.

---

## Implementation Details

### Concurrency Model

The server achieves concurrency using Python's **`threading`** module.

* **Sequential Problem:** The original server was sequential (`while True: accept() -> handle_client()`). The server would **block** inside `handle_client()` until the entire request was finished, preventing any other client from connecting.
* **Threading Solution:** In the `main()` loop, after accepting a new connection (`client_socket`), the server immediately **spawns a new thread** and passes the `client_socket` to the `handle_client` function within that thread.
* **Benefit:** The main thread instantly loops back to `server_socket.accept()`, allowing the server to accept the next client request without waiting for the previous request to complete.

### Protocol Features

* **Protocol Version:** HTTP/1.0
* **Methods Supported:** GET
* **File Serving:** Serves static files (e.g., HTML, CSS, PNG, PDF).
* **Error Handling:** Implements **404 Not Found** for missing files.
* **Content-Type Handling:** Dynamically sets the `Content-Type` header (e.g., `text/html`, `image/png`) to ensure files display correctly in the browser.

---

## Required Questions

#### 1. What is your strategy for identifying unique clients?


#### 2. How do you prevent clients from opening additional connections once they have reached the maximum number?

#### 3. Report the times and speedup for concurrent fetch of the URLs in testcases 1 and 2 with the stock HTTP server.

#### 4. Report the times and speedup for concurrent fetch of the URLs in testcases 1 and 2 with your http_server_conc. Are these numbers the same as above? Why or why not?
