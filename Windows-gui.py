import sys
import os
import ctypes
import time
import win32com.client
from concurrent.futures import ThreadPoolExecutor
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit,
                             QFileDialog, QProgressBar, QTextEdit, QMessageBox, QComboBox, QHBoxLayout)
from PyQt6.QtCore import QThread, pyqtSignal


class FileRepairWorker(QThread):
    progress_updated = pyqtSignal(int)
    log_updated = pyqtSignal(str)
    repair_finished = pyqtSignal(str)
    paused_changed = pyqtSignal(bool)

    def __init__(self, reference_disk, save_file_path, block_size):
        super().__init__()
        self.reference_disk = reference_disk
        self.save_file_path = save_file_path
        self.block_size = block_size
        self.paused = False
        self.stop_requested = False

    def run(self):
        try:
            self.log_updated.emit("Starting disk copy process...")

            disk_size = get_disk_size(self.reference_disk)
            if disk_size == 0:
                raise Exception("Unable to determine the disk size.")
            total_sectors = disk_size // 512

            total_read = 0
            sectors_per_block = self.block_size // 512

            start_time = time.time()
            with open(self.save_file_path, 'wb') as img_file, ThreadPoolExecutor(max_workers=4) as executor:
                futures = {executor.submit(read_physical_disk, self.reference_disk, offset, self.block_size): offset for offset in range(0, disk_size, self.block_size)}

                for future in futures:
                    if self.stop_requested:
                        self.log_updated.emit("Disk copy process stopped.")
                        break

                    while self.paused:
                        time.sleep(1)
                        if self.stop_requested:
                            break

                    if self.stop_requested:
                        break

                    result = future.result()
                    if result:
                        block, read_size, current_sector = result
                        img_file.write(block)
                        total_read += read_size

                        progress = (total_read / disk_size) * 100
                        elapsed_time = time.time() - start_time
                        speed = total_read / elapsed_time if elapsed_time > 0 else 0
                        remaining_time = (disk_size - total_read) / speed if speed > 0 else 0

                        self.progress_updated.emit(int(progress))
                        self.log_updated.emit(
                            f"Progress: {progress:.2f}% | Speed: {format_speed(speed)} | "
                            f"Sectors: {current_sector}/{total_sectors} | ETA: {format_time(remaining_time)}"
                        )

            if not self.stop_requested:
                self.repair_finished.emit("Disk copy process completed successfully.")
        except Exception as e:
            self.repair_finished.emit(f"An error occurred: {e}")

    def toggle_pause(self):
        self.paused = not self.paused
        self.paused_changed.emit(self.paused)

    def request_stop(self):
        self.stop_requested = True


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
        self.refresh_button.clicked.connect(self.load_physical_disks)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.refresh_button)

        reference_layout = QHBoxLayout()
        reference_layout.addWidget(self.reference_disk_combo)
        reference_layout.addWidget(self.refresh_button)

        self.save_label = QLabel("Save Directory:")
        self.save_directory_edit = QLineEdit()
        self.save_directory_browse_button = QPushButton("Browse", self)
        self.save_directory_browse_button.setObjectName("browseButton")
        self.save_directory_browse_button.clicked.connect(self.browse_save_directory)

        self.block_size_label = QLabel("Block Size (sectors):")
        self.block_size_combo = QComboBox()
        self.block_size_combo.addItems(["1", "2", "4", "8", "16", "32", "64", "128", "256"])

        button_layout.addWidget(self.block_size_label)
        button_layout.addWidget(self.block_size_combo)

        self.pause_button = QPushButton("Pause")
        self.pause_button.setObjectName("pauseButton")
        self.pause_button.clicked.connect(self.toggle_pause)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setObjectName("stopButton")
        self.stop_button.clicked.connect(self.stop_copy)

        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.stop_button)

        layout.addWidget(self.reference_label)
        layout.addLayout(reference_layout)
        layout.addWidget(self.save_label)
        layout.addWidget(self.save_directory_edit)
        layout.addWidget(self.save_directory_browse_button)
        layout.addLayout(button_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)

        layout.addWidget(self.progress_bar)
        layout.addWidget(self.log_box)

        self.repair_button = QPushButton("Copy Disk", self)
        self.repair_button.setObjectName("blueButton")
        self.repair_button.clicked.connect(self.copy_disk)
        layout.addWidget(self.repair_button)

        self.setLayout(layout)

        self.setStyleSheet("""
        #browseButton, #blueButton, #refreshButton, #pauseButton, #stopButton {
            background-color: #3498db;
            border: none;
            color: white;
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 4px;
        }
        #browseButton:hover, #blueButton:hover, #refreshButton:hover, #pauseButton:hover, #stopButton:hover {
            background-color: #2980b9;
        }
        #refreshButton, #pauseButton, #stopButton {
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
        for device_id, model in disks:
            self.reference_disk_combo.addItem(f"{device_id} ({model})", device_id)

    def browse_save_directory(self):
        save_directory = QFileDialog.getExistingDirectory(self, "Select Save Directory")
        if save_directory:
            self.save_directory_edit.setText(save_directory)

    def copy_disk(self):
        reference_disk_index = self.reference_disk_combo.currentIndex()
        reference_disk = self.reference_disk_combo.itemData(reference_disk_index)
        combo_text = self.reference_disk_combo.currentText()

        start_index = combo_text.find('(')
        end_index = combo_text.rfind(')')
        if start_index != -1 and end_index != -1:
            model = combo_text[start_index + 1:end_index].strip()
        else:
            model = "UnknownModel"

        invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
        for char in invalid_chars:
            model = model.replace(char, '_')

        model = model.replace(' ', '_')

        save_directory = self.save_directory_edit.text()
        block_size_sectors = int(self.block_size_combo.currentText())
        block_size = block_size_sectors * 512

        if not reference_disk:
            self.show_message("Error", "No reference disk selected.")
            return
        if not os.path.exists(save_directory):
            self.show_message("Error", "Save directory does not exist.")
            return

        save_file_name = f"_{model}.img"
        save_file_path = os.path.join(save_directory, save_file_name)

        self.worker = FileRepairWorker(reference_disk, save_file_path, block_size)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.log_updated.connect(self.update_log)
        self.worker.repair_finished.connect(self.repair_finished)
        self.worker.paused_changed.connect(self.update_pause_button)
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_log(self, message):
        self.log_box.append(message)

    def repair_finished(self, message):
        self.show_message("Success", message)

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)

    def toggle_pause(self):
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.toggle_pause()
            self.update_pause_button(self.worker.paused)

    def stop_copy(self):
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.request_stop()
            self.show_message("Stopped", "Copying process stopped.")

    def update_pause_button(self, paused):
        if paused:
            self.pause_button.setText("Resume")
        else:
            self.pause_button.setText("Pause")


def list_physical_disks():
    physical_disks = []
    wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
    service = wmi.ConnectServer(".", "root\\cimv2")
    for disk in service.ExecQuery("SELECT DeviceID, Model FROM Win32_DiskDrive"):
        physical_disks.append((disk.DeviceID, disk.Model))
    return physical_disks


def get_disk_size(disk):
    """Get the size of the physical disk in bytes."""
    wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
    service = wmi.ConnectServer(".", "root\\cimv2")
    for d in service.ExecQuery("SELECT Size, DeviceID FROM Win32_DiskDrive"):
        if d.DeviceID == disk:
            return int(d.Size)
    return 0


def read_physical_disk(disk, offset, block_size):
    """Read the physical disk in blocks of specified size."""
    handle = ctypes.windll.kernel32.CreateFileW(
        f"\\\\.\\{disk}",
        0x80000000,  # GENERIC_READ
        0x00000001 | 0x00000002,  # FILE_SHARE_READ | FILE_SHARE_WRITE
        None,
        0x00000003,  # OPEN_EXISTING
        0,
        None
    )

    if handle == ctypes.c_void_p(-1).value:
        raise Exception(f"Failed to open disk {disk}")

    try:
        ctypes.windll.kernel32.SetFilePointer(handle, offset, None, 0)
        read_buffer = ctypes.create_string_buffer(block_size)
        read = ctypes.c_ulong(0)
        
        success = ctypes.windll.kernel32.ReadFile(
            handle,
            read_buffer,
            block_size,
            ctypes.byref(read),
            None
        )

        if not success:
            raise Exception(f"Failed to read from disk {disk} at offset {offset}")

        return read_buffer.raw[:read.value], read.value, offset // 512

    finally:
        ctypes.windll.kernel32.CloseHandle(handle)


def format_speed(bytes_per_second):
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

