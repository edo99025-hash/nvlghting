"""
Sisipkan import + registerPlugin(NovaDownloadPlugin.class) ke MainActivity.java
yang digenerate otomatis oleh `npx cap add android`, supaya plugin native
NovaDownload (nulis file ke folder Downloads publik) bisa dipanggil dari
JavaScript lewat window.Capacitor.Plugins.NovaDownload.

Dipanggil sebagai: python3 patch_main_activity.py <path/to/MainActivity.java>
"""
import re
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 2:
        print("Usage: patch_main_activity.py <MainActivity.java path>")
        sys.exit(1)

    path = Path(sys.argv[1])
    text = path.read_text()

    # Import HARUS ditaruh di atas file (sebelum deklarasi class), tidak
    # boleh di tengah body class. Disisipkan tepat setelah baris
    # `package ...;` supaya posisinya selalu valid.
    if "import com.nova.lighting.NovaDownloadPlugin;" not in text:
        text = re.sub(
            r"(package [^\n]+\n)",
            r"\1import com.nova.lighting.NovaDownloadPlugin;\n",
            text,
            count=1,
        )
    if "import android.os.Bundle;" not in text:
        text = re.sub(
            r"(package [^\n]+\n)",
            r"\1import android.os.Bundle;\n",
            text,
            count=1,
        )

    if "registerPlugin(NovaDownloadPlugin.class)" not in text:
        has_on_create = re.search(
            r"protected void onCreate\(Bundle savedInstanceState\)\s*\{", text
        )
        if has_on_create:
            # onCreate sudah ada di file -> sisipkan pemanggilan
            # registerPlugin sebagai baris pertama di body-nya.
            text = re.sub(
                r"(protected void onCreate\(Bundle savedInstanceState\)\s*\{)",
                r"\1\n        registerPlugin(NovaDownloadPlugin.class);",
                text,
                count=1,
            )
        else:
            # MainActivity default Capacitor 7 biasanya kosong tanpa
            # override onCreate -> tambahkan method baru di dalam body class.
            new_method = (
                "\n"
                "    @Override\n"
                "    protected void onCreate(Bundle savedInstanceState) {\n"
                "        registerPlugin(NovaDownloadPlugin.class);\n"
                "        super.onCreate(savedInstanceState);\n"
                "    }\n"
            )
            text = re.sub(
                r"(public class MainActivity extends BridgeActivity\s*\{)",
                r"\1" + new_method,
                text,
                count=1,
            )

    path.write_text(text)
    print("--- MainActivity.java (setelah dipatch) ---")
    print(text)


if __name__ == "__main__":
    main()
