import os
import time
import psutil
import pyfiglet
from colorama import init, Fore

# Initialize colorama
init(autoreset=True)

def list_physical_disks():
    """List all physical disks available on the system."""
    physical_disks = []
    for disk in psutil.disk_partitions(all=False):
        if disk.device.startswith('/dev/sd') or disk.device.startswith('/dev/nvme'):
            physical_disks.append(disk.device)
    return physical_disks


def get_disk_size(disk):
    """Get the size of the physical disk in bytes."""
    disk_usage = psutil.disk_usage(disk)
    return disk_usage.total

def read_physical_disk(disk, block_size):
    """Read the physical disk in blocks of specified size."""
    try:
        with open(disk, 'rb') as disk_file:
            while True:
                block = disk_file.read(block_size)
                if not block:
                    break
                yield block
    except Exception as e:
        raise Exception(f"Failed to read disk {disk}: {e}")

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
    for idx, device in enumerate(disks):
        print(f"{Fore.GREEN}{idx + 1}: {device}")

    # Get the user's choice
    choice = int(input(Fore.YELLOW + "Enter the number of the disk: ")) - 1
    if choice < 0 or choice >= len(disks):
        print(Fore.RED + "Invalid choice.")
        return

    selected_disk = disks[choice]

    # Prompt for the directory path to save the image file
    directory_path = input(Fore.YELLOW + "Enter the directory path to save the image file: ")

    # Ensure the directory exists
    if not os.path.isdir(directory_path):
        print(Fore.RED + "The specified directory does not exist.")
        return

    # Create the full save file path with the disk model as the file name
    save_file_name = f"{os.path.basename(selected_disk).replace('/', '_')}.img"
    save_file_path = os.path.join(directory_path, save_file_name)

    block_size = 256 * 512  # 256 sectors * 512 bytes per sector

    # Get the disk size
    disk_size = get_disk_size(selected_disk)
    if disk_size == 0:
        print(Fore.RED + "Unable to determine the disk size.")
        return

    total_sectors = disk_size // 512

    # Copy the disk to the image file
    try:
        with open(save_file_path, 'wb') as img_file:
            start_time = time.time()
            total_read = 0
            current_sector = 0
            sectors_per_block = block_size // 512

            for block in read_physical_disk(selected_disk, block_size):
                img_file.write(block)
                total_read += len(block)
                current_sector += sectors_per_block

                current_time = time.time()
                elapsed_time = current_time - start_time
                if elapsed_time > 0:
                    speed = total_read / elapsed_time
                    progress = (total_read / disk_size) * 100
                    remaining_seconds = (disk_size - total_read) / speed if speed > 0 else 0
                    print(f"\r{Fore.CYAN}Progress: {progress:.2f}% | Speed: {format_speed(speed)} | "
                          f"Sectors: {current_sector}/{total_sectors} | "
                          f"ETA: {format_time(remaining_seconds)}", end='')
        print(Fore.GREEN + f"\nDisk {selected_disk} copied to {save_file_path} successfully.")
    except Exception as e:
        print(Fore.RED + f"An error occurred: {e}")

if __name__ == "__main__":
    main()
