🔍 NIST-Compliant-Drive-Imager 🖥️

📌 Overview

NIST-Compliant-Drive-Imager is a Windows-based tool designed to create forensically sound disk images in compliance with NIST standards. It supports the creation of disk images in both E01 and DD formats and includes hash validation (MD5, SHA1, SHA256) to ensure data integrity.

✅ Write Protection: Enable/disable via Windows registry
✅ Fast Imaging: Adjustable block sizes for optimal performance
✅ Real-time Monitoring: Speed, ETA, sector count

This tool follows NIST guidelines to ensure secure and reliable forensic imaging.

🛡️ NIST Compliance

This tool is fully compliant with NIST Special Publication 800-86, which provides guidelines on handling and acquiring digital evidence. It follows best practices for:

🔹 Forensically sound data imaging
🔹 Hash validation to verify image integrity
🔹 Write protection to prevent modification of the source drive

📖 NIST Special Publication 800-86

“Guide to Integrating Forensic Techniques into Incident Response” ensures compliance with best practices in digital forensics and data integrity.

⚡ Features

🖥️ Forensically Secure Imaging – Bit-by-bit copies with MD5, SHA1, SHA256 hash validation
✅ NIST Compliance – Fully aligned with forensic best practices
🪟 Windows Deployment – No need to remove physical hard drives
🔒 Write Protection Control – Enable/disable write protection for source drive security
📂 Multiple Formats – Supports E01 (EnCase) and DD (raw disk image)
📊 Progress Monitoring – Speed, sector count, and ETA tracking
🚀 Portable & Compact – Ideal for field use

🔧 Requirements

🖥️ Windows 10+
🐍 Python 3.6+
📦 Required Python libraries:
	•	pywin32
	•	pyewf
	•	colorama
	•	pyfiglet

📥 Installation

1️⃣ Clone the repository:

git clone https://github.com/DRCRecoveryData/NIST-Compliant-Drive-Imager.git

2️⃣ Install dependencies:

pip install -r requirements.txt

🚀 Usage

1️⃣ Run as Administrator

To ensure proper access to physical disks and registry manipulation, run the tool as Administrator:

python disk-imager-tool.py

2️⃣ Select the Disk to Image

The tool will list available physical drives for selection.

3️⃣ Choose Image Format (E01 or DD)

Select the desired output format for saving the disk image.

4️⃣ Enable/Disable Write Protection

Prevent any writes to the source drive via Windows registry settings.

5️⃣ Hash Validation

After imaging, the tool will calculate:
✅ MD5
✅ SHA1
✅ SHA256
To ensure data integrity.

6️⃣ Final Confirmation

Hashes of the original disk and created image are compared to verify a successful imaging process.

📝 Example Workflow

1️⃣ Run as Admin:

python disk_imager.py

2️⃣ Select the Disk:

1: \\.\PHYSICALDRIVE0 (Samsung SSD 860 EVO)  
2: \\.\PHYSICALDRIVE1 (Seagate 1TB HDD)  

3️⃣ Choose Image Format:

Choose the output format (E01/DD): e01

4️⃣ Enable/Disable Write Protection:

Enable Write Protection? (y/n): y

5️⃣ Start Imaging & Monitor Progress:

Progress: 45.67% | Speed: 100.00 MB/s | Sectors: 100000/1000000 | ETA: 00:10:00

6️⃣ Confirm Image Integrity with Hash Validation:

MD5: <calculated MD5 hash>  
SHA1: <calculated SHA1 hash>  
SHA256: <calculated SHA256 hash>  

📜 License

⚠️ This tool is provided as-is, with no warranty or support.
📜 You are free to modify and distribute it under the MIT license.

🛠️ Developed by: Nguyen Vu Ha / DRC Lab
📧 Contact: hanaloginstruments@gmail.com