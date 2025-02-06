verify image integrity.
- Write protection to prevent modification of the source drive during imaging.

### NIST Special Publication 800-86:
*"Guide to Integrating Forensic Techniques into Incident Response"* and related documents serve as the foundation for digital forensics compliance, ensuring best practices in data acquisition and integrity.

## Features
- **Forensically Secure Imaging**: Create bit-by-bit copies of hard drives with MD5, SHA1, and SHA256 hash validation to ensure data integrity.
- **NIST Compliance**: Fully aligned with NIST recommendations for forensically sound imaging practices.
- **Windows Deployment**: Deployable on Windows operating systems without removing the physical hard drives.
- **Write Protection Control**: Enable or disable write protection via Windows registry to secure the source drive during imaging.
- **Multiple Formats**: Choose between **E01** (EnCase) or **DD** (raw disk image) formats for the disk image.
- **Progress Monitoring**: Real-time updates of imaging progress, including speed, sector count, and ETA.
- **Portable & Compact**: Designed for field use, offering portability and ease of use.

## Requirements
- **Windows 10** or later.
- **Python 3.6+**.
- Required Python libraries:
  - `pywin32`
  - `pyewf`
  - `colorama`
  - `pyfiglet`

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/DRCRecoveryData/NIST-Compliant-Drive-Imager.git
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### 1. Run the script as Administrator
To ensure proper access to physical disks and registry manipulation, it is necessary to run the tool as an administrator.

```bash
python disk-imager-tool.py

2. Select the disk to image

You will be prompted to select the physical disk you wish to image from a list of available drives.

3. Choose image format (E01 or DD)

After selecting the disk, you will be prompted to choose between E01 (EnCase) or DD (raw disk image) format for saving the disk image.

4. Enable/Disable Write Protection

Before starting the imaging process, you can enable or disable write protection via registry manipulation to ensure no writes occur to the source drive.

5. Hash Validation

After the disk image is created, the tool will calculate the MD5, SHA1, and SHA256 hashes of the original disk and the created image to ensure data integrity.

6. Final Confirmation

Once the image creation is complete, the tool will compare the hashes of the original disk and the created image. If they match, the process is confirmed as successful.

Example Workflow
	1.	Run as admin:

python disk_imager.py


	2.	Select the disk:

1: \\.\PHYSICALDRIVE0 (Samsung SSD 860 EVO)
2: \\.\PHYSICALDRIVE1 (Seagate 1TB HDD)


	3.	Choose image format:

Choose the output format (E01/DD): e01


	4.	Enable/Disable Write Protection:

Enable Write Protection? (y/n): y


	5.	Start imaging and monitor progress:

Progress: 45.67% | Speed: 100.00 MB/s | Sectors: 100000/1000000 | ETA: 00:10:00


	6.	Confirm image integrity with hash validation:

MD5: <calculated MD5 hash>
SHA1: <calculated SHA1 hash>
SHA256: <calculated SHA256 hash>



License

This tool is provided as-is, with no warranty or support. You are free to modify and distribute it under the terms of the MIT license.

Developed by: [Nguyen Vu Ha / DRC Lab]
Contact: [hanaloginstruments@gmail.com]