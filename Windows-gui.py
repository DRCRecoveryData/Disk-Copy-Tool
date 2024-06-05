import os
import sys
import time
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QLineEdit, QFileDialog, QProgressBar, QTextEdit, QMessageBox, QComboBox, QHBoxLayout
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

class DiskCopyWorker(QThread):
    progress_updated = pyqtSignal(int)
    log_updated = pyqtSignal(str)
    copy_finished = pyqtSignal(str)

    def __init__(self, selected_disk, save_directory):
        super().__init__()
        self.selected_disk = selected_disk
        self.save_directory = save_directory

    def run(self):
        try:
            self.log_updated.emit("Starting disk copy process...")

            block_size = 256 * 512  # 256 sectors * 512 bytes per sector
            disk_size = os.path.getsize(self.selected_disk)
            total_sectors = disk_size // 512

            save_file_name = os.path.basename(self.selected_disk).replace(' ', '_').replace('/', '_') + ".img"
            save_file_path = os.path.join(self.save_directory, save_file_name)

            total_read = 0
            current_sector = 0
            sectors_per_block = block_size // 512

            start_time = time.time()
            with open(self.selected_disk, 'rb') as disk_file, open(save_file_path, 'wb') as img_file:
                while True:
                    block = disk_file.read(block_size)
                    if not block:
                        break
                    img_file.write(block)
                    total_read += len(block)
                    current_sector += sectors_per_block

                    elapsed_time = time.time() - start_time
                    if elapsed_time > 0:
                        speed = total_read / elapsed_time
                        progress = (total_read / disk_size) * 100
                        remaining_seconds = (disk_size - total_read) / speed if speed > 0 else 0

                        self.progress_updated.emit(int(progress))
                        self.log_updated.emit(
                            f"Progress: {progress:.2f}% | Speed: {self.format_speed(speed)} | "
                            f"Sectors: {current_sector}/{total_sectors} | "
                            f"ETA: {self.format_time(remaining_seconds)}"
                        )

            self.copy_finished.emit(f"Disk {self.selected_disk} copied to {save_file_path} successfully.")
        except Exception as e:
            self.copy_finished.emit(f"An error occurred: {e}")

    def format_speed(self, bytes_per_second):
        """Format the speed to be human-readable."""
        units = ["B/s", "KB/s", "MB/s", "GB/s"]
        speed = bytes_per_second
        unit = units[0]
        for u in units:
            if speed < 1024:
                unit = u
                break
            speed /= 1024
        return f"{speed:.2f} {unit}"

    def format_time(self, seconds):
        """Format seconds into HH:MM:SS format."""
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

class DiskCopyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Disk Copy Tool")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.header_label = QLabel("Disk Copy Tool")
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.header_label)

        self.credit_label = QLabel("Credit: Development by DRC Lab/ Nguyen Vu Ha +84903408066 Ha Noi, Viet Nam")
        self.credit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.credit_label)

        self.disk_combo_label = QLabel("Select a physical disk to copy:")
        layout.addWidget(self.disk_combo_label)

        self.disk_combo = QComboBox()
        layout.addWidget(self.disk_combo)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_physical_disks)
        layout.addWidget(self.refresh_button)

        self.save_directory_label = QLabel("Enter the directory path to save the image file:")
        layout.addWidget(self.save_directory_label)

        self.save_directory_edit = QLineEdit()
        layout.addWidget(self.save_directory_edit)

        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_save_directory)
        layout.addWidget(self.browse_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box)

        self.copy_button = QPushButton("Copy Disk")
        self.copy_button.clicked.connect(self.copy_disk)
        layout.addWidget(self.copy_button)

        self.setLayout(layout)

        self.load_physical_disks()

    def load_physical_disks(self):
        self.disk_combo.clear()
        disks = self.list_physical_disks()
        for device_id, model in disks:
            self.disk_combo.addItem(f"{device_id} ({model})")

    def list_physical_disks(self):
        """List all physical disks available on the system."""
        physical_disks = []
        wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        service = wmi.ConnectServer(".", "root\\cimv2")
        for disk in service.ExecQuery("SELECT DeviceID, Model FROM Win32_DiskDrive"):
            physical_disks.append((disk.DeviceID, disk.Model))
        return physical_disks

    def browse_save_directory(self):
        save_directory = QFileDialog.getExistingDirectory(self, "Select Save Directory")
        if save_directory:
            self.save_directory_edit.setText(save_directory)

    def copy_disk(self):
        selected_disk_index = self.disk_combo.currentIndex()
        selected_disk_model = self.disk_combo.currentText()
        selected_disk = self.disk_combo.itemData(selected_disk_index)

        save_directory = self.save_directory_edit.text()

        if not os.path.isdir(save_directory):
            QMessageBox.critical(self, "Error", "The specified directory does not exist.")
            return

        self.worker = DiskCopyWorker(selected_disk, save_directory)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.log_updated.connect(self.update_log)
        self.worker.copy_finished.connect(self.copy_finished)
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_log(self, message):
        self.log_box.append(message)

    def copy_finished(self, message):
        QMessageBox.information(self, "Copy Finished", message)

def main():
    app = QApplication(sys.argv)
    window = DiskCopyApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

