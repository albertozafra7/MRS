import socket
import json

# Define port to listen on
PORT = 65432  # Replace with the same port number used by sender

# Create a socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
sock.bind(("", PORT))

# Listen for incoming connections
sock.listen(1)
print("Listening in port", PORT)

while True:
    # Accept a connection
    conn, addr = sock.accept()

    print("Connected by", addr)

    # Receive data from the client
    data = conn.recv(1024).decode()

    # Decode JSON data
    try:
        json_data = json.loads(data)
        print("Received JSON data:", json_data)

        # Prepare a reply message (modify as needed)
        reply = {"message": "Como 33", "value": 33}
        json_data = json.dumps(reply)

        # Encode and send the reply
        conn.sendall(json_data.encode())
    except json.JSONDecodeError:
        print("Error decoding JSON data:", data)
        reply = "Error: Invalid JSON data received"
        conn.sendall(reply.encode())

    # Close the connection
    conn.close()

# Close the socket
sock.close()
