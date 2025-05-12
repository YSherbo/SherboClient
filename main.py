from dotenv import load_dotenv
import os
import requests
import json
import base64
import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6 import QtCore, QtGui, QtWidgets

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

def get_access_token():
    authString = f"{CLIENT_ID}:{CLIENT_SECRET}"
    authBytes = authString.encode("utf-8")
    authBase64 = str(base64.b64encode(authBytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {authBase64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }
    response = requests.post(url, headers=headers, data=data)
    json_response = json.loads(response.content)
    token = json_response["access_token"]
    return token

def get_auth_header(token):
    return { "Authorization": f"Bearer {token}" }

def search_track(token, track_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={track_name}&type=track&limit=10"
    
    query_url = url + query
    response = requests.get(query_url, headers=headers)
    json_response = json.loads(response.content)
    
    if "tracks" in json_response:
        tracks = json_response["tracks"]["items"]
        for idx, track in enumerate(tracks):
            print(f"{idx + 1}. {track['name']} - {track['artists'][0]['name']}")
        return tracks
    return None

class SearchWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spotify Track Search")
        self.setGeometry(100, 100, 600, 400)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create search input
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.perform_search)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        layout.addLayout(search_layout)
        
        # Create results list
        self.results_list = QListWidget()
        layout.addWidget(self.results_list)
        
        # Get initial token
        self.token = get_access_token()

    def perform_search(self):
        query = self.search_input.text()
        if query:
            self.results_list.clear()
            tracks = search_track(self.token, query)
            if tracks:
                for track in tracks:
                    track_name = track['name']
                    artist_name = track['artists'][0]['name']
                    self.results_list.addItem(f"{track_name} - {artist_name}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SearchWindow()
    window.show()
    sys.exit(app.exec())