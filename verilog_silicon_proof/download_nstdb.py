import urllib.request
import os
import struct

DOWNLOAD_DIR = r"c:\Users\Lenovo\OneDrive\Documents\CardioSense\verilog_silicon_proof"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# MIT-BIH Noise Stress Test Database (NSTDB) Record 118e_6 (severe motion artifact: -6 dB SNR)
BASE_URL = "https://physionet.org/files/nstdb/1.0.0/"
FILES = ["118e_6.hea", "118e_6.dat"]

print("Downloading MIT-BIH NSTDB Record 118e_6 from PhysioNet...")
for fname in FILES:
    dest_path = os.path.join(DOWNLOAD_DIR, fname)
    if not os.path.exists(dest_path):
        url = BASE_URL + fname
        print(f"Fetching {url} -> {dest_path}")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp, open(dest_path, 'wb') as f:
            f.write(resp.read())
        print(f"Downloaded {fname} successfully ({os.path.getsize(dest_path)} bytes).")
    else:
        print(f"File {fname} already cached locally.")

print("All benchmark data files ready.")
