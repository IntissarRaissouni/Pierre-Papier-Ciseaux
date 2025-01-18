import sys
import socket
import threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QMessageBox
)

class GameClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pierre-Papier-Ciseaux")
        self.setGeometry(200, 200, 400, 300)

        self.layout = QVBoxLayout()

        self.status_label = QLabel("Status: Disconnected", self)
        self.layout.addWidget(self.status_label)

        self.result_label = QLabel("Welcome to Pierre-Papier-Ciseaux!", self)
        self.layout.addWidget(self.result_label)

        self.pierre_button = QPushButton("Pierre", self)
        self.pierre_button.clicked.connect(lambda: self.send_choice("pierre"))
        self.layout.addWidget(self.pierre_button)

        self.papier_button = QPushButton("Papier", self)
        self.papier_button.clicked.connect(lambda: self.send_choice("papier"))
        self.layout.addWidget(self.papier_button)

        self.ciseaux_button = QPushButton("Ciseaux", self)
        self.ciseaux_button.clicked.connect(lambda: self.send_choice("ciseaux"))
        self.layout.addWidget(self.ciseaux_button)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        self.client_socket = None
        self.connected = False

        self.connect_to_server()

    def connect_to_server(self):
        server_address = "127.0.0.1"
        port = 5555

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((server_address, port))
            self.connected = True
            self.status_label.setText("Status: Connected")

            threading.Thread(target=self.receive_messages, daemon=True).start()
        except ConnectionError:
            self.show_error("Failed to connect to the server.")

    def send_choice(self, choice):
        if self.connected:
            try:
                self.client_socket.send(choice.encode())
            except ConnectionError:
                self.show_error("Connection to the server was lost.")
        else:
            self.show_error("Not connected to the server.")

    def receive_messages(self):
        while self.connected:
            try:
                message = self.client_socket.recv(1024).decode()
                self.result_label.setText(message)

                if "Invalid choice" in message:
                    self.show_error("Invalid choice. Please try again.")

            except ConnectionError:
                self.connected = False
                self.status_label.setText("Status: Disconnected")
                break

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)

    def closeEvent(self, event):
        if self.connected and self.client_socket:
            self.client_socket.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = GameClient()
    client.show()
    sys.exit(app.exec_())
