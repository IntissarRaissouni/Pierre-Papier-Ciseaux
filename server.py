import socket
import threading

# Thread-safe lock for accessing shared resources
clients_lock = threading.Lock()

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

# Function to handle each client connection
def handle_client(client_socket, client_address, clients, scores):
    print(f"[SERVER] New connection from {client_address}")

    # Send welcome message to the client
    client_socket.send(b"Welcome to Pierre-Papier-Ciseaux! Waiting for another player...\n")

    # Wait until two players are connected
    while len(clients) < 2:
        pass

    # Notify both players that the game is starting
    if len(clients) == 2:
        client_socket.send(b"Both players connected!\n")

    while True:
        try:
            # Prompt the client for their choice
            client_socket.send(b"Enter your choice (Pierre, Papier, Ciseaux): ")
            player_choice = client_socket.recv(1024).decode().strip().lower()

            # Validate the choice
            if player_choice not in ["pierre", "papier", "ciseaux"]:
                client_socket.send(b"Invalid choice. Try again.\n")
                continue

            # Update the client's choice in the shared dictionary
            with clients_lock:
                clients[client_address] = player_choice

            # Wait for both players to submit their choices
            while len(clients) < 2 or None in clients.values():
                pass

            # Determine the opponent's choice
            with clients_lock:
                opponent_address = [addr for addr in clients if addr != client_address][0]
                opponent_choice = clients[opponent_address]

            # Determine the result of the game
            result = determine_winner(player_choice, opponent_choice)

            # Update scores and prepare the result message
            if result == 0:
                message = f"It's a tie! Both chose {player_choice.capitalize()}!\n"
            elif result == 1:
                scores[client_address] += 1
                message = f"You win! {player_choice.capitalize()} beats {opponent_choice.capitalize()}!\n"
            else:
                scores[opponent_address] += 1
                message = f"You lose! {opponent_choice.capitalize()} beats {player_choice.capitalize()}!\n"

            # Send the result and score in a single message
            client_socket.send(f"{message}Score:{scores[client_address]}\n".encode())

            # Reset choices for the next round
            with clients_lock:
                clients[client_address] = None
                clients[opponent_address] = None

            # Exit if both players choose to exit
            if all(value == "exit" for value in clients.values()):
                break

        except ConnectionError:
            print(f"[SERVER] Connection lost with {client_address}")
            break

    # Close the client socket
    client_socket.close()

# Main server function
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5555))
    server.listen(2)
    print("[SERVER] Server is running and waiting for connections...")

    clients = {}
    scores = {}
    threads = []

    while True:
        client_socket, client_address = server.accept()
        with clients_lock:
            clients[client_address] = None
            scores[client_address] = 0

        # Start a new thread to handle the client
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address, clients, scores))
        thread.start()
        threads.append(thread)

        # Notify when two players are connected
        if len(clients) == 2:
            print("[SERVER] Both players connected. Let the game begin!")

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()