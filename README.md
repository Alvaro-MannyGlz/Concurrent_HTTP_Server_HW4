# Concurrent HTTP Server with Resource Limits

This project will build on a previous project, a sequential Python HTTP server, to now handle multiple client connections **concurrently** using multi-threading. A key focus is on implementing strict resource management to prevent server overload.
- accept multiple connections from clients (e.g., 12)
- limit the total number of connections a server is allowed to open (e.g., 60)

## Execution and Usage

### Execution

1.  **Launch the Server:** Run the script from your terminal, specifying the port number with the `-p` flag:

    ```bash
    python http_server.py -p 8080
    ```
    (Replace `8080` with any unused port number.)

2.  **Test with a Browser:** Open your web browser and request a file from the running server:

    ```
    http://localhost:8080/index.html
    ```
    (Ensure you have the requested file, e.g., `index.html`, in the same directory.)

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

#### 1. What is the difference between this `http_server` and Apache?

This server is a **simple, basic implementation** designed for educational purposes. It handles only static files, sequential processing of headers/body, and the basic HTTP/1.0 GET method. **Apache** is a robust, production-grade web server that handles complex features such as concurrency management (using processes or threads), dynamic content generation (via modules), advanced security, persistent connections (HTTP/1.1+), and complex configuration/virtual hosting.

#### 2. How can you write `http_server` to allow only certain browsers (e.g., Chrome) to download content?

