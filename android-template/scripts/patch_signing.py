"""
Patch android/app/build.gradle supaya build tipe "debug" selalu di-sign
pakai satu file keystore yang sudah di-commit ke repo
(android-template/app/debug.keystore), bukan keystore acak yang
di-auto-generate ulang Gradle di tiap runner CI baru.

Kenapa ini penting: Android cuma mau nawarin "Update" (install menimpa versi
lama tanpa uninstall & tanpa hilang data) kalau APK baru versionCode-nya
lebih besar DAN ditandatangani dengan signature yang SAMA PERSIS seperti APK
yang sudah terpasang. Kalau tiap build CI pakai keystore beda, signature-nya
ikut beda, dan user terpaksa uninstall dulu tiap update — makanya keystore-nya
dikunci satu dan sama untuk semua build.

Dipanggil sebagai: python3 patch_signing.py <path/to/build.gradle>
"""
import re
import sys
from pathlib import Path

def main():
    if len(sys.argv) != 2:
        print("Usage: patch_signing.py <build.gradle path>")
        sys.exit(1)

    gradle_path = Path(sys.argv[1])
    text = gradle_path.read_text()

    signing_lines = [
        "    signingConfigs {",
        "        debug {",
        "            storeFile file('debug.keystore')",
        "            storePassword 'android'",
        "            keyAlias 'androiddebugkey'",
        "            keyPassword 'android'",
        "        }",
        "    }",
        "",
    ]
    signing_block = "\n".join(signing_lines)

    if "signingConfigs" not in text:
        text = re.sub(r'(android\s*\{)', r'\1\n' + signing_block, text, count=1)

    if "signingConfig signingConfigs.debug" not in text:
        # Kalau ada block "buildTypes { debug { ... } }" eksplisit, sisipkan
        # rujukan signingConfig di dalamnya. Kalau tidak ada (Capacitor
        # default sering cuma punya block "release"), Gradle tetap otomatis
        # memakai signingConfigs.debug untuk varian debug begitu blok
        # signingConfigs.debug di atas ada — jadi tetap aman walau regex ini
        # tidak menemukan match.
        text = re.sub(
            r'(buildTypes\s*\{\s*debug\s*\{)',
            r'\1\n            signingConfig signingConfigs.debug',
            text,
            count=1,
        )

    gradle_path.write_text(text)


if __name__ == "__main__":
    main()
