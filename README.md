# Disk Copy Tool

Disk Copy Tool is a Python script designed to copy the contents of a physical disk to an image file. It supports both Windows and Linux operating systems.

## Features

- Lists available physical disks on the system.
- Copies the selected disk to an image file.
- Displays progress, speed, sectors read, and estimated time remaining during the copying process.

## Requirements

### Windows

- Python 3.x
- Libraries: `ctypes`, `os`, `win32com.client`, `time`, `colorama`, `pyfiglet`

### Linux

- Python 3.x
- Libraries: `os`, `time`, `psutil`, `pyfiglet`, `colorama`

## Installation

Install the required Python libraries using `pip`:

```sh
pip install psutil pyfiglet colorama pypiwin32
```

## Usage

### Windows

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/disk-copy-tool.git
    cd disk-copy-tool
    ```

2. Run the script:
    ```sh
    python Windows.py
    ```

### Linux

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/disk-copy-tool.git
    cd disk-copy-tool
    ```

2. Run the script:
    ```sh
    sudo python3 Linux.py
    ```

## Script Details

### Windows Version

The Windows version of the script uses the `win32com.client` library to interface with WMI (Windows Management Instrumentation) for listing physical disks and getting disk sizes. It uses the `ctypes` library to read from the physical disk.

### Linux Version

The Linux version of the script uses the `psutil` library to list physical disks and get their sizes. It reads from the physical disk by directly opening the device file.

## Sample Output

### Windows

```
 ____  _     _       ____                    _____           _ 
|  _ \(_)___| | __  / ___|___  _ __  _   _  |_   _|__   ___ | |
| | | | / __| |/ / | |   / _ \| '_ \| | | |   | |/ _ \ / _ \| |
| |_| | \__ \   <  | |__| (_) | |_) | |_| |   | | (_) | (_) | |
|____/|_|___/_|\_\  \____\___/| .__/ \__, |   |_|\___/ \___/|_|
                              |_|    |___/                     

Credit: Development by DRC Lab/ Nguyen Vu Ha +84903408066 Ha Noi, Viet Nam

Select a physical disk to copy:
1: \\.\PHYSICALDRIVE0 (Model Name)
2: \\.\PHYSICALDRIVE1 (Model Name)

Enter the number of the disk: 1

Enter the directory path to save the image file: C:\path\to\save

Progress: 25.00% | Speed: 30.50 MB/s | Sectors: 500000/2000000 | ETA: 00:00:40
Disk \\.\PHYSICALDRIVE0 copied to C:\path\to\save\Model_Name.img successfully.
```

### Linux

```
 ____  _     _       ____                    _____           _ 
|  _ \(_)___| | __  / ___|___  _ __  _   _  |_   _|__   ___ | |
| | | | / __| |/ / | |   / _ \| '_ \| | | |   | |/ _ \ / _ \| |
| |_| | \__ \   <  | |__| (_) | |_) | |_| |   | | (_) | (_) | |
|____/|_|___/_|\_\  \____\___/| .__/ \__, |   |_|\___/ \___/|_|
                              |_|    |___/                     

Credit: Development by DRC Lab/ Nguyen Vu Ha +84903408066 Ha Noi, Viet Nam

Select a physical disk to copy:
1: /dev/sda
2: /dev/nvme0n1

Enter the number of the disk: 1

Enter the directory path to save the image file: /path/to/save

Progress: 25.00% | Speed: 30.50 MB/s | Sectors: 500000/2000000 | ETA: 00:00:40
Disk /dev/sda copied to /path/to/save/sda.img successfully.
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Credits

Development by DRC Lab/ Nguyen Vu Ha +84903408066 Ha Noi, Viet Nam
