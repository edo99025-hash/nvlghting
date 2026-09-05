"""
Tambahkan permission yang dibutuhkan ke AndroidManifest.xml hasil generate
`npx cap add android`, dan pastikan tag <application> punya
android:requestLegacyExternalStorage="true" (dibutuhkan supaya penulisan
file ke folder Downloads publik tetap kompatibel di Android 10 / API 29).

Dipanggil sebagai: python3 patch_manifest.py <path/to/AndroidManifest.xml>
"""
import re
import sys
from pathlib import Path

PERMISSIONS = [
    '<uses-permission android:name="android.permission.INTERNET" />',
    '<uses-permission android:name="android.permission.RECORD_AUDIO" />',
    '<uses-permission android:name="android.permission.MANAGE_EXTERNAL_STORAGE" />',
    '<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" android:maxSdkVersion="32" />',
    '<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" android:maxSdkVersion="29" />',
]


def main():
    if len(sys.argv) != 2:
        print("Usage: patch_manifest.py <AndroidManifest.xml path>")
        sys.exit(1)

    manifest_path = Path(sys.argv[1])
    text = manifest_path.read_text()
    marker = "</manifest>"

    for perm in PERMISSIONS:
        if perm not in text:
            text = text.replace(marker, "    " + perm + "\n" + marker, 1)

    if "android:requestLegacyExternalStorage" not in text:
        text = re.sub(
            r"(<application\b)",
            r'\1 android:requestLegacyExternalStorage="true"',
            text,
            count=1,
        )

    manifest_path.write_text(text)


if __name__ == "__main__":
    main()
