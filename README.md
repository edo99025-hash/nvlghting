# Nova Lighting - GitHub APK Builder

Project web cukup satu file: `www/nova.html`.
Kalau HTML Nova memakai CSS/JS inline, tidak perlu folder CSS/JS terpisah.

## Cara pakai
1. Upload semua isi ZIP ini ke repository GitHub.
2. Pastikan file Nova berada di `www/nova.html`.
3. Push ke branch `main` atau `master`.
4. Buka tab **Actions** di GitHub.
5. Workflow **Build Nova APK** akan berjalan.
6. Setelah selesai, buka hasil run dan download artifact **Nova-Lighting-APK**.

Jika Nova punya gambar/font/file eksternal, tambahkan file tersebut ke `www/` dan sesuaikan referensinya di `nova.html`.


## Permission Android
Template ini menyiapkan:
- `INTERNET` untuk fitur online/Firebase.
- `RECORD_AUDIO` untuk fitur audio/microphone.

Tidak menambahkan:
- Location
- Camera
- Contacts
- SMS
- Phone
- Bluetooth

Permission microphone tetap akan meminta persetujuan pengguna saat runtime jika digunakan oleh aplikasi.


## Full Storage Access
The Android manifest includes `MANAGE_EXTERNAL_STORAGE` for full file access.
On supported Android versions, the user must enable **Allow access to manage all files**
for Nova in Android Settings before the app can use unrestricted storage access.


## Full-screen mode
The APK build config hides the Android status bar and navigation bar using
immersive sticky mode so `nova.html` can occupy the full screen.
