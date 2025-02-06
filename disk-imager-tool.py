import ctypes
import os
import sys
import win32com.client
import time
import hashlib
from concurrent.futures import ThreadPoolExecutor
from colorama import init, Fore, Back, Style
import pyfiglet
import pyewf
import subprocess

# Check if the script is running as admin
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

# If not admin, relaunch the script as admin
def run_as_admin():
    if sys.version_info[0] < 3:
        executable = sys.executable.encode(sys.getfilesystemencoding())
    else:
        executable = sys.executable

    ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, ' '.join(sys.argv), None, 1)

# If not running as admin, re-launch as admin
if not is_admin():
    run_as_admin()
    sys.exit()

# Initialize colorama
init(autoreset=True)

# List all physical disks
def list_physical_disks():
    physical_disks = []
    wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
    service = wmi.ConnectServer(".", "root\\cimv2")
    for disk in service.ExecQuery("SELECT DeviceID, Model FROM Win32_DiskDrive"):
        physical_disks.append((disk.DeviceID, disk.Model))
    return physical_disks

# Get disk size
def get_disk_size(disk):
    wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
    service = wmi.ConnectServer(".", "root\\cimv2")
    for d in service.ExecQuery("SELECT Size, DeviceID FROM Win32_DiskDrive"):
        if d.DeviceID == disk:
            return int(d.Size)
    return 0

# Enable or disable write protection via registry
def set_write_protect(enable):
    reg_key = r"HKLM\SYSTEM\CurrentControlSet\Control\StorageDevicePolicies"
    reg_value = "WriteProtect"

    try:
        if enable:
            subprocess.run(['reg', 'add', reg_key, '/v', reg_value, '/t', 'REG_DWORD', '/d', '1', '/f'], check=True)
            print(Fore.GREEN + "Write protection enabled.")
        else:
            subprocess.run(['reg', 'add', reg_key, '/v', reg_value, '/t', 'REG_DWORD', '/d', '0', '/f'], check=True)
            print(Fore.GREEN + "Write protection disabled.")
    except subprocess.CalledProcessError:
        print(Fore.RED + "Error modifying the registry. Ensure you have admin privileges.")

# Check current write protection status
def check_write_protection():
    reg_key = r"HKLM\SYSTEM\CurrentControlSet\Control\StorageDevicePolicies"
    reg_value = "WriteProtect"
    try:
        output = subprocess.check_output(['reg', 'query', reg_key, '/v', reg_value], stderr=subprocess.PIPE)
        if b'1' in output:
            print(Fore.GREEN + "Write protection is enabled.")
        else:
            print(Fore.RED + "Write protection is disabled.")
    except subprocess.CalledProcessError:
        print(Fore.RED + "Write protection registry key not found.")

# Calculate hash of the drive
def get_drive_hash(disk):
    hash_md5 = hashlib.md5()
    hash_sha1 = hashlib.sha1()
    hash_sha256 = hashlib.sha256()

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

    buffer = ctypes.create_string_buffer(4096)
    bytes_read = ctypes.c_ulong(0)

    while ctypes.windll.kernel32.ReadFile(handle, buffer, len(buffer), ctypes.byref(bytes_read), None):
        if bytes_read.value == 0:
            break
        data = buffer.raw[:bytes_read.value]
        hash_md5.update(data)
        hash_sha1.update(data)
        hash_sha256.update(data)

    ctypes.windll.kernel32.CloseHandle(handle)

    return hash_md5.hexdigest(), hash_sha1.hexdigest(), hash_sha256.hexdigest()

# Copy block from physical disk
def read_physical_disk(disk, block_size, offset):
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

    offset_high = ctypes.c_long(offset >> 32)
    offset_low = ctypes.c_long(offset & 0xFFFFFFFF)
    result = ctypes.windll.kernel32.SetFilePointerEx(handle, offset_low, ctypes.byref(offset_high), 0)
    if not result:
        ctypes.windll.kernel32.CloseHandle(handle)
        raise Exception(f"Failed to set file pointer for disk {disk}")

    read_buffer = ctypes.create_string_buffer(block_size)
    read = ctypes.c_ulong(0)

    success = ctypes.windll.kernel32.ReadFile(
        handle,
        read_buffer,
        block_size,
        ctypes.byref(read),
        None
    )

    ctypes.windll.kernel32.CloseHandle(handle)

    if not success or read.value == 0:
        return None, 0

    return read_buffer.raw[:read.value], read.value

# Format speed in human-readable format
def format_speed(bytes_per_second):
    units = ["B/s", "KB/s", "MB/s", "GB/s"]
    speed = bytes_per_second
    unit = units[0]
    for u in units:
        if speed < 1024:
            unit = u
            break
        speed /= 1024
    return f"{speed:.2f} {unit}"

# Format time in HH:MM:SS format
def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

# Main process
def main():
    # ASCII art header
    header = pyfiglet.figlet_format("Disk Copy Tool")
    print(Fore.YELLOW + header)

    # Show credit line
    print(Fore.CYAN + "Credit: Development by DRC Lab/ Nguyen Vu Ha +84903408066 Ha Noi, Viet Nam")

    # List all physical disks
    disks = list_physical_disks()
    if not disks:
        print(Fore.RED + "No physical disks found.")
        return

    # Display the list of disks to the user
    print(Fore.CYAN + "\nSelect a physical disk to copy:")
    for idx, (device_id, model) in enumerate(disks):
        print(f"{Fore.GREEN}{idx + 1}: {device_id} ({model})")

    # Get the user's choice
    choice = int(input(Fore.YELLOW + "Enter the number of the disk: ")) - 1
    if choice < 0 or choice >= len(disks):
        print(Fore.RED + "Invalid choice.")
        return

    selected_disk, disk_model = disks[choice]

    # Calculate hash of the original drive
    original_hashes = get_drive_hash(selected_disk)
    print(Fore.CYAN + "Original Drive Hashes:")
    print(f"MD5: {original_hashes[0]}")
    print(f"SHA1: {original_hashes[1]}")
    print(f"SHA256: {original_hashes[2]}")

    # Enable/Disable write protection
    write_protect = input(Fore.YELLOW + "Enable write protection? (Y/N): ").strip().lower()
    if write_protect == 'y':
        set_write_protect(True)
    else:
        set_write_protect(False)

    # Check write protection status
    check_write_protection()

    # Prompt for the directory path to save the image file
    directory_path = input(Fore.YELLOW + "Enter the directory path to save the image file: ")

    # Ensure the directory exists
    if not os.path.isdir(directory_path):
        print(Fore.RED + "The specified directory does not exist.")
        return

    # Choose the image format (E01 or DD)
    image_format = input(Fore.YELLOW + "Choose the output format (E01/DD): ").strip().lower()

    save_file_name = f"{disk_model.replace(' ', '_').replace('/', '_')}.{image_format}"
    save_file_path = os.path.join(directory_path, save_file_name)

    block_size = 8 * 1024 * 1024  # 8 MB blocks

    # Get the disk size
    disk_size = get_disk_size(selected_disk)
    if disk_size == 0:
        print(Fore.RED + "Unable to determine the disk size.")
        return

    total_sectors = disk_size // 512

    def copy_block(offset):
        return read_physical_disk(selected_disk, block_size, offset)

    # Create the image file
    try:
        with open(save_file_path, 'wb') as img_file:
            start_time = time.time()
            total_read = 0

            with ThreadPoolExecutor() as executor:
                for offset in range(0, total_sectors * 512, block_size):
                    block_data, bytes_read = copy_block(offset)
                    if block_data is None:
                        continue
                    img_file.write(block_data)
                    total_read += bytes_read

            end_time = time.time()
            total_time = end_time - start_time

            # Calculate the hashing for the image created
            created_hashes = get_drive_hash(save_file_path)
            print(Fore.CYAN + "Image File Hashes:")
            print(f"MD5: {created_hashes[0]}")
            print(f"SHA1: {created_hashes[1]}")
            print(f"SHA256: {created_hashes[2]}")

            print(Fore.GREEN + f"Disk image created: {save_file_path}")
            print(Fore.CYAN + f"Time taken: {format_time(total_time)}")
            print(Fore.CYAN + f"Data copied: {format_speed(total_read / total_time)}")

    except Exception as e:
        print(Fore.RED + f"Error: {e}")

if __name__ == "__main__":
    main()