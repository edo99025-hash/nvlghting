"""
Sisipkan import + registerPlugin(...) ke MainActivity.java yang digenerate
otomatis oleh `npx cap add android`, supaya plugin native custom kita bisa
dipanggil dari JavaScript lewat window.Capacitor.Plugins.<Nama>.

Plugin yang didaftarkan:
  - NovaDownloadPlugin — nulis file ke folder Downloads publik.
  - NovaUpdaterPlugin  — hot-update konten web (index.html) tanpa APK baru,
    dipakai fitur auto-update offline (lihat NovaUpdaterPlugin.java).

Dipanggil sebagai: python3 patch_main_activity.py <path/to/MainActivity.java>
"""
import re
import sys
from pathlib import Path

PLUGINS = ["NovaDownloadPlugin", "NovaUpdaterPlugin"]


def main():
    if len(sys.argv) != 2:
        print("Usage: patch_main_activity.py <MainActivity.java path>")
        sys.exit(1)

    path = Path(sys.argv[1])
    text = path.read_text()

    # Import HARUS ditaruh di atas file (sebelum deklarasi class), tidak
    # boleh di tengah body class. Disisipkan tepat setelah baris
    # `package ...;` supaya posisinya selalu valid.
    for plugin in PLUGINS:
        import_line = "import com.nova.lighting.{};".format(plugin)
        if import_line not in text:
            text = re.sub(
                r"(package [^\n]+\n)",
                r"\1" + import_line + "\n",
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

    register_lines = "\n".join(
        "        registerPlugin({}.class);".format(p)
        for p in PLUGINS
        if "registerPlugin({}.class)".format(p) not in text
    )

    if register_lines:
        has_on_create = re.search(
            r"protected void onCreate\(Bundle savedInstanceState\)\s*\{", text
        )
        if has_on_create:
            # onCreate sudah ada di file -> sisipkan pemanggilan
            # registerPlugin sebagai baris pertama di body-nya.
            text = re.sub(
                r"(protected void onCreate\(Bundle savedInstanceState\)\s*\{)",
                r"\1\n" + register_lines,
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
                + register_lines + "\n"
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
