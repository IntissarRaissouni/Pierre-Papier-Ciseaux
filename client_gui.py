import sys
import socket
import threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QMessageBox, QHBoxLayout,
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QSize

# Start Menu class
class StartMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pierre-Papier-Ciseaux - Menu")
        self.setGeometry(100, 100, 800, 600)

        # Set a gradient background
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FBFBFB, stop:1 #E8F9FF);
            }
            QLabel {
                font-size: 36px;
                font-family: 'Comic Sans MS';
                font-weight: bold;
                color: #333333;
            }
            QPushButton {
                font-size: 24px;
                font-family: 'Arial';
                font-weight: bold;
                color: white;
                background-color: #C4D9FF;
                border-radius: 15px;
                padding: 20px;
            }
            QPushButton:hover {
                background-color: #C5BAFF;
            }
            QPushButton:pressed {
                background-color: #A8A3FF;
            }
        """)

        # Main layout
        self.layout = QVBoxLayout()

        # Title label
        self.title_label = QLabel("Pierre-Papier-Ciseaux", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 48px; font-weight: bold; color: #333333;")
        self.layout.addWidget(self.title_label)

        # Start game button
        self.start_button = QPushButton("Start Game", self)
        self.start_button.clicked.connect(self.start_game)
        self.layout.addWidget(self.start_button)

        # Quit button
        self.quit_button = QPushButton("Quit", self)
        self.quit_button.clicked.connect(self.close)
        self.layout.addWidget(self.quit_button)

        # Main container
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def start_game(self):
        """Open the GameClient window and close the StartMenu."""
        self.game_client = GameClient()
        self.game_client.show()
        self.close()

# Game Client class
class GameClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pierre-Papier-Ciseaux")
        self.setGeometry(100, 100, 800, 600)

        # Set a gradient background
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FBFBFB, stop:1 #E8F9FF);
            }
            QLabel {
                font-size: 24px;
                font-family: 'Arial';
                font-weight: bold;
                color: #333333;
            }
            QPushButton {
                font-size: 18px;
                font-weight: bold;
                color: white;
                background-color: #C4D9FF;
                border-radius: 10px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #C5BAFF;
            }
            QPushButton:pressed {
                background-color: #A8A3FF;
            }
        """)

        # Main layout
        self.layout = QVBoxLayout()

        # Status label
        self.status_label = QLabel("Status: Disconnected", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #FF6347;")
        self.layout.addWidget(self.status_label)

        # Score label
        self.score_label = QLabel("Score: 0", self)
        self.score_label.setAlignment(Qt.AlignCenter)
        self.score_label.setStyleSheet("font-size: 36px; font-weight: bold; color: #C4D9FF;")
        self.layout.addWidget(self.score_label)

        # Result label
        self.result_label = QLabel("Make your choice!", self)
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #333333;")
        self.layout.addWidget(self.result_label)

        # Choice buttons
        self.choice_layout = QHBoxLayout()
        self.choice_layout.setAlignment(Qt.AlignCenter)

        self.pierre_button = QPushButton(self)
        self.pierre_button.setIcon(QIcon("icon-rock.svg"))
        self.pierre_button.setIconSize(QSize(80, 80))
        self.pierre_button.setText(" Pierre ")
        self.pierre_button.clicked.connect(lambda: self.send_choice("pierre"))
        self.choice_layout.addWidget(self.pierre_button)

        self.papier_button = QPushButton(self)
        self.papier_button.setIcon(QIcon("icon-paper.svg"))
        self.papier_button.setIconSize(QSize(80, 80))
        self.papier_button.setText(" Papier ")
        self.papier_button.clicked.connect(lambda: self.send_choice("papier"))
        self.choice_layout.addWidget(self.papier_button)

        self.ciseaux_button = QPushButton(self)
        self.ciseaux_button.setIcon(QIcon("icon-scissors.svg"))
        self.ciseaux_button.setIconSize(QSize(80, 80))
        self.ciseaux_button.setText(" Ciseaux ")
        self.ciseaux_button.clicked.connect(lambda: self.send_choice("ciseaux"))
        self.choice_layout.addWidget(self.ciseaux_button)

        self.layout.addLayout(self.choice_layout)

        # Main container
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        # Socket and connection status
        self.client_socket = None
        self.connected = False
        self.score = 0

        # Connect to the server
        self.connect_to_server()

    def connect_to_server(self):
        """Connect to the server."""
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
        """Send the player's choice to the server."""
        if self.connected:
            try:
                self.client_socket.send(choice.encode())
                self.result_label.setText(f"Waiting for the server's response...")
            except Exception as e:
                self.result_label.setText(f"Error sending choice: {str(e)}")
        else:
            QMessageBox.warning(self, "Connection Error", "Not connected to the server.")

    def receive_messages(self):
        """Receive messages from the server."""
        while self.connected:
            try:
                message = self.client_socket.recv(1024).decode()
                if "Score:" in message:
                    self.score = int(message.split("Score:")[1].strip())
                    self.score_label.setText(f"Score: {self.score}")
                else:
                    self.result_label.setText(message)
            except ConnectionError:
                self.result_label.setText("Connection lost.")
                self.connected = False
                break

    def closeEvent(self, event):
        """Close the socket when the window is closed."""
        if self.connected:
            self.client_socket.close()
        event.accept()

# Main application entry point
if __name__ == "__main__":
    app = QApplication(sys.argv)
    menu = StartMenu()
    menu.show()
    sys.exit(app.exec_())