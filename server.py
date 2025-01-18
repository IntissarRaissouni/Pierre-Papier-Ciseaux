import socket
import threading

# Server-side code
def handle_client(client_socket, client_address, clients, scores):
    print(f"[SERVER] New connection from {client_address}")

    client_socket.send(b"Welcome to Pierre-Papier-Ciseaux! Waiting for another player...\n")
    while len(clients) < 2:
        pass  # Wait until two players are connected

    if len(clients) == 2:
        client_socket.send(b"Both players connected!\n")

    while True:
        try:
            client_socket.send(b"Enter your choice (Pierre, Papier, Ciseaux): ")
            player_choice = client_socket.recv(1024).decode().strip().lower()

            if player_choice not in ["pierre", "papier", "ciseaux"]:
                client_socket.send(b"Invalid choice. Try again.\n")
                continue

            clients[client_address] = player_choice

            while len(clients) < 2 or None in clients.values():
                pass  # Wait for both players to submit their choices

            opponent_address = [addr for addr in clients if addr != client_address][0]
            opponent_choice = clients[opponent_address]

            result = determine_winner(player_choice, opponent_choice)

            if result == 0:
                message = f"It's a tie! Both chose {player_choice.capitalize()}!\n"
            elif result == 1:
                scores[client_address] += 1
                message = f"You win! {player_choice.capitalize()} beats {opponent_choice.capitalize()}!\n"
            else:
                scores[opponent_address] += 1
                message = f"You lose! {opponent_choice.capitalize()} beats {player_choice.capitalize()}!\n"

            client_socket.send(message.encode())
            client_socket.send(f"Current Score: {scores[client_address]}\n".encode())

            if all(value == "exit" for value in clients.values()):
                break

        except ConnectionError:
            print(f"[SERVER] Connection lost with {client_address}")
            break

    client_socket.close()


def determine_winner(choice1, choice2):
    if choice1 == choice2:
        return 0
    elif (
        (choice1 == "pierre" and choice2 == "ciseaux") or
        (choice1 == "papier" and choice2 == "pierre") or
        (choice1 == "ciseaux" and choice2 == "papier")
    ):
        return 1
    else:
        return -1


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5555))
    server.listen(2)
    print("[SERVER] Server is running and waiting for connections...")

    clients = {}
    scores = {}

    while len(clients) < 2:
        client_socket, client_address = server.accept()
        clients[client_address] = None
        scores[client_address] = 0
        threading.Thread(target=handle_client, args=(client_socket, client_address, clients, scores)).start()

    print("[SERVER] Both players connected. Let the game begin!")


if __name__ == "__main__":
    main()
