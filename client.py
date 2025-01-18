import socket

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = input("Enter server IP (default 127.0.0.1): ") or "127.0.0.1"
    port = 5555

    try:
        client.connect((server_address, port))
        print("[CLIENT] Connected to the server.")

        while True:
            message = client.recv(1024).decode()
            print(message, end="")

            if "Enter your choice" in message:
                choice = input().strip().lower()
                client.send(choice.encode())
            elif "Current Score" in message or "Both players connected!" in message:
                continue
            elif "Invalid choice" in message:
                print("[CLIENT] Please enter either Pierre, Papier, or Ciseaux.")

    except ConnectionError:
        print("[CLIENT] Connection to the server was lost.")
    finally:
        client.close()

if __name__ == "__main__":
    main()
