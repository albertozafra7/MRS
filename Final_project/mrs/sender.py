import socket
import json

# Define IP address and port
HOST = "127.0.0.1"  # Replace with the receiver's IP address
PORT = 65432        # Replace with desired port number

# Create a socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
sock.connect((HOST, PORT))

# Sample JSON data
data = {"message": "Im the sender", "value": 33}

# Encode data to JSON string
json_data = json.dumps(data)

# Send the JSON string
sock.sendall(json_data.encode())

print("Sent JSON data:", json_data)

# Receive reply from the listener
reply = sock.recv(1024).decode()

try:
    json_data = json.loads(reply)
    print(f"Received reply: ", json_data)

except json.JSONDecodeError:
    print("Error decoding JSON data:", reply)

# Close the socket
sock.close()
