import sys
import os
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QFileDialog, QHBoxLayout, QProgressBar
from pytube import YouTube

class DownloadThread(QThread):
    progress_updated = pyqtSignal(int)

    def __init__(self, url, destination):
        super().__init__()
        self.url = url
        self.destination = destination
        self.stream = None  # Initialize stream attribute
        self.filesize = 0  # Initialize total file size

    def run(self):
        try:
            yt = YouTube(self.url)
            self.stream = yt.streams.get_highest_resolution()
            filename = self.stream.default_filename
            file_path = os.path.join(self.destination, filename)
            self.filesize = self.stream.filesize
            print("File size:", self.filesize)
            self.progress_updated.emit(0)  # Start progress at 0%
            self.stream.download(output_path=self.destination, filename=filename, max_retries=10)
            self.progress_updated.emit(100)  # Set progress to 100% when download completes
            print("Downloaded file size:", os.path.getsize(file_path))
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def update_progress(self):
        try:
            if self.stream is not None:
                filename = os.path.join(self.destination, self.stream.default_filename)
                downloaded = os.path.getsize(filename)
                if self.filesize > 0:
                    progress = int((downloaded / self.filesize) * 100)
                    print("Progress:", progress)
                    self.progress_updated.emit(progress)
        except Exception as e:
            print(f"Error updating progress: {str(e)}")

class YouTubeDownloader(QMainWindow):
    def __init__(self):
        super().__init__(flags=Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        self.setWindowTitle("YouTube Video Downloader")
        self.setGeometry(100, 100, 600, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignCenter)

        self.url_label = QLabel("Enter YouTube URL:")
        layout.addWidget(self.url_label)

        self.url_entry = QLineEdit()
        self.url_entry.setMaximumWidth(300)
        layout.addWidget(self.url_entry)

        destination_section_layout = QVBoxLayout()
        self.destination_label = QLabel("Select destination:")
        destination_section_layout.addWidget(self.destination_label)

        self.destination_entry = QLineEdit()
        self.destination_entry.setMaximumWidth(300)
        self.destination_entry.setReadOnly(True)
        self.destination_entry.setText(os.getcwd())
        destination_section_layout.addWidget(self.destination_entry)

        destination_button_layout = QHBoxLayout()
        self.browse_button = QPushButton("Save Here")
        self.browse_button.setMaximumWidth(100)
        self.browse_button.clicked.connect(self.browse_destination)
        destination_button_layout.addWidget(self.browse_button)

        destination_section_layout.addLayout(destination_button_layout)
        layout.addLayout(destination_section_layout)

        

        download_button_layout = QHBoxLayout()
        self.download_button = QPushButton("Download")
        self.download_button.setMaximumWidth(100)
        self.download_button.setStyleSheet("background-color: green;")
        self.download_button.clicked.connect(self.download_video)
        download_button_layout.addWidget(self.download_button)
        layout.addLayout(download_button_layout)


        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        self.progress_bar.hide()
        
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

    def download_video(self):
        url = self.url_entry.text()
        destination = self.destination_entry.text()
        if not destination:
            destination = os.getcwd()

        # Create and start the download thread
        self.download_thread = DownloadThread(url, destination)
        self.download_thread.progress_updated.connect(self.update_progress)
        self.download_thread.start()

        # Start timer to update progress every 2 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.download_thread.update_progress)
        self.timer.start(2000)

        # Show progress bar
        self.progress_bar.show()
        self.progress_bar.setValue(0)

    def update_progress(self, progress):
        print("Progress:", progress)
        self.progress_bar.setValue(progress)
        # if progress == 100:
        #     self.progress_bar.hide()  # Hide progress bar when download is complete
            

    def browse_destination(self):
        destination = QFileDialog.getExistingDirectory(self, "Select destination")
        if destination:
            self.destination_entry.setText(destination)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YouTubeDownloader()
    window.show()
    sys.exit(app.exec_())
