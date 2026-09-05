"""
Naikkan versionCode & versionName di android/app/build.gradle memakai nomor
build CI (github.run_number), supaya tiap build APK baru selalu punya
versionCode LEBIH BESAR dari build sebelumnya.

Android mensyaratkan versionCode APK baru > versionCode yang sedang
terpasang sebelum menawarkan opsi "Update" (install menimpa, data user
tetap ada). github.run_number naik terus setiap kali workflow ini jalan,
jadi aman dipakai langsung sebagai versionCode.

Dipanggil sebagai: python3 bump_version.py <path/to/build.gradle> <run_number>
"""
import re
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 3:
        print("Usage: bump_version.py <build.gradle path> <run_number>")
        sys.exit(1)

    gradle_path = Path(sys.argv[1])
    run_number = sys.argv[2]

    version_code = run_number
    version_name = "1.0.{}".format(run_number)

    text = gradle_path.read_text()
    text = re.sub(r"versionCode\s+\d+", "versionCode {}".format(version_code), text, count=1)
    text = re.sub(r'versionName\s+"[^"]*"', 'versionName "{}"'.format(version_name), text, count=1)
    gradle_path.write_text(text)

    print("versionCode={} versionName={}".format(version_code, version_name))


if __name__ == "__main__":
    main()
