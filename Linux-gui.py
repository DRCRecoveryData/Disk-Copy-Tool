import sys
import os
import psutil
import time
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, 
                             QFileDialog, QProgressBar, QTextEdit, QMessageBox, QComboBox, QHBoxLayout)
from PyQt6.QtCore import QThread, pyqtSignal

class FileRepairWorker(QThread):
    progress_updated = pyqtSignal(int)
    log_updated = pyqtSignal(str)
    repair_finished = pyqtSignal(str)

    def __init__(self, reference_disk, save_directory):
        super().__init__()
        self.reference_disk = reference_disk
        self.save_directory = save_directory

    def run(self):
        try:
            self.log_updated.emit("Starting disk copy process...")

            block_size = 256 * 512  # 256 sectors * 512 bytes per sector
            disk_size = get_disk_size(self.reference_disk)
            if disk_size == 0:
                raise Exception("Unable to determine the disk size.")
            total_sectors = disk_size // 512

            save_file_name = f"{os.path.basename(self.reference_disk).replace('/', '_')}.img"
            save_file_path = os.path.join(self.save_directory, save_file_name)

            total_read = 0
            sectors_per_block = block_size // 512

            start_time = time.time()
            with open(self.reference_disk, 'rb') as disk_file, open(save_file_path, 'wb') as img_file:
                while True:
                    block = disk_file.read(block_size)
                    if not block:
                        break
                    img_file.write(block)
                    total_read += len(block)
                    progress = (total_read / disk_size) * 100
                    elapsed_time = time.time() - start_time
                    speed = total_read / elapsed_time if elapsed_time > 0 else 0
                    remaining_time = (disk_size - total_read) / speed if speed > 0 else 0

                    self.progress_updated.emit(int(progress))
                    self.log_updated.emit(
                        f"Progress: {progress:.2f}% | Speed: {format_speed(speed)} | "
                        f"Read: {total_read} bytes | ETA: {format_time(remaining_time)}"
                    )

            self.repair_finished.emit("Disk copy process completed successfully.")
        except Exception as e:
            self.repair_finished.emit(f"An error occurred: {e}")

class FileRepairApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Disk Copy Tool")
        self.setGeometry(100, 100, 400, 400)

        layout = QVBoxLayout()

        self.reference_label = QLabel("Reference Disk:")
        self.reference_disk_combo = QComboBox()
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setObjectName("refreshButton")
        self.refresh_button.setFixedSize(100, 25)
        self.refresh_button.clicked.connect(self.load_physical_disks)

        reference_layout = QHBoxLayout()
        reference_layout.addWidget(self.reference_disk_combo)
        reference_layout.addWidget(self.refresh_button)

        self.save_directory_label = QLabel("Save Directory:")
        self.save_directory_edit = QLineEdit()
        self.save_directory_browse_button = QPushButton("Browse", self)
        self.save_directory_browse_button.setObjectName("browseButton")
        self.save_directory_browse_button.clicked.connect(self.browse_save_directory)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)

        self.copy_button = QPushButton("Copy Disk", self)
        self.copy_button.setObjectName("blueButton")
        self.copy_button.clicked.connect(self.copy_disk)

        layout.addWidget(self.reference_label)
        layout.addLayout(reference_layout)
        layout.addWidget(self.save_directory_label)
        layout.addWidget(self.save_directory_edit)
        layout.addWidget(self.save_directory_browse_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.log_box)
        layout.addWidget(self.copy_button)

        self.setLayout(layout)

        self.setStyleSheet("""
        #browseButton, #blueButton, #refreshButton {
            background-color: #3498db;
            border: none;
            color: white;
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 4px;
        }
        #browseButton:hover, #blueButton:hover, #refreshButton:hover {
            background-color: #2980b9;
        }
        #refreshButton {
            padding: 5px 10px;
            font-size: 14px;
        }
        """)

        self.load_physical_disks()

    def load_physical_disks(self):
        self.reference_disk_combo.clear()
        disks = list_physical_disks()
        if not disks:
            QMessageBox.critical(self, "Error", "No physical disks found.")
            return
        self.reference_disk_combo.addItems(disks)

    def browse_save_directory(self):
        save_directory = QFileDialog.getExistingDirectory(self, "Select Save Directory")
        if save_directory:
            self.save_directory_edit.setText(save_directory)

    def copy_disk(self):
        reference_disk = self.reference_disk_combo.currentText()
        save_directory = self.save_directory_edit.text()

        if not reference_disk:
            self.show_message("Error", "No reference disk selected.")
            return
        if not os.path.exists(save_directory):
            self.show_message("Error", "Save directory does not exist.")
            return

        self.worker = FileRepairWorker(reference_disk, save_directory)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.log_updated.connect(self.update_log)
        self.worker.repair_finished.connect(self.repair_finished)
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_log(self, message):
        self.log_box.append(message)

    def repair_finished(self, message):
        self.show_message("Success", message)

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)

def list_physical_disks():
    """List all physical disks available on the system."""
    physical_disks = []
    for disk in psutil.disk_partitions(all=False):
        if disk.device.startswith('/dev/sd') or disk.device.startswith('/dev/nvme') or disk.device.startswith('/dev/mmcblk'):
            physical_disks.append(disk.device)
    return physical_disks

def get_disk_size(disk):
    """Get the size of the physical disk in bytes."""
    try:
        with open(disk, 'rb') as f:
            f.seek(0, os.SEEK_END)
            return f.tell()
    except Exception as e:
        print(f"Error determining disk size: {e}")
        return 0

def format_speed(bytes_per_second):
    """Format the speed to be human-readable."""
    units = ["B/s", "KB/s", "MB/s", "GB/s"]
    speed = bytes_per_second
    for unit in units:
        if speed < 1024:
            break
        speed /= 1024
    return f"{speed:.2f} {unit}"

def format_time(seconds):
    """Format seconds into HH:MM:SS format."""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FileRepairApp()
    window.show()
    sys.exit(app.exec())
