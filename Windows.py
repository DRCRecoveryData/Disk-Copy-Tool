import ctypes
import os
import win32com.client
import time
from concurrent.futures import ThreadPoolExecutor
from colorama import init, Fore, Back, Style
import pyfiglet

# Initialize colorama
init(autoreset=True)

def list_physical_disks():
    """List all physical disks available on the system."""
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

def read_physical_disk(disk, block_size, offset):
    """Read a block of specified size from the physical disk at the given offset."""
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

    # Move the file pointer to the correct position
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

    ctypes.windll.kernel32.CloseHandle(handle)

    if not success or read.value == 0:
        return None, 0

    return read_buffer.raw[:read.value], read.value

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

    # Prompt for the directory path to save the image file
    directory_path = input(Fore.YELLOW + "Enter the directory path to save the image file: ")

    # Ensure the directory exists
    if not os.path.isdir(directory_path):
        print(Fore.RED + "The specified directory does not exist.")
        return

    # Create the full save file path with the disk model as the file name
    save_file_name = f"{disk_model.replace(' ', '_').replace('/', '_')}.img"
    save_file_path = os.path.join(directory_path, save_file_name)

    block_size = 256 * 512  # 256 sectors * 512 bytes per sector

    # Get the disk size
    disk_size = get_disk_size(selected_disk)
    if disk_size == 0:
        print(Fore.RED + "Unable to determine the disk size.")
        return

    total_sectors = disk_size // 512

    def copy_block(offset):
        return read_physical_disk(selected_disk, block_size, offset)

    # Copy the disk to the image file
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
    except Exception as e:
        print(Fore.RED + f"An error occurred: {e}")

if __name__ == "__main__":
    main()
