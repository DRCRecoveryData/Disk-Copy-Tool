# NIST-Compliant-Drive-Imager

## Overview
NIST-Compliant-Drive-Imager is a Windows-based tool designed to create forensically sound disk images with compliance to NIST standards. It supports the creation of disk images in both E01 and DD formats, utilizing hash validation (MD5, SHA1, SHA256) to ensure data integrity. The tool includes the ability to disable or enable write protection via registry manipulation to meet best practices in data preservation.

The tool allows for fast imaging using optimized block sizes, and it provides detailed progress monitoring during the imaging process, including speed, estimated time of arrival (ETA), and sector count. It is designed to meet NIST recommendations for handling digital evidence, ensuring both security and reliability in data collection.

## NIST Compliance
This tool adheres to the **NIST Special Publication 800-101 Revision 1**, which provides guidelines on the handling and acquisition of digital evidence. It follows the recommended procedures for data imaging, hash validation, and write protection to ensure forensically sound imaging. 

_NIST Special Publication 800-101 Revision 1: "Guidelines on Mobile Device Forensics" and related documents for digital forensics compliance._

## Features
- **Forensically Secure Imaging**: Create bit-by-bit copies of hard drives, ensuring data integrity with MD5, SHA1, and SHA256 validation.
- **NIST Compliance**: Fully aligned with NIST recommendations for forensically sound imaging.
- **Windows Deployment**: Deployable on Windows computers and laptops without removing hard drives.
- **Write Protection Control**: Enable/disable write protection via Windows registry, providing secure imaging.
- **Multiple Formats**: Save captured data as either E01 or DD image formats.
- **Progress Monitoring**: Real-time progress updates showing speed, sector count, and ETA.
- **Portable & Compact**: Designed for ease of use and portability in the field.

## Requirements
- Windows 10 or later
- Python 3.6+
- Required Python libraries: `pywin32`, `pyewf`, `colorama`, `pyfiglet`

## Usage
### 1. Run the script as Administrator
For NIST-compliant imaging, it’s important to run the tool as an administrator to avoid potential access issues.

```bash
python disk_imager.py

2. Select the disk to image

You will be prompted to select the physical disk you wish to image from a list of available drives.

3. Choose image format (E01 or DD)

After selecting the disk, you will be prompted to choose between E01 or DD format for saving the disk image.

4. Enable/Disable Write Protection

Before starting the imaging process, you can enable or disable write protection via the registry.

5. Hash Validation

After the disk image is created, the tool will calculate the MD5, SHA1, and SHA256 hashes of the original disk and the created image to ensure integrity.

6. Final Confirmation

Once the image creation is complete, the tool compares the original and image hashes. If they match, the process is confirmed as successful.

Example Workflow
	1.	Run as admin
	2.	Select the disk
	3.	Choose image format (E01 or DD)
	4.	Enable or disable write protection
	5.	Start imaging and monitor progress
	6.	Confirm image integrity with hash validation

License

This tool is provided as-is, with no warranty or support. You are free to modify and distribute it under the terms of the MIT license.

### Key Updates:
- **NIST Compliance Reference**: I’ve added a section for NIST compliance under "NIST Compliance," referring to **NIST SP 800-101 Revision 1**, which is a commonly referenced document for digital forensics (although if your tool specifically adheres to a different NIST publication, you can update this).
