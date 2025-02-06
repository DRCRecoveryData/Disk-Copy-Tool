import ctypes
import os
import sys
import win32com.client
import time
import hashlib
import winreg  # For interacting with Windows registry
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

# Modify the registry to enable or disable write protection
def set_write_protection(enable):
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\StorageDevicePolicies", 0, winreg.KEY_SET_VALUE)
        if enable:
            winreg.SetValueEx(reg_key, "WriteProtect", 0, winreg.REG_DWORD, 1)  # Enable write protection
            print(Fore.GREEN + "Write protection enabled.")
        else:
            winreg.SetValueEx(reg_key, "WriteProtect", 0, winreg.REG_DWORD, 0)  # Disable write protection
            print(Fore.GREEN + "Write protection disabled.")
        winreg.CloseKey(reg_key)
    except Exception as e:
        print(Fore.RED + f"Error modifying registry: {e}")

# Check the current write protection status
def check_write_protection():
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\StorageDevicePolicies", 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(reg_key, "WriteProtect")
        winreg.CloseKey(reg_key)
        if value == 1:
            print(Fore.CYAN + "Write protection is currently enabled.")
        else:
            print(Fore.CYAN + "Write protection is currently disabled.")
    except Exception as e:
        print(Fore.RED + f"Error checking registry: {e}")

# Main process
def main():
    # ASCII art header
    header = pyfiglet.figlet_format("Disk Copy Tool")
    print(Fore.YELLOW + header)

    # Show credit line
    print(Fore.CYAN + "Credit: Development by DRC Lab/ Nguyen Vu Ha +84903408066 Ha Noi, Viet Nam")

    # Ask for write protection setting
    print(Fore.YELLOW + "Do you want to enable or disable write protection?")
    user_choice = input("Enter 'enable' to enable write protection, 'disable' to disable it, or 'check' to check current status: ").strip().lower()
    
    if user_choice == "enable":
        set_write_protection(True)
    elif user_choice == "disable":
        set_write_protection(False)
    elif user_choice == "check":
        check_write_protection()
    else:
        print(Fore.RED + "Invalid choice. Please enter 'enable', 'disable', or 'check'.")
        return

    # Proceed with the disk imaging process
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
                futures = {executor.submit(copy_block, offset): offset for offset in range(0, disk_size, block_size)}
                for future in futures:
                    block, read_size = future.result()
                    if block is not None:
                        img_file.write(block)
                        total_read += read_size
                    current_time = time.time()
                    elapsed_time = current_time - start_time
                    if elapsed_time > 0:
                        speed = total_read / elapsed_time
                        progress = (total_read / disk_size) * 100
                        remaining_seconds = (disk_size - total_read) / speed if speed > 0 else 0
                        print(f"\r{Fore.CYAN}Progress: {progress:.2f}% | Speed: {format_speed(speed)} | "
                              f"Sectors: {total_read // 512}/{total_sectors} | "
                              f"ETA: {format_time(remaining_seconds)}", end='')

        print(Fore.GREEN + f"\nDisk {selected_disk} copied to {save_file_path} successfully.")

        # After imaging, hash the copied image file
        print(Fore.CYAN + "Hashed Image File:")
        with open(save_file_path, 'rb') as img_file:
            img_hash_md5 = hashlib.md5()
            img_hash_sha1 = hashlib.sha1()
            img_hash_sha256 = hashlib.sha256()

            while chunk := img_file.read(4096):
                img_hash_md5.update(chunk)
                img_hash_sha1.update(chunk)
                img_hash_sha256.update(chunk)

            print(f"MD5: {img_hash_md5.hexdigest()}")
            print(f"SHA1: {img_hash_sha1.hexdigest()}")
            print(f"SHA256: {img_hash_sha256.hexdigest()}")

        # Compare the hashes
        if original_hashes == (img_hash_md5.hexdigest(), img_hash_sha1.hexdigest(), img_hash_sha256.hexdigest()):
            print(Fore.GREEN + "Hashes match! The disk image is verified successfully.")
        else:
            print(Fore.RED + "Hashes do not match. The image is corrupted.")
    except Exception as e:
        print(Fore.RED + f"An error occurred: {e}")

if __name__ == "__main__":
    main()