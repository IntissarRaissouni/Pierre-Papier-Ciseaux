from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QMessageBox, QHBoxLayout,
)
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtCore import Qt
import socket
import threading
from PyQt5.QtCore import QSize


class GameClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pierre-Papier-Ciseaux")
        self.setGeometry(100, 100, 600, 400)

        # Police et couleurs
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QLabel {
                font-size: 16px;
                font-family: Arial;
            }
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                color: white;
                background-color: #4CAF50;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3e8e41;
            }
        """)

        self.layout = QVBoxLayout()

        # Titre et état de connexion
        self.status_label = QLabel("Status: Disconnected", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: red; font-size: 18px; font-weight: bold;")
        self.layout.addWidget(self.status_label)

        self.result_label = QLabel("Bienvenue dans Pierre-Papier-Ciseaux!", self)
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        self.layout.addWidget(self.result_label)

        # Ajout des boutons pour les choix
        self.choice_layout = QHBoxLayout()

        self.pierre_button = QPushButton(self)
        self.pierre_button.setIcon(QIcon("icon-rock.svg"))
        self.pierre_button.setIconSize(QSize(50, 50))
        self.pierre_button.setText(" Pierre ")
        self.pierre_button.clicked.connect(lambda: self.send_choice("pierre"))
        self.choice_layout.addWidget(self.pierre_button)

        self.papier_button = QPushButton(self)
        self.papier_button.setIcon(QIcon("icon-spock.svg"))
        self.papier_button.setIconSize(QSize(50, 50))
        self.papier_button.setText(" Papier ")
        self.papier_button.clicked.connect(lambda: self.send_choice("papier"))
        self.choice_layout.addWidget(self.papier_button)

        self.ciseaux_button = QPushButton(self)
        self.ciseaux_button.setIcon(QIcon("icon-scissors.svg"))
        self.ciseaux_button.setIconSize(QSize(50, 50))
        self.ciseaux_button.setText(" Ciseaux ")
        self.ciseaux_button.clicked.connect(lambda: self.send_choice("ciseaux"))
        self.choice_layout.addWidget(self.ciseaux_button)

        self.layout.addLayout(self.choice_layout)

        # Conteneur principal
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        self.client_socket = None
        self.connected = False

        # Connexion au serveur
        self.connect_to_server()

    def connect_to_server(self):
        """Établir une connexion au serveur."""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(("127.0.0.1", 5555))  # Modifier selon l'adresse et le port du serveur
            self.connected = True
            self.status_label.setText("Status: Connected")
            self.status_label.setStyleSheet("color: green; font-size: 18px; font-weight: bold;")

            # Démarrer un thread pour écouter les messages du serveur
            threading.Thread(target=self.receive_messages, daemon=True).start()

        except ConnectionError:
            self.status_label.setText("Status: Failed to Connect")
            self.status_label.setStyleSheet("color: red; font-size: 18px; font-weight: bold;")
            self.connected = False

    def send_choice(self, choice):
        """Envoyer le choix du joueur au serveur."""
        if self.connected:
            try:
                self.client_socket.send(choice.encode())
                self.result_label.setText(f"En attente de la réponse du serveur...")
            except Exception as e:
                self.result_label.setText(f"Erreur lors de l'envoi : {str(e)}")
        else:
            QMessageBox.warning(self, "Erreur de Connexion", "Non connecté au serveur.")

    def receive_messages(self):
        """Recevoir des messages du serveur."""
        while self.connected:
            try:
                message = self.client_socket.recv(1024).decode()
                self.result_label.setText(message)
            except ConnectionError:
                self.result_label.setText("Connexion perdue.")
                self.connected = False
                break

    def closeEvent(self, event):
        """Fermer le socket lors de la fermeture de l'application."""
        if self.connected:
            self.client_socket.close()
        event.accept()


from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QMessageBox, QHBoxLayout,
)
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtCore import Qt
import socket
import threading
from PyQt5.QtCore import QSize


class StartMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pierre-Papier-Ciseaux - Menu")
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()

        # Title Label
        self.title_label = QLabel("Pierre-Papier-Ciseaux", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        self.layout.addWidget(self.title_label)

        # Image Label
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)

        # Load the image
        pixmap = QPixmap("rock-paper-scissors-game-rules.png")
        if not pixmap.isNull():
            # Scale the image to fit within the window
            scaled_pixmap = pixmap.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
        else:
            self.image_label.setText("Image not found!")

        self.layout.addWidget(self.image_label)

        # Start Game Button
        self.start_button = QPushButton("Start Game", self)
        self.start_button.clicked.connect(self.start_game)
        self.layout.addWidget(self.start_button)

        # Quit Button
        self.quit_button = QPushButton("Quit", self)
        self.quit_button.clicked.connect(self.close)
        self.layout.addWidget(self.quit_button)

        # Main Container
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def start_game(self):
        """Open the GameClient window and close the StartMenu."""
        self.game_client = GameClient()
        self.game_client.show()
        self.close()

if __name__ == "__main__":
    app = QApplication([])
    menu = StartMenu()  # Create the StartMenu instance
    menu.show()         # Show the StartMenu
    app.exec_()
