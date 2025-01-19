import sys
import socket
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QMessageBox, QHBoxLayout
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt

# Start Menu class
class StartMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pierre-Papier-Ciseaux - Menu")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QMainWindow { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FBFBFB, stop:1 #E8F9FF); }
            QLabel { font-size: 36px; font-family: 'Comic Sans MS'; font-weight: bold; color: #333333; }
            QPushButton { font-size: 24px; font-family: 'Arial'; font-weight: bold; color: white; background-color: #C4D9FF; border-radius: 15px; padding: 20px; }
            QPushButton:hover { background-color: #C5BAFF; }
            QPushButton:pressed { background-color: #A8A3FF; }
        """)

        layout = QVBoxLayout()
        title_label = QLabel("Pierre-Papier-Ciseaux", self)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 48px; font-weight: bold; color: #333333;")
        layout.addWidget(title_label)

        start_button = QPushButton("Start Game", self)
        start_button.clicked.connect(self.start_game)
        layout.addWidget(start_button)

        quit_button = QPushButton("Quit", self)
        quit_button.clicked.connect(self.close)
        layout.addWidget(quit_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def start_game(self):
        self.game_client = GameClient()
        self.game_client.show()
        self.close()

# Game Client class
class GameClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pierre-Papier-Ciseaux")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QMainWindow { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FBFBFB, stop:1 #E8F9FF); }
            QLabel { font-size: 24px; font-family: 'Arial'; font-weight: bold; color: #333333; }
            QPushButton { font-size: 18px; font-weight: bold; color: white; background-color: #C4D9FF; border-radius: 10px; padding: 15px; }
            QPushButton:hover { background-color: #C5BAFF; }
            QPushButton:pressed { background-color: #A8A3FF; }
        """)

        layout = QVBoxLayout()
        self.status_label = QLabel("Status: Disconnected", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #FF6347;")
        layout.addWidget(self.status_label)

        self.score_label = QLabel("Score: 0", self)
        self.score_label.setAlignment(Qt.AlignCenter)
        self.score_label.setStyleSheet("font-size: 36px; font-weight: bold; color: #C4D9FF;")
        layout.addWidget(self.score_label)

        self.result_label = QLabel("Make your choice!", self)
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #333333;")
        layout.addWidget(self.result_label)

        choice_layout = QHBoxLayout()
        choice_layout.setAlignment(Qt.AlignCenter)

        self.pierre_button = QPushButton(self)
        self.pierre_button.setText(" Pierre ")
        self.pierre_button.clicked.connect(lambda: self.send_choice("pierre"))
        choice_layout.addWidget(self.pierre_button)

        self.papier_button = QPushButton(self)
        self.papier_button.setText(" Papier ")
        self.papier_button.clicked.connect(lambda: self.send_choice("papier"))
        choice_layout.addWidget(self.papier_button)

        self.ciseaux_button = QPushButton(self)
        self.ciseaux_button.setText(" Ciseaux ")
        self.ciseaux_button.clicked.connect(lambda: self.send_choice("ciseaux"))
        choice_layout.addWidget(self.ciseaux_button)

        layout.addLayout(choice_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.client_socket = None
        self.connected = False
        self.score = 0

        self.connect_to_server()

    def connect_to_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(("127.0.0.1", 5555))
            self.connected = True
            self.status_label.setText("Status: Connected")
            self.status_label.setStyleSheet("color: #4CAF50; font-size: 24px; font-weight: bold;")

            # Start a thread to receive messages from the server
            threading.Thread(target=self.receive_messages, daemon=True).start()

        except ConnectionError:
            self.status_label.setText("Status: Failed to Connect")
            self.status_label.setStyleSheet("color: #FF6347; font-size: 24px; font-weight: bold;")
            self.connected = False

    def send_choice(self, choice):
        if self.connected:
            try:
                self.client_socket.send(choice.encode())
                self.result_label.setText("Waiting for the server's response...")
            except Exception as e:
                self.result_label.setText(f"Error sending choice: {str(e)}")
        else:
            QMessageBox.warning(self, "Connection Error", "Not connected to the server.")

    def receive_messages(self):
        while self.connected:
            try:
                message = self.client_socket.recv(1024).decode()
                if not message:
                    break

                # Check if the message contains the score
                if "Score:" in message:
                    # Extract the score and result from the message
                    parts = message.split("Score: ")
                    result_msg = parts[0].strip()
                    score_str = parts[1].strip().split("\n")[0]
                    self.score = int(score_str)
                    self.score_label.setText(f"Score: {self.score}")
                    self.result_label.setText(result_msg)
                else:
                    self.result_label.setText(message)

            except ConnectionError:
                self.result_label.setText("Connection lost.")
                self.connected = False
                break

    def closeEvent(self, event):
        if self.connected:
            self.client_socket.close()
        event.accept()

# Main application entry point
if __name__ == "__main__":
    app = QApplication(sys.argv)
    menu = StartMenu()
    menu.show()
    sys.exit(app.exec_())