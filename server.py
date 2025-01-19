import socket
import threading
import queue

# Function to determine the winner of the game
def determine_winner(choice1, choice2):
    if choice1 == choice2:
        return 0  # Tie
    elif (
        (choice1 == "pierre" and choice2 == "ciseaux") or
        (choice1 == "papier" and choice2 == "pierre") or
        (choice1 == "ciseaux" and choice2 == "papier")
    ):
        return 1  # Player 1 wins
    else:
        return -1  # Player 2 wins

# Shared resources
client_sockets = []
choice_queue = queue.Queue()
scores = {}

# Function to handle the game logic
def game_loop():
    while True:
        if len(client_sockets) < 2:
            continue  # Wait for two clients

        # Collect choices from both clients
        choices = []
        try:
            for _ in range(2):
                choice = choice_queue.get()
                choices.append(choice)
        except queue.Empty:
            continue  # Not enough choices yet

        # Determine the winner
        result = determine_winner(choices[0], choices[1])

        # Update scores
        if result == 1:
            scores[client_sockets[0]] += 1
        elif result == -1:
            scores[client_sockets[1]] += 1

        # Prepare result messages
        if result == 0:
            msg = f"It's a tie! Both chose {choices[0].capitalize()}!\n"
        elif result == 1:
            msg = f"Player 1 wins! {choices[0].capitalize()} beats {choices[1].capitalize()}!\n"
        else:
            msg = f"Player 2 wins! {choices[1].capitalize()} beats {choices[0].capitalize()}!\n"

        # Send results to both clients
        for sock in client_sockets:
            score = scores.get(sock, 0)
            sock.send(f"{msg}Score: {score}\n".encode())

# Function to handle each client connection
def handle_client(client_socket):
    client_socket.send(b"Welcome to Pierre-Papier-Ciseaux! Waiting for another player...\n")
    client_sockets.append(client_socket)
    scores[client_socket] = 0

    # Assign player roles
    if len(client_sockets) == 1:
        client_socket.send(b"ROLE: Player 1\n")
    elif len(client_sockets) == 2:
        client_socket.send(b"ROLE: Player 2\n")
        
    # Notify both players that the game is starting
    if len(client_sockets) == 2:
        for sock in client_sockets:
            sock.send(b"Both players connected!\n")

    while True:
        try:
            # Prompt the client for their choice
            client_socket.send(b"Enter your choice (Pierre, Papier, Ciseaux): ")
            player_choice = client_socket.recv(1024).decode().strip().lower()

            # Validate the choice
            if player_choice not in ["pierre", "papier", "ciseaux"]:
                client_socket.send(b"Invalid choice. Try again.\n")
                continue

            # Add the choice to the queue
            choice_queue.put(player_choice)

        except ConnectionError:
            print(f"[SERVER] Connection lost with {client_socket.getpeername()}")
            break

    # Remove the client from the list and scores
    client_sockets.remove(client_socket)
    del scores[client_socket]
    client_socket.close()

# Main server function
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5555))
    server.listen(2)
    print("[SERVER] Server is running and waiting for connections...")

    # Start the game loop in a separate thread
    game_thread = threading.Thread(target=game_loop)
    game_thread.start()

    while True:
        client_socket, client_address = server.accept()
        print(f"[SERVER] New connection from {client_address}")

        # Start a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

if __name__ == "__main__":
    main()